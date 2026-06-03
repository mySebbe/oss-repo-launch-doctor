# Contributing

Thanks for improving `oss-repo-launch-doctor`.

## Local Setup

Use Python 3.11 or newer.

```bash
python -m unittest discover -s tests
```

## Pull Requests

- Keep changes stdlib-first unless a dependency is clearly justified.
- Add or update `unittest` coverage for behavior changes.
- Keep CLI output stable and useful for automation.

Release instructions live in [PUBLISHING.md](PUBLISHING.md).
