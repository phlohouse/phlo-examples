"""Workshop execution flow."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from workshop_runner.manifest import ChapterManifest
from workshop_runner.services import ServiceManager


@dataclass(frozen=True)
class ChapterResult:
    """Result for one chapter run."""

    slug: str
    title: str
    passed: bool
    duration_seconds: float


class WorkshopRunner:
    """Declarative runner for workshop chapters."""

    def __init__(self, workshop_dir: Path, *, console: Console, requested_profiles: tuple[str, ...]):
        self.workshop_dir = workshop_dir
        self.console = console
        self.services = ServiceManager(
            workshop_dir=workshop_dir,
            console=console,
            requested_profiles=requested_profiles,
        )

    def prepare_environment(self) -> None:
        """Install all optional workshop dependencies before validation."""
        self.console.print("  [dim]syncing workshop environment (uv sync --all-extras)...[/dim]")
        result = subprocess.run(
            "uv sync --all-extras",
            shell=True,
            capture_output=True,
            text=True,
            timeout=900,
            cwd=str(self.workshop_dir),
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "uv sync failed"
            raise RuntimeError(message)

    def bootstrap_prerequisites(self, chapters: list[ChapterManifest]) -> None:
        """Copy solution files from prerequisite chapters into the workspace."""
        copied_files: set[Path] = set()
        for chapter in chapters:
            copied_files.update(self.copy_solution_files(chapter, quiet=True))
        if Path("pyproject.toml") in copied_files:
            self.sync_project_install()

    def bootstrap_chapters(self, chapters: list[ChapterManifest]) -> None:
        """Materialize prerequisite chapter state without running their checks."""
        if not chapters:
            return
        self.console.print("  [dim]bootstrapping prerequisite chapter commands...[/dim]")
        for chapter in chapters:
            self.console.print(f"  [dim]bootstrap {chapter.slug}: {chapter.title}[/dim]")
            self.services.setup(profiles=chapter.profiles, services=chapter.services)
            copied_files = self.copy_solution_files(chapter, quiet=True)
            if Path("pyproject.toml") in copied_files:
                self.sync_project_install()
            commands_ok, outputs = self.run_commands(chapter)
            if not commands_ok:
                self.console.print("  [yellow]retrying bootstrap commands after a short wait...[/yellow]")
                time.sleep(5)
                commands_ok, outputs = self.run_commands(chapter)
            for line in outputs:
                self.console.print(f"    {line[:300]}..." if len(line) > 300 else f"    {line}")
            if not commands_ok:
                raise RuntimeError(f"bootstrap commands failed for {chapter.slug}")

    def run_chapter(self, chapter: ChapterManifest, *, skip_setup: bool = False) -> ChapterResult:
        """Run setup, commands, and check for a chapter."""
        self.console.rule(f"[bold]{chapter.slug}: {chapter.title}[/bold]")
        started = time.monotonic()

        if not skip_setup:
            self.services.setup(profiles=chapter.profiles, services=chapter.services)

        copied_files = self.copy_solution_files(chapter)
        if Path("pyproject.toml") in copied_files:
            self.sync_project_install()

        self.services.ensure_runtime_ready(profiles=chapter.profiles)
        commands_ok, outputs = self.run_commands(chapter)
        if not commands_ok:
            self.console.print("  [yellow]retrying chapter commands after refreshing service readiness...[/yellow]")
            time.sleep(5)
            self.services.ensure_runtime_ready(profiles=chapter.profiles)
            commands_ok, retry_outputs = self.run_commands(chapter)
            outputs.extend(retry_outputs)
        for line in outputs:
            self.console.print(f"    {line[:300]}..." if len(line) > 300 else f"    {line}")
        if not commands_ok:
            if chapter.has_solution:
                self.console.print("  [red]✗ commands failed[/red]")
                return ChapterResult(chapter.slug, chapter.title, False, time.monotonic() - started)
            self.console.print(
                "  [yellow]⚠ commands failed (exploration-only, checking anyway)[/yellow]"
            )

        check_ok, check_output = self.run_check(chapter)
        if check_output and check_output != "no check.py":
            for line in check_output.split("\n"):
                self.console.print(f"    {line}")
        if not check_ok:
            self.console.print("  [red]✗ check failed[/red]")
            return ChapterResult(chapter.slug, chapter.title, False, time.monotonic() - started)

        elapsed = time.monotonic() - started
        self.console.print(f"  [green]✓ passed[/green] ({elapsed:.0f}s)")
        return ChapterResult(chapter.slug, chapter.title, True, elapsed)

    def copy_solution_files(self, chapter: ChapterManifest, *, quiet: bool = False) -> set[Path]:
        """Copy chapter solution files into the workspace."""
        solution_dir = chapter.directory / "solution"
        if not solution_dir.exists():
            return set()
        copied: set[Path] = set()
        for src in solution_dir.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(solution_dir)
            dest = self.workshop_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
            copied.add(rel)
            if not quiet:
                self.console.print(f"  [dim]copied {rel}[/dim]")
        return copied

    def sync_project_install(self) -> None:
        """Refresh editable install after project metadata changes."""
        self.console.print("  [dim]refreshing project install (uv sync --all-extras)...[/dim]")
        result = subprocess.run(
            "uv sync --all-extras",
            shell=True,
            capture_output=True,
            text=True,
            timeout=900,
            cwd=str(self.workshop_dir),
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "uv sync failed"
            raise RuntimeError(message)

    def run_commands(self, chapter: ChapterManifest) -> tuple[bool, list[str]]:
        """Run chapter shell commands."""
        outputs: list[str] = []
        for command in chapter.commands:
            self.console.print(f"  [dim]$ {command}[/dim]")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=str(self.workshop_dir),
                )
            except subprocess.TimeoutExpired:
                outputs.append(f"[timeout] {command}")
                return False, outputs
            if result.stdout:
                outputs.append(result.stdout.rstrip())
            if result.returncode != 0:
                if result.stderr:
                    outputs.append(result.stderr.rstrip())
                return False, outputs
        return True, outputs

    def run_check(self, chapter: ChapterManifest) -> tuple[bool, str]:
        """Run the chapter checkpoint script."""
        check_script = chapter.directory / "check.py"
        if not check_script.exists():
            return True, "no check.py"
        try:
            result = subprocess.run(
                [sys.executable, str(check_script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.workshop_dir),
            )
        except subprocess.TimeoutExpired:
            return False, "check.py timed out"
        output = (result.stdout + result.stderr).rstrip()
        return result.returncode == 0, output


def print_summary(console: Console, results: list[ChapterResult]) -> None:
    """Print result table."""
    table = Table(title="Workshop Validation Summary")
    table.add_column("Chapter", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Result", justify="center")
    table.add_column("Time", justify="right", style="dim")

    for result in results:
        status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
        table.add_row(result.slug, result.title, status, f"{result.duration_seconds:.0f}s")

    console.print()
    console.print(table)
    console.print(
        f"\n[bold]{sum(1 for item in results if item.passed)}/{len(results)} chapters passed "
        f"({sum(item.duration_seconds for item in results):.0f}s)[/bold]"
    )
