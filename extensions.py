import re
import subprocess
from datetime import date

from jinja2.ext import Extension


class GitDefaultsExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals["git_user_name"] = self._get_git_config("user.name")
        environment.globals["git_user_email"] = self._get_git_config("user.email")
        environment.globals["github_username"] = self._get_github_username()

    def _get_git_config(self, key: str) -> str:
        """Get a git configuration value.

        Args:
            key: The git config key to retrieve (e.g., 'user.name', 'user.email')

        Returns:
            The configuration value or empty string if not found
        """
        try:
            result = subprocess.run(
                ["git", "config", "--get", key],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    def _get_github_username(self) -> str:
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            for line in result.stdout.splitlines():
                if "github.com" in line:
                    # Extract username from URLs like:
                    # git@github.com:username/repo.git
                    # https://github.com/username/repo.git
                    match = re.search(r"github\.com[:/]([^/]+)", line)
                    if match:
                        return match.group(1)

        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
        return ""


class PythonVersionExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals["py_versions_range"] = self._py_versions_range
        environment.globals["py_classifiers"] = self._py_classifiers
        environment.globals["black_target_versions"] = self._black_target_versions

    def _py_versions_range(self, min_version: str, max_version: str) -> list[str]:
        min_major, min_minor = map(int, min_version.split("."))
        _, max_minor = map(int, max_version.split("."))
        versions = []
        for minor in range(min_minor, max_minor + 1):
            versions.append(f"{min_major}.{minor}")
        return versions

    def _py_classifiers(self, min_version: str, max_version: str) -> list[str]:
        versions = self._py_versions_range(min_version, max_version)
        return [f"Programming Language :: Python :: {version}" for version in versions]

    def _black_target_versions(self, min_version: str, max_version: str) -> list[str]:
        versions = self._py_versions_range(min_version, max_version)
        return [f"py{version.replace('.', '')}" for version in versions]


class CurrentYearExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals["current_year"] = date.today().year
