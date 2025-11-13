"""Round-trip exported HS3 JSON workspaces and compare against the originals."""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Sequence, Tuple

try:
    import ROOT  # type: ignore
except ImportError as exc:
    raise SystemExit(
        "PyROOT is required to run this script. Ensure that ROOT is available in the environment."
    ) from exc


def configure_roofit_logging() -> None:
    msgservice = ROOT.RooMsgService.instance()
    msgservice.setGlobalKillBelow(ROOT.RooFit.WARNING)
    msgservice.getStream(ROOT.RooFit.INFO).removeTopic(ROOT.RooFit.ObjectHandling)
    msgservice.getStream(ROOT.RooFit.DEBUG).removeTopic(ROOT.RooFit.ObjectHandling)


def locate_json_files(paths: Sequence[Path]) -> List[Path]:
    json_files: List[Path] = []
    for path in paths:
        if path.is_dir():
            json_files.extend(sorted(p for p in path.glob("*.json") if p.is_file()))
        elif path.suffix == ".json" and path.is_file():
            json_files.append(path)
    return json_files


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _sort_key_for_dict(item: Mapping[str, Any]) -> Tuple[str, str]:
    name = item.get("name")
    if isinstance(name, str):
        return ("name", name)
    identifier = item.get("id")
    if isinstance(identifier, str):
        return ("id", identifier)
    type_ = item.get("type")
    if isinstance(type_, str):
        return ("type", type_)
    serialized = json.dumps(item, sort_keys=True, separators=(",", ":"))
    return ("json", serialized)


def canonicalize(obj: object) -> object:
    if isinstance(obj, dict):
        return {key: canonicalize(obj[key]) for key in sorted(obj)}
    if isinstance(obj, list):
        if not obj:
            return []
        if all(isinstance(item, dict) for item in obj):
            canonicalized_items = [canonicalize(item) for item in obj]
            canonicalized_items.sort(key=_sort_key_for_dict)
            return canonicalized_items
        return [canonicalize(item) for item in obj]
    return obj


IGNORED_PATHS = (
    re.compile(r"\$\.data\[\d+\]\.axes\[\d+\]\.value"),
    re.compile(r"\$\.metadata(?:\..*)?"),
)


def should_ignore(path: str) -> bool:
    return any(pattern.fullmatch(path) for pattern in IGNORED_PATHS)


def find_difference(expected: object, actual: object, path: str = "$") -> str | None:
    if should_ignore(path):
        return None
    if type(expected) != type(actual):
        return f"{path}: type mismatch ({type(expected).__name__} vs {type(actual).__name__})"

    if isinstance(expected, dict):
        expected_keys = set(expected)
        actual_keys = set(actual)

        missing = expected_keys - actual_keys
        if missing:
            key = next(iter(sorted(missing)))
            return f"{path}: missing key {key!r}"

        unexpected = actual_keys - expected_keys
        if unexpected:
            key = next(iter(sorted(unexpected)))
            return f"{path}: unexpected key {key!r}"

        for key in sorted(expected_keys):
            nested_path = f"{path}.{key}"
            diff = find_difference(expected[key], actual[key], nested_path)
            if diff:
                return diff
        return None

    if isinstance(expected, list):
        if len(expected) != len(actual):
            return f"{path}: list length differs ({len(expected)} vs {len(actual)})"

        for index, (exp_item, act_item) in enumerate(zip(expected, actual)):
            nested_path = f"{path}[{index}]"
            diff = find_difference(exp_item, act_item, nested_path)
            if diff:
                return diff
        return None

    if expected != actual:
        return f"{path}: value differs ({expected!r} vs {actual!r})"

    return None


def round_trip(json_path: Path) -> Tuple[bool, str | None]:
    workspace = ROOT.RooWorkspace(f"ws_{json_path.stem}")
    tool = ROOT.RooJSONFactoryWSTool(workspace)
    tool.importJSON(str(json_path))
    
    temp_path = Path("tmpdir") / json_path.name
    tool.exportJSON(str(temp_path))
    original = canonicalize(load_json(json_path))
    regenerated = canonicalize(load_json(temp_path))
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / json_path.name
        tool.exportJSON(str(temp_path))

        original = canonicalize(load_json(json_path))
        regenerated = canonicalize(load_json(temp_path))
    """
    diff = find_difference(original, regenerated)
    return diff is None, diff


def iter_input_paths(args: argparse.Namespace) -> Iterator[Path]:
    if args.paths:
        yield from args.paths
    else:
        yield Path("exportedJSON")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-import HS3 JSON workspaces and verify a round-trip export."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="JSON files or directories to verify (default: exportedJSON).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_roofit_logging()

    json_paths = locate_json_files(list(iter_input_paths(args)))
    if not json_paths:
        print("No JSON files found to process.")
        return 0

    ok = True
    for json_path in json_paths:
        try:
            matches, diff = round_trip(json_path)
        except Exception as exc:
            ok = False
            print(f"❌ {json_path}: {exc}")
            continue

        if matches:
            print(f"✅ {json_path}")
        else:
            ok = False
            detail = f" ({diff})" if diff else ""
            print(f"❌ {json_path}{detail}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
