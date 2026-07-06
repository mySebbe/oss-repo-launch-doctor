from __future__ import annotations

import argparse
import json
import tomllib
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from ._version import __version__


@dataclass(frozen=True)
class CheckResult:
    name: str
    present: bool
    detail: str
    weight: int
    suggestion: str


@dataclass(frozen=True)
class DoctorReport:
    path: str
    score: int
    checks: dict[str, CheckResult]
    optional_checks: dict[str, CheckResult]
    suggestions: list[str]
    metadata: dict[str, str]


def _first_existing(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        match = root / name
        if match.exists():
            return match
    return None


def _first_glob(root: Path, patterns: Iterable[str]) -> Path | None:
    for pattern in patterns:
        for match in root.glob(pattern):
            if match.is_file():
                return match
    return None


def _check(name: str, found: Path | None, weight: int, suggestion: str) -> CheckResult:
    return CheckResult(
        name=name,
        present=found is not None,
        detail=str(found) if found is not None else "missing",
        weight=weight,
        suggestion=suggestion,
    )


def _read_project_metadata(root: Path) -> dict[str, str]:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return {}
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError):
        return {}
    project = data.get("project", {})
    metadata: dict[str, str] = {}
    for key in ("name", "version", "description"):
        value = project.get(key)
        if isinstance(value, str):
            metadata[f"project_{key}" if key == "name" else key] = value
    return metadata


def analyze_repository(path: str | Path) -> DoctorReport:
    root = Path(path).resolve()
    checks = {
        "readme": _check(
            "README",
            _first_glob(root, ["README", "README.*", "readme.*"]),
            15,
            "Add a README with purpose, install steps, usage, and support status.",
        ),
        "license": _check(
            "License",
            _first_existing(root, ["LICENSE", "LICENSE.md", "COPYING", "COPYING.md"]),
            15,
            "Add a license file so users know how the project can be used.",
        ),
        "contributing": _check(
            "Contributing guide",
            _first_existing(root, ["CONTRIBUTING.md", "CONTRIBUTING.rst", ".github/CONTRIBUTING.md"]),
            10,
            "Add CONTRIBUTING.md with setup, test, and pull request guidance.",
        ),
        "security": _check(
            "Security policy",
            _first_existing(root, ["SECURITY.md", ".github/SECURITY.md"]),
            10,
            "Add SECURITY.md with vulnerability reporting instructions.",
        ),
        "ci_workflow": _check(
            "CI workflow",
            _first_glob(root, [".github/workflows/*.yml", ".github/workflows/*.yaml"]),
            15,
            "Add a GitHub Actions workflow that runs the test suite.",
        ),
        "issue_templates": _check(
            "Issue templates",
            _first_glob(root, [".github/ISSUE_TEMPLATE/*.md", ".github/ISSUE_TEMPLATE/*.yml", ".github/ISSUE_TEMPLATE/*.yaml"]),
            10,
            "Add issue templates for bugs and feature requests.",
        ),
        "pyproject": _check(
            "pyproject.toml",
            root / "pyproject.toml" if (root / "pyproject.toml").is_file() else None,
            15,
            "Add pyproject.toml with build-system and project metadata.",
        ),
        "package_metadata": _check(
            "Package metadata",
            root / "pyproject.toml" if _read_project_metadata(root).get("project_name") else None,
            10,
            "Add a [project] table with at least name and version.",
        ),
    }
    optional_checks = {
        "code_of_conduct": _check(
            "Code of conduct",
            _first_existing(root, ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]),
            0,
            "Add CODE_OF_CONDUCT.md so contributors know expected community behavior.",
        ),
        "funding": _check(
            "Funding metadata",
            _first_existing(root, [".github/FUNDING.yml", ".github/FUNDING.yaml"]),
            0,
            "Add .github/FUNDING.yml if the project accepts sponsorship.",
        ),
        "changelog": _check(
            "Changelog",
            _first_existing(root, ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"]),
            0,
            "Add CHANGELOG.md so users can understand releases.",
        ),
    }
    earned = sum(check.weight for check in checks.values() if check.present)
    total = sum(check.weight for check in checks.values())
    suggestions = [check.suggestion for check in checks.values() if not check.present]
    suggestions.extend(check.suggestion for check in optional_checks.values() if not check.present)
    score = round((earned / total) * 100) if total else 0
    return DoctorReport(str(root), score, checks, optional_checks, suggestions, _read_project_metadata(root))


def format_text_report(report: DoctorReport) -> str:
    lines = [
        "OSS Repo Launch Doctor",
        f"Repository: {report.path}",
        f"Score: {report.score}/100",
        "",
        "Checks:",
    ]
    for check in report.checks.values():
        mark = "OK" if check.present else "MISSING"
        lines.append(f"- {mark}: {check.name} ({check.detail})")
    if report.optional_checks:
        lines.extend(["", "Optional checks:"])
        for check in report.optional_checks.values():
            mark = "OK" if check.present else "RECOMMENDED"
            lines.append(f"- {mark}: {check.name} ({check.detail})")
    if report.metadata:
        lines.extend(["", "Metadata:"])
        for key, value in sorted(report.metadata.items()):
            lines.append(f"- {key}: {value}")
    lines.extend(["", "Suggestions:"])
    if report.suggestions:
        lines.extend(f"- {item}" for item in report.suggestions)
    else:
        lines.append("- No suggestions. Launch basics are present.")
    return "\n".join(lines) + "\n"


def _to_jsonable(report: DoctorReport) -> dict[str, object]:
    return {
        "path": report.path,
        "score": report.score,
        "checks": {key: asdict(value) for key, value in report.checks.items()},
        "optional_checks": {key: asdict(value) for key, value in report.optional_checks.items()},
        "suggestions": report.suggestions,
        "metadata": report.metadata,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect an OSS repository for launch-readiness basics.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("path", nargs="?", default=".", help="Repository path to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        help="Return exit code 1 when the readiness score is below this value.",
    )
    args = parser.parse_args(argv)

    report = analyze_repository(args.path)
    if args.json:
        print(json.dumps(_to_jsonable(report), indent=2, sort_keys=True))
    else:
        print(format_text_report(report), end="")
    return 1 if report.score < max(0, args.min_score) else 0
