# Security Review - July 2026

## Scope

The review covered repository traversal, TOML parsing, GitHub workflow inspection, CLI output, and
the package/release workflows.

## Fixed Findings

1. The launch report treated any workflow as sufficient and could not identify mutable third-party
   action tags. Reports now list every non-SHA action reference and can fail CI on the result.
2. Workflow token permissions were not assessed. Every workflow must now declare explicit
   top-level permissions for the security gate to pass.
3. Dependency-update coverage was not assessed. The gate requires both pip and GitHub Actions in
   Dependabot configuration.

## Residual Risk

The workflow checks intentionally use bounded text inspection rather than a full YAML evaluator.
They verify the highest-value repository controls but do not prove that arbitrary shell steps or
third-party actions are safe. Review action ownership and workflow scripts when changing them.

## Validation

The final PR gate runs unittest, Ruff, Bandit, pip-audit, package build, Trivy, and the doctor
against its own repository with `--fail-on-security`.
