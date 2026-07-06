# oss-repo-launch-doctor

`oss-repo-launch-doctor` is a stdlib-first Python CLI that inspects a repository for practical open source launch basics:

- README
- license
- contribution guide
- security policy
- GitHub Actions workflow
- issue templates
- `pyproject.toml`
- package metadata

It emits a score out of 100 plus targeted suggestions.

## 0.1.2 Highlights

- CI and release workflows can now enforce a readiness floor with `--min-score`.
- The command exits `1` when the repository score falls below the configured threshold.

## Usage

```bash
python -m oss_repo_launch_doctor /path/to/repo
python -m oss_repo_launch_doctor /path/to/repo --json
python -m oss_repo_launch_doctor /path/to/repo --min-score 90
```

Installed script:

```bash
oss-repo-launch-doctor /path/to/repo
```

## Development

```bash
python -m unittest discover -s tests
```

No network calls are required by the test suite.
