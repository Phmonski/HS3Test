"""Run all tutorial scripts sequentially.

This script discovers every Python file in the ``tutorials`` directory and
executes them one at a time using the current Python interpreter. If any
script exits with a non-zero status code, execution stops and the failure is
reported.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


def discover_tutorials(tutorial_dir: Path) -> List[Path]:
    """Return a sorted list of tutorial scripts within ``tutorial_dir``.

    Only ``.py`` files are included. The returned list is sorted to provide
    predictable execution order.
    """
    return sorted(path for path in tutorial_dir.glob("*.py") if path.is_file())


def run_scripts(scripts: Iterable[Path]) -> None:
    """Run each script sequentially.

    Each script is executed with the same Python interpreter running this
    wrapper. If a script exits with a non-zero status code, the function
    raises ``subprocess.CalledProcessError`` to allow the caller to surface
    the failure.
    """
    for script in scripts:
        print(f"\n=== Running {script} ===")
        subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all tutorial scripts.")
    parser.add_argument(
        "tutorial_dir",
        nargs="?",
        default=Path("tutorials"),
        type=Path,
        help="Directory containing tutorial scripts (default: tutorials)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tutorial_dir = args.tutorial_dir.resolve()

    if not tutorial_dir.is_dir():
        print(f"Tutorial directory not found: {tutorial_dir}", file=sys.stderr)
        return 1

    scripts = discover_tutorials(tutorial_dir)
    if not scripts:
        print(f"No tutorial scripts found in {tutorial_dir}")
        return 0

    try:
        run_scripts(scripts)
    except subprocess.CalledProcessError as exc:
        print(f"Script failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        return exc.returncode or 1

    print("\nAll tutorial scripts completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
