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

## 0.1.1 Highlights

- Reports now include optional launch maturity checks without changing the core readiness score.
- Optional checks cover Code of Conduct, funding metadata, and changelog files.

## Usage

```bash
python -m oss_repo_launch_doctor /path/to/repo
python -m oss_repo_launch_doctor /path/to/repo --json
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
