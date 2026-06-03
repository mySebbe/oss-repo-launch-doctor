"""Repository launch-readiness checks for open source projects."""

from .doctor import CheckResult, DoctorReport, analyze_repository, format_text_report

__all__ = ["__version__", "CheckResult", "DoctorReport", "analyze_repository", "format_text_report"]
from ._version import __version__
