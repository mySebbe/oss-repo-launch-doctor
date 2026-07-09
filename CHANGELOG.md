# Changelog

All notable changes to `oss-repo-launch-doctor` will be documented in this file.

The format is based on Keep a Changelog, and this project uses semantic versioning.

## [Unreleased]

- Added supply-chain checks for immutable GitHub Action references, explicit workflow permissions,
  and Dependabot coverage.
- Added `--fail-on-security` for CI enforcement without changing the historical readiness score.

## [0.1.2] - 2026-07-06

- Updated GitHub Actions workflow dependencies to current major versions.
- Modernized package license metadata to avoid current Setuptools deprecation warnings.
- Added `--min-score` to fail CI or release checks below a required launch-readiness score.
- Kept text and JSON output available even when the score gate fails.

## [0.1.1] - 2026-06-17

- Added optional non-scoring checks for Code of Conduct, funding metadata, and changelog files.
- Included optional checks in text and JSON output.
- Fixed GitHub Actions workflow pins to supported action versions.

## [0.1.0] - 2026-06-03

- Initial open-source release with CLI, examples, tests, GitHub workflows, security policy, and contributor docs.
