from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2.ext import Extension

from sprout import GitDefaultsExtension, Question, validate_repository_url


class PythonVersionExtension(Extension):
    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.globals["py_versions_range"] = self._py_versions_range
        environment.globals["py_classifiers"] = self._py_classifiers
        environment.globals["black_target_versions"] = self._black_target_versions

    def _py_versions_range(self, min_version: str, max_version: str) -> list[str]:
        min_major, min_minor = map(int, min_version.split("."))
        _, max_minor = map(int, max_version.split("."))
        return [f"{min_major}.{minor}" for minor in range(min_minor, max_minor + 1)]

    def _py_classifiers(self, min_version: str, max_version: str) -> list[str]:
        versions = self._py_versions_range(min_version, max_version)
        return [f"Programming Language :: Python :: {version}" for version in versions]

    def _black_target_versions(self, min_version: str, max_version: str) -> list[str]:
        versions = self._py_versions_range(min_version, max_version)
        return [f"py{version.replace('.', '')}" for version in versions]


class CurrentYearExtension(Extension):
    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.globals["current_year"] = date.today().year


def validate_package_name(
    value: str, answers: dict[str, Any]
) -> tuple[bool, str | None]:
    name = value.strip()
    if not name:
        return False, "Package name is required."
    if not re.compile(r"^[a-z][_a-z0-9]*$").fullmatch(name):
        return (
            False,
            "Package name must be snake_case and start with a letter (letters, numbers, underscores).",
        )
    return True, None


def validate_repo_name(value: str, answers: dict[str, Any]) -> tuple[bool, str | None]:
    name = value.strip()
    if not name:
        return False, "Repository name is required."
    if not re.compile(r"^[A-Za-z0-9._-]+$").fullmatch(name):
        return (
            False,
            "Repository name may only include letters, numbers, dots, underscores, and hyphens.",
        )
    return True, None


def validate_versions(value: str, answers: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"python_min_version", "python_max_version", "python_default_version"}
    if not required.issubset(answers):
        return True, None

    min_version = tuple(
        int(part) for part in str(answers["python_min_version"]).split(".")
    )
    max_version = tuple(
        int(part) for part in str(answers["python_max_version"]).split(".")
    )
    default_version = tuple(
        int(part) for part in str(answers["python_default_version"]).split(".")
    )

    if min_version > max_version:
        return (
            False,
            "Minimum Python version must be less than or equal to the maximum version.",
        )
    if not (min_version <= default_version <= max_version):
        return False, "Default Python version must be within the supported range."

    return True, None


def _python_identifier(name: str) -> str:
    sanitized = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_").lower()
    if not sanitized:
        return "my_package"
    if sanitized[0].isdigit():
        return f"pkg_{sanitized}"
    return sanitized


python_version_choices = [
    ("3.8", "Python 3.8"),
    ("3.9", "Python 3.9"),
    ("3.10", "Python 3.10"),
    ("3.11", "Python 3.11"),
    ("3.12", "Python 3.12"),
    ("3.13", "Python 3.13"),
    ("3.14", "Python 3.14"),
]

license_choices = [
    ("None", "No license"),
    ("MIT", "MIT License"),
    ("Apache-2.0", "Apache License 2.0"),
    ("GPL-3.0", "GNU General Public License v3.0 only"),
    ("BSD-3-Clause", 'BSD 3-Clause "New" or "Revised" License'),
    ("Unlicense", "The Unlicense"),
    ("GPL-2.0", "GNU General Public License v2.0 only"),
    ("AGPL-3.0", "GNU Affero General Public License v3.0"),
    ("LGPL-3.0", "GNU Lesser General Public License v3.0 only"),
    ("LGPL-2.1", "GNU Lesser General Public License v2.1 only"),
    ("BSD-2-Clause", 'BSD 2-Clause "Simplified" License'),
    ("BSD-3-Clause-Clear", "BSD 3-Clause Clear License"),
    ("BSL-1.0", "Boost Software License 1.0"),
    ("CC-BY-4.0", "Creative Commons Attribution 4.0 International"),
    ("CC-BY-SA-4.0", "Creative Commons Attribution Share Alike 4.0"),
    ("CC0-1.0", "Creative Commons Zero v1.0 Universal"),
    ("WTFPL", "Do What The F*ck You Want To Public License"),
    ("AFL-3.0", "Academic Free License v3.0"),
    ("Artistic-2.0", "Artistic License 2.0"),
    ("ECL-2.0", "Educational Community License v2.0"),
    ("EPL-1.0", "Eclipse Public License 1.0"),
    ("EPL-2.0", "Eclipse Public License 2.0"),
    ("EUPL-1.1", "European Union Public License 1.1"),
    ("EUPL-1.2", "European Union Public License 1.2"),
    ("ISC", "ISC License"),
    ("LPPL-1.3c", "LaTeX Project Public License v1.3c"),
    ("MPL-2.0", "Mozilla Public License 2.0"),
    ("MS-PL", "Microsoft Public License"),
    ("MS-RL", "Microsoft Reciprocal License"),
    ("NCSA", "University of Illinois/NCSA Open Source License"),
    ("OFL-1.1", "SIL Open Font License 1.1"),
    ("OSL-3.0", "Open Software License 3.0"),
    ("PostgreSQL", "PostgreSQL License"),
    ("Zlib", "zlib License"),
]

github_actions_choices = [
    ("tests", "Run tests"),
    ("lint", "Lint and format"),
    ("publish", "Publish to PyPI"),
]


def should_skip_file(relative_path: str, answers: dict[str, Any]) -> bool:
    github_actions = answers.get("github_actions", [])

    if relative_path == "LICENSE.jinja" and answers.get("copyright_license") == "None":
        return True
    if (
        relative_path == ".github/workflows/tests.yml.jinja"
        and "tests" not in github_actions
    ):
        return True
    if (
        relative_path == ".github/workflows/lint.yml.jinja"
        and "lint" not in github_actions
    ):
        return True
    if (
        relative_path == ".github/workflows/publish.yml.jinja"
        and "publish" not in github_actions
    ):
        return True
    return False


def questions(env: Environment, destination: Path) -> list[Question]:
    git_user_name = env.globals.get("git_user_name", "")
    git_user_email = env.globals.get("git_user_email", "")

    suggested_package = _python_identifier(destination.name)

    def version_tuple(value: str | None) -> tuple[int, int] | None:
        if not value:
            return None
        major, minor = value.split(".")
        return int(major), int(minor)

    def filtered_version_choices(
        *,
        min_version: str | None = None,
        max_version: str | None = None,
    ) -> list[tuple[str, str]]:
        min_tuple = version_tuple(min_version)
        max_tuple = version_tuple(max_version)
        choices: list[tuple[str, str]] = []
        for value, label in python_version_choices:
            current_tuple = version_tuple(value)
            if min_tuple and current_tuple and current_tuple < min_tuple:
                continue
            if max_tuple and current_tuple and current_tuple > max_tuple:
                continue
            choices.append((value, label))
        return choices

    def default_package_name(answers: dict[str, Any]) -> str:
        return suggested_package

    def default_repo_name(answers: dict[str, Any]) -> str:
        package = answers.get("package_name") or suggested_package
        repo = str(package).replace("_", "-")
        return repo or "my-package"

    def default_repository_url(answers: dict[str, Any]) -> str:
        repo = answers.get("repo_name") or default_repo_name(answers)
        username = env.globals.get("github_username") or "my-user"
        return f"https://github.com/{username}/{repo}"

    def python_max_version_choices(answers: dict[str, Any]) -> list[tuple[str, str]]:
        min_version = answers.get("python_min_version")
        return filtered_version_choices(min_version=min_version)

    def default_python_max_version(answers: dict[str, Any]) -> str:
        choices = python_max_version_choices(answers)
        preferred = "3.13"
        available_values = [value for value, _ in choices]
        if preferred in available_values:
            return preferred
        if available_values:
            return available_values[-1]
        return preferred

    def python_default_version_choices(
        answers: dict[str, Any],
    ) -> list[tuple[str, str]]:
        min_version = answers.get("python_min_version")
        max_version = answers.get("python_max_version")
        return filtered_version_choices(
            min_version=min_version, max_version=max_version
        )

    def default_python_default_version(answers: dict[str, Any]) -> str:
        choices = python_default_version_choices(answers)
        preferred = "3.12"
        available_values = [value for value, _ in choices]
        if preferred in available_values:
            return preferred
        for key in (
            answers.get("python_max_version"),
            answers.get("python_min_version"),
        ):
            if key in available_values:
                return str(key)
        if available_values:
            return available_values[-1]
        return preferred

    return [
        Question(
            key="package_name",
            prompt="Python package name",
            help="Use a valid Python identifier (snake_case).",
            default=default_package_name,
            validators=[validate_package_name],
        ),
        Question(
            key="repo_name",
            prompt="Repository name",
            help="Typically the package name with dashes.",
            default=default_repo_name,
            validators=[validate_repo_name],
        ),
        Question(
            key="author_name",
            prompt="Author name",
            default=git_user_name or None,
        ),
        Question(
            key="author_email",
            prompt="Author email",
            default=git_user_email or None,
        ),
        Question(
            key="description",
            prompt="Project description",
            default=" ",
            parser=lambda value, answers: value.strip(),
        ),
        Question(
            key="repository_url",
            prompt="Repository URL",
            default=default_repository_url,
            validators=[validate_repository_url],
        ),
        Question(
            key="python_min_version",
            prompt="Minimum supported Python version",
            choices=python_version_choices,
            default="3.10",
        ),
        Question(
            key="python_max_version",
            prompt="Maximum supported Python version",
            choices=python_max_version_choices,
            default=default_python_max_version,
            validators=[validate_versions],
        ),
        Question(
            key="python_default_version",
            prompt="Default development Python version",
            choices=python_default_version_choices,
            default=default_python_default_version,
            validators=[validate_versions],
        ),
        Question(
            key="copyright_license",
            prompt="Project license",
            choices=license_choices,
            default="None",
        ),
        Question(
            key="github_actions",
            prompt="Select GitHub Actions workflows",
            help="Pick any workflows to include. Leave blank for none.",
            choices=github_actions_choices,
            multiselect=True,
            default=[],
        ),
        Question(
            key="readme_badges",
            prompt="Include README badges?",
            choices=[("yes", "Yes"), ("no", "No")],
            default="yes",
            parser=lambda value, answers: value.lower() in {"yes", "y", "true", "1"},
        ),
    ]


extensions: Sequence[type[Extension]] = (
    GitDefaultsExtension,
    PythonVersionExtension,
    CurrentYearExtension,
)


template_dir = "template"
