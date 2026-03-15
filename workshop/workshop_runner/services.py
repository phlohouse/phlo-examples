"""Service orchestration for workshop validation."""

from __future__ import annotations

import subprocess
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import yaml
from phlo.cli.commands.services.utils import get_profile_service_names
from phlo.cli.infrastructure.utils import get_project_name
from phlo_trino.resource import TrinoResource
from rich.console import Console

CORE_SERVICE_STARTUP_SECONDS = 45
PROFILE_SERVICE_STARTUP_SECONDS = 45
PROFILE_START_TIMEOUT_SECONDS = 300
PROFILE_START_TIMEOUT_OVERRIDES = {
    "openmetadata": 900,
}
CORE_HTTP_READINESS_CHECKS = (
    ("Nessie", "http://localhost:19120/api/v1/config"),
    ("MinIO", "http://localhost:9000/minio/health/live"),
)
PROFILE_SERVICE_MARKERS = {
    "observability": ("clickstack", "grafana", "prometheus", "loki", "alloy"),
    "openmetadata": ("openmetadata", "openmetadata-elasticsearch", "openmetadata-mysql"),
    "api": ("phlo-api", "hasura", "postgrest"),
    "proxy": ("traefik",),
}


@dataclass
class ServiceManager:
    """Track and orchestrate workshop services."""

    workshop_dir: Path
    console: Console
    requested_profiles: tuple[str, ...]
    initialized: bool = False
    core_started: bool = False
    started_profiles: set[str] = field(default_factory=set)
    started_services: set[str] = field(default_factory=set)

    def detect_existing_runtime(self) -> None:
        """Mark the current manager as initialized when the compose project is already up."""
        compose_file = self.workshop_dir / ".phlo" / "docker-compose.yml"
        if not compose_file.exists():
            return

        project_name = get_project_name()
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--format",
                    "{{.Names}}",
                    "--filter",
                    f"label=com.docker.compose.project={project_name}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workshop_dir),
            )
        except subprocess.SubprocessError:
            return

        if result.returncode != 0:
            return

        running_names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        if not running_names:
            return

        self.initialized = True
        self.core_started = True
        self.started_services.update(
            name.removeprefix(f"{project_name}-").rsplit("-", 1)[0] for name in running_names
        )
        for profile, markers in PROFILE_SERVICE_MARKERS.items():
            if any(any(marker in name for marker in markers) for name in running_names):
                self.started_profiles.add(profile)

    def setup(self, *, profiles: tuple[str, ...], services: tuple[str, ...]) -> None:
        """Ensure requested chapter services are running."""
        requested_profiles = " ".join(
            f"--profile {profile}" for profile in self.requested_profiles
        )
        if not self.initialized:
            self.console.print("  [dim]initializing services (phlo services init --dev --force)...[/dim]")
            self._run(
                f"phlo services init --dev --force {requested_profiles}".strip(),
                timeout=300,
                error_message="services init failed",
            )
            self.initialized = True
        else:
            self._ensure_rendered(profiles=profiles, services=services)

        if not self.core_started:
            self.console.print("  [dim]starting base services...[/dim]")
            self._run(
                "phlo services start --build",
                timeout=300,
                error_message="base service startup failed",
            )
            self.core_started = True
            self._sleep(CORE_SERVICE_STARTUP_SECONDS, reason="base services")
            self._wait_for_core_readiness()

        for profile in [item for item in profiles if item not in self.started_profiles]:
            self.console.print(f"  [dim]starting profile: {profile}[/dim]")
            timeout_seconds = PROFILE_START_TIMEOUT_OVERRIDES.get(
                profile, PROFILE_START_TIMEOUT_SECONDS
            )
            try:
                self._run(
                    f"phlo services start --build --profile {profile}",
                    timeout=timeout_seconds,
                    error_message=f"profile {profile} failed",
                )
            except subprocess.TimeoutExpired:
                self.console.print(f"  [yellow]⚠ profile {profile}: start timed out[/yellow]")
            self.started_profiles.add(profile)
            self._sleep(PROFILE_SERVICE_STARTUP_SECONDS, reason=f"profile {profile}")
            self._wait_for_profile_readiness(profile)
            self._wait_for_core_readiness()

        for service in [item for item in services if item not in self.started_services]:
            self.console.print(f"  [dim]starting service: {service}[/dim]")
            self._run(
                f"phlo services start --build --service {service}",
                timeout=300,
                error_message=f"service {service} failed",
            )
            self.started_services.add(service)
            self._sleep(PROFILE_SERVICE_STARTUP_SECONDS, reason=f"service {service}")
            self._wait_for_service_readiness(service)
            self._wait_for_core_readiness()

    def _ensure_rendered(self, *, profiles: tuple[str, ...], services: tuple[str, ...]) -> None:
        """Ensure later chapter profiles/services exist in the rendered compose file."""
        compose_services = self._rendered_service_names()
        missing_profiles = tuple(
            profile
            for profile in profiles
            if profile not in self.started_profiles
            or any(name not in compose_services for name in get_profile_service_names((profile,)))
        )
        missing_services = tuple(
            service
            for service in services
            if service not in self.started_services or service not in compose_services
        )

        if not missing_profiles and not missing_services:
            return

        parts: list[str] = ["phlo services add", "--no-start"]
        for profile in missing_profiles:
            parts.extend(["--profile", profile])
        for service in missing_services:
            parts.extend(["--service", service])

        self.console.print("  [dim]rendering late chapter services into compose...[/dim]")
        self._run(
            " ".join(parts),
            timeout=300,
            error_message="services add failed",
        )

    def _rendered_service_names(self) -> set[str]:
        """Return service names currently rendered into .phlo/docker-compose.yml."""
        compose_file = self.workshop_dir / ".phlo" / "docker-compose.yml"
        if not compose_file.exists():
            return set()
        try:
            data = yaml.safe_load(compose_file.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            return set()
        services = data.get("services", {})
        if not isinstance(services, dict):
            return set()
        return {str(name) for name in services}

    def ensure_runtime_ready(self, *, profiles: tuple[str, ...]) -> None:
        """Re-check service readiness before retrying chapter commands."""
        self._wait_for_core_readiness()
        for profile in profiles:
            if profile in self.started_profiles:
                self._wait_for_profile_readiness(profile)

    def teardown(self) -> None:
        """Remove running workshop containers and volumes."""
        self.console.print("  [dim]stopping services...[/dim]")
        project_name = get_project_name()
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-aq",
                    "--filter",
                    f"label=com.docker.compose.project={project_name}",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.workshop_dir),
            )
        except subprocess.SubprocessError:
            result = None

        container_ids: list[str] = []
        if result and result.returncode == 0:
            container_ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if container_ids:
            subprocess.run(
                ["docker", "rm", "-f", *container_ids],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=str(self.workshop_dir),
            )

        compose_file = self.workshop_dir / ".phlo" / "docker-compose.yml"
        if compose_file.exists():
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "-p",
                    project_name,
                    "-f",
                    str(compose_file),
                    "down",
                    "--volumes",
                    "--remove-orphans",
                    "--timeout",
                    "30",
                ],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=str(self.workshop_dir),
            )

        try:
            volume_result = subprocess.run(
                [
                    "docker",
                    "volume",
                    "ls",
                    "-q",
                    "--filter",
                    f"label=com.docker.compose.project={project_name}",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.workshop_dir),
            )
        except subprocess.SubprocessError:
            volume_result = None

        if volume_result and volume_result.returncode == 0:
            volume_names = [line.strip() for line in volume_result.stdout.splitlines() if line.strip()]
            if volume_names:
                subprocess.run(
                    ["docker", "volume", "rm", "-f", *volume_names],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=str(self.workshop_dir),
                )

        self._clear_local_state()

    def _run(self, command: str, *, timeout: int, error_message: str) -> None:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(self.workshop_dir),
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or error_message)

    def _sleep(self, seconds: int, *, reason: str) -> None:
        if seconds <= 0:
            return
        self.console.print(f"  [dim]waiting {seconds}s for {reason}...[/dim]")
        time.sleep(seconds)

    def _wait_for_profile_readiness(self, profile: str) -> None:
        if profile == "openmetadata":
            self.console.print("  [dim]waiting for OpenMetadata API readiness...[/dim]")
            deadline = time.monotonic() + 600
            last_error = "timed out"
            while time.monotonic() < deadline:
                try:
                    response = httpx.get(
                        "http://localhost:8585/api/v1/system/version",
                        timeout=10,
                        follow_redirects=True,
                    )
                    if response.status_code == 200:
                        return
                    last_error = f"status {response.status_code}"
                except Exception as exc:
                    last_error = str(exc)
                time.sleep(5)
            raise RuntimeError(f"OpenMetadata did not become ready: {last_error}")

        if profile == "proxy":
            self.console.print("  [dim]waiting for proxy readiness...[/dim]")
            deadline = time.monotonic() + 180
            last_error = "timed out"
            while time.monotonic() < deadline:
                try:
                    response = httpx.get(
                        "http://localhost",
                        headers={"Host": "traefik.phlo.localhost"},
                        timeout=5,
                        follow_redirects=True,
                    )
                    if response.status_code < 500:
                        return
                    last_error = f"status {response.status_code}"
                except Exception as exc:
                    last_error = str(exc)
                time.sleep(3)
            raise RuntimeError(f"Proxy did not become ready: {last_error}")

    def _wait_for_core_readiness(self) -> None:
        """Wait for core HTTP services used by workshop commands."""
        self.console.print("  [dim]waiting for core service readiness...[/dim]")
        deadline = time.monotonic() + 180
        last_errors: dict[str, str] = {}
        try:
            TrinoResource(host="localhost").wait_ready(timeout=45.0, interval=1.0)
        except Exception as exc:
            last_errors["Trino"] = str(exc)

        pending = {name: url for name, url in CORE_HTTP_READINESS_CHECKS}
        while time.monotonic() < deadline and pending:
            for name, url in list(pending.items()):
                try:
                    response = httpx.get(url, timeout=5, follow_redirects=True)
                    if response.status_code < 500:
                        pending.pop(name, None)
                        continue
                    last_errors[name] = f"status {response.status_code}"
                except Exception as exc:
                    last_errors[name] = str(exc)
            if pending:
                time.sleep(3)
        if "Trino" in last_errors or pending:
            names = ["Trino", *pending]
            details = ", ".join(
                f"{name}: {last_errors.get(name, 'timed out')}"
                for index, name in enumerate(names)
                if name not in names[:index]
            )
            raise RuntimeError(f"Core services did not become ready: {details}")

    def _wait_for_service_readiness(self, service: str) -> None:
        """Wait for service-specific readiness when chapter checks depend on it."""
        if service != "superset":
            return

        self.console.print("  [dim]waiting for Superset readiness...[/dim]")
        deadline = time.monotonic() + 300
        last_error = "timed out"
        while time.monotonic() < deadline:
            try:
                response = httpx.get(
                    "http://localhost:8088/health",
                    timeout=10,
                    follow_redirects=True,
                )
                if response.status_code == 200:
                    if "proxy" not in self.started_profiles:
                        return
                    named = httpx.get(
                        "http://localhost",
                        headers={"Host": "superset.phlo.localhost"},
                        timeout=5,
                        follow_redirects=True,
                    )
                    if named.status_code == 200:
                        return
                    last_error = f"named-url status {named.status_code}"
                else:
                    last_error = f"status {response.status_code}"
            except Exception as exc:
                last_error = str(exc)
            time.sleep(5)
        raise RuntimeError(f"Superset did not become ready: {last_error}")

    def _clear_local_state(self) -> None:
        """Remove bind-mounted local service state for deterministic reruns."""
        state_paths = [
            self.workshop_dir / ".phlo" / "volumes",
            self.workshop_dir / ".phlo" / "dagster" / "storage",
            self.workshop_dir / ".phlo" / "dagster" / "logs",
            self.workshop_dir / ".phlo" / "logs",
        ]
        for path in state_paths:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
                path.mkdir(parents=True, exist_ok=True)
