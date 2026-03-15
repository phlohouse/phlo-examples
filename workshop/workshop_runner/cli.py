"""CLI entrypoint for the standalone workshop runner."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from workshop_runner.manifest import discover_chapters, filter_chapters, normalized_profiles
from workshop_runner.runner import ChapterResult, WorkshopRunner, print_summary

WORKSHOP_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = WORKSHOP_DIR / "chapters"


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(description="Run workshop chapters declaratively")
    parser.add_argument("--act", type=int, choices=[0, 1, 2, 3, 4], help="Run only this act")
    parser.add_argument("--chapter", type=str, help="Run only this chapter (directory name)")
    parser.add_argument("--no-setup", action="store_true", help="Skip service setup")
    parser.add_argument("--clean", action="store_true", help="Reset services before the run")
    parser.add_argument("--sync", action="store_true", help="Refresh the workshop environment first")
    parser.add_argument("--teardown", action="store_true", help="Tear down services after run")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run selected workshop chapters."""
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()

    all_chapters = discover_chapters(CHAPTERS_DIR)
    chapters = filter_chapters(
        all_chapters,
        act=args.act,
        chapter=args.chapter,
    )
    if not chapters:
        console.print("[red]No chapters matched filters[/red]")
        return 1

    runner = WorkshopRunner(
        WORKSHOP_DIR,
        console=console,
        requested_profiles=normalized_profiles(chapters),
    )

    if args.sync:
        try:
            runner.prepare_environment()
        except RuntimeError as exc:
            console.print(f"[red]Environment preparation failed:[/red] {exc}")
            return 1

    if args.no_setup:
        console.print("  [dim]reusing existing services (--no-setup)[/dim]")
    elif args.clean or any(chapter.slug == "00-workshop-warmup" for chapter in chapters):
        console.print("  [dim]resetting services for a clean validation run...[/dim]")
        runner.services.teardown()
    else:
        console.print("  [dim]running additively; existing services/state are preserved[/dim]")
        runner.services.detect_existing_runtime()

    first_selected_index = min(all_chapters.index(chapter) for chapter in chapters)
    prerequisite_chapters = all_chapters[:first_selected_index]
    if prerequisite_chapters:
        console.print("  [dim]bootstrapping prerequisite chapter solutions...[/dim]")
        runner.bootstrap_prerequisites(prerequisite_chapters)

    bootstrap_slugs: list[str] = []
    for chapter in chapters:
        for slug in chapter.bootstrap_chapters:
            if slug not in bootstrap_slugs:
                bootstrap_slugs.append(slug)
    if bootstrap_slugs:
        bootstrap_lookup = {chapter.slug: chapter for chapter in all_chapters}
        try:
            runner.bootstrap_chapters([bootstrap_lookup[slug] for slug in bootstrap_slugs])
        except KeyError as exc:
            console.print(f"[red]Unknown bootstrap chapter:[/red] {exc.args[0]}")
            return 1
        except RuntimeError as exc:
            console.print(f"[red]Bootstrap failed:[/red] {exc}")
            return 1

    console.print(f"[bold]Running {len(chapters)} chapter(s)...[/bold]\n")
    results: list[ChapterResult] = []
    for chapter in chapters:
        results.append(runner.run_chapter(chapter, skip_setup=args.no_setup))

    if args.teardown:
        console.rule("[bold]Teardown[/bold]")
        runner.services.teardown()

    print_summary(console, results)
    return 0 if all(item.passed for item in results) else 1
