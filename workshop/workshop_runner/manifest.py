"""Manifest loading for workshop chapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

LEGACY_BASE_PROFILES = {"core", "query"}


@dataclass(frozen=True)
class ChapterManifest:
    """Loaded chapter manifest."""

    title: str
    act: int | None
    slug: str
    directory: Path
    commands: tuple[str, ...]
    profiles: tuple[str, ...]
    services: tuple[str, ...]
    bootstrap_chapters: tuple[str, ...]
    has_solution: bool


def discover_chapters(chapters_dir: Path) -> list[ChapterManifest]:
    """Read all chapter manifests."""
    chapters: list[ChapterManifest] = []
    for chapter_dir in sorted(chapters_dir.iterdir()):
        manifest_path = chapter_dir / "chapter.yaml"
        if not manifest_path.exists():
            continue
        with manifest_path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        chapters.append(
            ChapterManifest(
                title=data["title"],
                act=data.get("act"),
                slug=chapter_dir.name,
                directory=chapter_dir,
                commands=tuple(data.get("commands", [])),
                profiles=tuple(data.get("profiles", [])),
                services=tuple(data.get("services", [])),
                bootstrap_chapters=tuple(data.get("bootstrap_chapters", [])),
                has_solution=(chapter_dir / "solution").is_dir(),
            )
        )
    return chapters


def filter_chapters(
    chapters: list[ChapterManifest],
    *,
    act: int | None = None,
    chapter: str | None = None,
) -> list[ChapterManifest]:
    """Filter loaded chapters."""
    if chapter:
        return [item for item in chapters if item.slug == chapter]
    if act:
        return [item for item in chapters if item.act == act]
    return chapters


def normalized_profiles(chapters: list[ChapterManifest]) -> tuple[str, ...]:
    """Return unique optional profiles across selected chapters."""
    profiles: list[str] = []
    for chapter in chapters:
        for profile in chapter.profiles:
            if profile in LEGACY_BASE_PROFILES:
                continue
            if profile not in profiles:
                profiles.append(profile)
    return tuple(profiles)
