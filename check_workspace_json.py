"""Validate tutorial workspaces against their exported JSON files.

This utility executes each tutorial script, captures the workspace that was
used for exporting to JSON, imports the exported JSON into a fresh workspace
and compares the content of both workspaces.  The comparison checks variables,
functions, PDFs and datasets to ensure that the JSON representation faithfully
recreates the original workspace.
"""
from __future__ import annotations

import argparse
import runpy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple

try:
    import ROOT  # type: ignore
except ImportError as exc:  # pragma: no cover - dependency injection
    raise SystemExit(
        "PyROOT is required to run this script. Ensure that ROOT is available in the environment."
    ) from exc

# Access the RooMsgService instance
msgservice = ROOT.RooMsgService.instance()

# Example: turn off INFO messages (keeps WARNING and ERROR)
msgservice.setGlobalKillBelow(ROOT.RooFit.WARNING)

# Alternatively, suppress all messages completely:
msgservice.setGlobalKillBelow(ROOT.RooFit.FATAL)

# Or more fine-grained: silence a specific source or topic
msgservice.getStream(ROOT.RooFit.INFO).removeTopic(ROOT.RooFit.ObjectHandling)
msgservice.getStream(ROOT.RooFit.DEBUG).removeTopic(ROOT.RooFit.ObjectHandling)

@dataclass
class WorkspaceSummary:
    """Collections of named objects grouped by RooFit category."""

    variables: Mapping[str, str]
    categories: Mapping[str, str]
    functions: Mapping[str, str]
    pdfs: Mapping[str, str]
    data: Mapping[str, str]
    resolutionModels: Mapping[str, str]

    def as_dict(self) -> Dict[str, Mapping[str, str]]:
        return {
            "variables": self.variables,
            "categories": self.categories,
            "functions": self.functions,
            "pdfs": self.pdfs,
            "data": self.data,
        }


def _collect_named_objects(argset: ROOT.RooAbsCollection) -> Dict[str, str]:  # type: ignore[name-defined]
    return {obj.GetName(): obj.ClassName() for obj in argset}


def _fallback_sanitize_name(name: str) -> str:
    """Reproduce the HS3 name sanitisation rules in pure Python."""

    result: List[str] = []
    for char in name:
        if char in "[|,(":
            result.append("_")
        elif char in "])":
            continue
        elif char == ".":
            result.append("_dot_")
        elif char == "@":
            result.append("at")
        elif char == "-":
            result.append("minus")
        elif char == "/":
            result.append("_div_")
        else:
            result.append(char)

    return "".join(result)


def sanitize_name(name: str) -> str:
    """Return the HS3-sanitised version of ``name``.

    The implementation delegates to ``RooJSONFactoryWSTool`` when available to
    stay in sync with ROOT, but falls back to the locally reproduced rules if
    the method is not exposed in the PyROOT bindings.
    """

    try:
        sanitized = ROOT.RooJSONFactoryWSTool.sanitizeName(name)  # type: ignore[attr-defined]
    except AttributeError:
        sanitized = _fallback_sanitize_name(name)

    return str(sanitized)


def _prepare_objects(objects: Mapping[str, str]) -> Dict[str, List[Tuple[str, str]]]:
    """Group objects by their sanitised name.

    Each entry keeps both the original display name (annotated with the
    sanitised form when it differs) and the class name.  This allows the
    comparison logic to match objects across workspaces even if their names are
    transformed by the sanitiser.
    """

    grouped: Dict[str, List[Tuple[str, str]]] = {}
    for name, class_name in objects.items():
        sanitised = sanitize_name(name)
        display_name = name if sanitised == name else f"{name} [sanitised: {sanitised}]"
        grouped.setdefault(sanitised, []).append((display_name, class_name))

    return grouped


def summarize_workspace(ws: ROOT.RooWorkspace) -> WorkspaceSummary:  # type: ignore[name-defined]
    """Return the essential objects stored in ``ws`` grouped by category."""

    return WorkspaceSummary(
        variables=_collect_named_objects(ws.allVars()),
        categories=_collect_named_objects(ws.allCats()),
        functions=_collect_named_objects(ws.allFunctions()),
        pdfs=_collect_named_objects(ws.allPdfs()),
        data=_collect_named_objects(ws.allData()),
        resolutionModels=_collect_named_objects(ws.allResolutionModels()),
    )


def compare_workspaces(expected: WorkspaceSummary, actual: WorkspaceSummary) -> Dict[str, Dict[str, Tuple[str, str]]]:
    """Compare two workspaces and report discrepancies.

    The returned mapping contains, per category, the objects that are missing,
    unexpected, or of a different type in the imported workspace.  An empty
    dictionary indicates perfect agreement.
    """

    diff: Dict[str, Dict[str, Tuple[str, str]]] = {}

    for category, expected_objects in expected.as_dict().items():
        expected_grouped = _prepare_objects(expected_objects)
        actual_grouped = _prepare_objects(actual.as_dict()[category])

        expected_keys = set(expected_grouped)
        actual_keys = set(actual_grouped)

        missing = {
            ", ".join(display for display, _ in expected_grouped[name]): (
                ", ".join(f"{display} ({cls})" for display, cls in expected_grouped[name]),
                "<missing>",
            )
            for name in expected_keys - actual_keys
        }
        unexpected = {
            ", ".join(display for display, _ in actual_grouped[name]): (
                "<unexpected>",
                ", ".join(f"{display} ({cls})" for display, cls in actual_grouped[name]),
            )
            for name in actual_keys - expected_keys
        }

        type_mismatch: Dict[str, Tuple[str, str]] = {}
        for name in expected_keys & actual_keys:
            expected_entries = expected_grouped[name]
            actual_entries = actual_grouped[name]

            expected_classes = sorted(cls for _, cls in expected_entries)
            actual_classes = sorted(cls for _, cls in actual_entries)

            if len(expected_entries) != len(actual_entries) or expected_classes != actual_classes:
                label = ", ".join(display for display, _ in expected_entries)
                expected_desc = ", ".join(
                    f"{display} ({cls})" for display, cls in expected_entries
                )
                actual_desc = ", ".join(
                    f"{display} ({cls})" for display, cls in actual_entries
                )
                type_mismatch[label] = (expected_desc, actual_desc)

        combined: Dict[str, Tuple[str, str]] = {}
        combined.update(missing)
        combined.update(unexpected)
        combined.update(type_mismatch)

        if combined:
            diff[category] = combined

    return diff


def import_workspace_from_json(json_path: Path) -> ROOT.RooWorkspace:  # type: ignore[name-defined]
    ws = ROOT.RooWorkspace("ws_from_json")
    tool = ROOT.RooJSONFactoryWSTool(ws)
    tool.importJSON(str(json_path))
    return ws


def run_tutorial(script_path: Path) -> Mapping[str, object]:
    """Execute ``script_path`` and return its globals."""

    return runpy.run_path(str(script_path), run_name="__main__")


def resolve_workspace(namespace: Mapping[str, object]) -> ROOT.RooWorkspace:  # type: ignore[name-defined]
    """Return the original workspace exposed by the tutorial script."""

    candidates = ("ws", "w", "combWS", "workspace")

    for name in candidates:
        workspace = namespace.get(name)
        if isinstance(workspace, ROOT.RooWorkspace):
            return workspace

    raise RuntimeError(
        "Tutorial script did not expose a RooWorkspace (expected one of: "
        + ", ".join(candidates)
        + ")."
    )


def resolve_export_path(namespace: Mapping[str, object], default_path: Path) -> Path:
    export_file = namespace.get("exportFile")
    if export_file is None:
        return default_path
    return Path(export_file)


def check_tutorial(script_path: Path, export_dir: Path) -> bool:
    namespace = run_tutorial(script_path)
    expected_ws = resolve_workspace(namespace)
    export_path = resolve_export_path(namespace, export_dir / f"{script_path.stem}.json")

    if not export_path.exists():
        raise FileNotFoundError(f"Exported JSON file not found: {export_path}")

    imported_ws = import_workspace_from_json(export_path)

    diff = compare_workspaces(
        summarize_workspace(expected_ws), summarize_workspace(imported_ws)
    )

    if diff:
        print(f"\n❌ {script_path.name}: mismatches detected")
        for category, objects in diff.items():
            print(f"  {category}:")
            for name, (expected, actual) in sorted(objects.items()):
                print(f"    - {name}: expected {expected}, found {actual}")
        return False

    print(f"\n✅ {script_path.name}: workspace matches exported JSON")
    return True


def discover_scripts(tutorial_dir: Path) -> Iterable[Path]:
    return sorted(path for path in tutorial_dir.glob("*.py") if path.is_file())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that tutorial workspaces match their exported JSON files."
    )
    parser.add_argument(
        "tutorial_dir",
        nargs="?",
        default=Path("tutorials"),
        type=Path,
        help="Directory containing the tutorial scripts (default: tutorials)",
    )
    parser.add_argument(
        "--export-dir",
        default=Path("exportedJSON"),
        type=Path,
        help="Directory containing the exported JSON files (default: exportedJSON)",
    )
    parser.add_argument(
        "scripts",
        nargs="*",
        help="Optional subset of tutorial script names to verify (e.g. rf101_basics.py)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tutorial_dir = args.tutorial_dir.resolve()
    export_dir = args.export_dir.resolve()

    if args.scripts:
        scripts = [tutorial_dir / name for name in args.scripts]
    else:
        scripts = list(discover_scripts(tutorial_dir))

    if not scripts:
        print(f"No tutorial scripts found in {tutorial_dir}")
        return 0

    all_ok = True
    for script in scripts:
        try:
            result = check_tutorial(script, export_dir)
        except Exception as exc:  # pragma: no cover - used for CLI resilience
            all_ok = False
            print(f"\n❌ {script.name}: {exc}")
        else:
            all_ok = all_ok and result

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
