import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from oss_repo_launch_doctor.doctor import analyze_repository, format_text_report


class LaunchDoctorTest(unittest.TestCase):
    def test_analyze_repository_scores_present_launch_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            (repo / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (repo / "CONTRIBUTING.md").write_text("Contribute\n", encoding="utf-8")
            (repo / "SECURITY.md").write_text("Security\n", encoding="utf-8")
            (repo / "CODE_OF_CONDUCT.md").write_text("Be kind\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text(
                "[project]\nname = \"demo\"\nversion = \"0.1.0\"\n",
                encoding="utf-8",
            )
            workflow = repo / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "test.yml").write_text(
                "name: tests\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n",
                encoding="utf-8",
            )
            (repo / ".github" / "dependabot.yml").write_text(
                'version: 2\nupdates:\n  - package-ecosystem: "pip"\n'
                '  - package-ecosystem: "github-actions"\n',
                encoding="utf-8",
            )
            (repo / ".github" / "FUNDING.yml").write_text("github: demo\n", encoding="utf-8")
            issue_templates = repo / ".github" / "ISSUE_TEMPLATE"
            issue_templates.mkdir(parents=True)
            (issue_templates / "bug.md").write_text("bug\n", encoding="utf-8")

            report = analyze_repository(repo)

        self.assertEqual(report.score, 100)
        self.assertFalse(report.suggestions)
        self.assertTrue(report.checks["readme"].present)
        self.assertTrue(report.optional_checks["changelog"].present)
        self.assertEqual(report.metadata["project_name"], "demo")
        self.assertTrue(all(check.present for check in report.security_checks.values()))

    def test_analyze_repository_suggests_missing_launch_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = analyze_repository(Path(tmp))

        self.assertLess(report.score, 50)
        self.assertIn("Add a README", " ".join(report.suggestions))
        self.assertIn("CHANGELOG", " ".join(report.suggestions))
        self.assertFalse(report.checks["license"].present)

    def test_text_and_json_cli_outputs_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

            text = subprocess.run(
                [sys.executable, "-m", "oss_repo_launch_doctor", str(repo)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )
            data = subprocess.run(
                [sys.executable, "-m", "oss_repo_launch_doctor", str(repo), "--json"],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

        self.assertIn("OSS Repo Launch Doctor", text.stdout)
        self.assertIn("Score:", text.stdout)
        parsed = json.loads(data.stdout)
        self.assertIn("score", parsed)
        self.assertIn("optional_checks", parsed)
        self.assertIn("suggestions", parsed)
        self.assertIn("security_checks", parsed)

    def test_cli_min_score_returns_nonzero_when_score_is_too_low(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

            result = subprocess.run(
                [sys.executable, "-m", "oss_repo_launch_doctor", str(repo), "--json", "--min-score", "90"],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

        self.assertEqual(result.returncode, 1)
        self.assertLess(json.loads(result.stdout)["score"], 90)

    def test_format_text_report_lists_suggestions(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = analyze_repository(Path(tmp))

        output = format_text_report(report)

        self.assertIn("Suggestions", output)
        self.assertIn("Optional checks", output)
        self.assertIn("README", output)
        self.assertIn("Security checks", output)

    def test_cli_fail_on_security_rejects_mutable_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            workflow = repo / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "test.yml").write_text(
                "name: test\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    steps:\n      - uses: actions/checkout@v7\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "oss_repo_launch_doctor",
                    str(repo),
                    "--json",
                    "--fail-on-security",
                ],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["security_checks"]["immutable_actions"]["present"])
        self.assertIn("actions/checkout@v7", data["security_checks"]["immutable_actions"]["detail"])


if __name__ == "__main__":
    unittest.main()
