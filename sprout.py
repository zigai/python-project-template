from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2.ext import Extension

from sprout import (
    CurrentYearExtension,
    GitDefaultsExtension,
    ManifestContext,
    Question,
    validate_repository_url,
)
from sprout.cli import render_templates as sprout_render_templates
from sprout.project import (
    SPDX_LICENSE_CHOICES,
    github_repository_url,
    run_git_post_actions,
    should_skip_license_file,
    validate_repository_name,
)
from sprout.prompt import console as sprout_console


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


python_version_choices = [
    ("3.10", "Python 3.10"),
    ("3.11", "Python 3.11"),
    ("3.12", "Python 3.12"),
    ("3.13", "Python 3.13"),
    ("3.14", "Python 3.14"),
]

license_choices = list(SPDX_LICENSE_CHOICES)

github_actions_choices = [
    ("tests", "Run tests"),
    ("lint", "Lint and format"),
    ("publish", "Publish to PyPI"),
]


def validate_package_name(value: str, answers: dict[str, Any]) -> tuple[bool, str | None]:
    name = value.strip()
    if not name:
        return False, "Package name is required."
    if not re.compile(r"^[a-z][_a-z0-9]*$").fullmatch(name):
        return (
            False,
            "Package name must be snake_case and start with a letter (letters, numbers, underscores).",
        )
    return True, None


def validate_versions(value: str, answers: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"python_min_version", "python_max_version", "python_default_version"}
    if not required.issubset(answers):
        return True, None

    min_version = tuple(int(part) for part in str(answers["python_min_version"]).split("."))
    max_version = tuple(int(part) for part in str(answers["python_max_version"]).split("."))
    default_version = tuple(int(part) for part in str(answers["python_default_version"]).split("."))

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


# Sprout manifest entrypoints


def should_skip_file(relative_path: str, answers: dict[str, Any]) -> bool:
    github_actions = answers.get("github_actions", [])

    if should_skip_license_file(relative_path, answers):
        return True
    if relative_path == ".github/workflows/test.yml.jinja" and "tests" not in github_actions:
        return True
    if relative_path == ".github/workflows/lint.yml.jinja" and "lint" not in github_actions:
        return True
    if relative_path == ".github/workflows/publish.yml.jinja" and "publish" not in github_actions:
        return True
    if relative_path == ".readthedocs.yaml.jinja" and not answers.get("setup_readthedocs"):
        return True
    if relative_path.startswith("docs/") and not answers.get("setup_readthedocs"):
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
        repo = str(answers.get("repo_name") or default_repo_name(answers))
        username = str(env.globals.get("github_username") or "my-user")
        return github_repository_url(username, repo)

    def python_max_version_choices(answers: dict[str, Any]) -> list[tuple[str, str]]:
        min_version = answers.get("python_min_version")
        return filtered_version_choices(min_version=min_version)

    def default_python_max_version(answers: dict[str, Any]) -> str:
        choices = python_max_version_choices(answers)
        preferred = "3.14"
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
        return filtered_version_choices(min_version=min_version, max_version=max_version)

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
            validators=[validate_repository_name],
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
            default="",
            parser=lambda value, answers: value.strip(),
        ),
        Question(
            key="repository_url",
            prompt="Repository URL",
            default=default_repository_url,
            validators=[validate_repository_url],
        ),
        Question.yes_no(
            key="create_github_repo",
            prompt="Create a GitHub repository now?",
            help_text=(
                "Uses GitHub CLI (`gh repo create`) after files are generated and pushes "
                "the initial commit when available."
            ),
            default=False,
        ),
        Question(
            key="github_repo_visibility",
            prompt="GitHub repository visibility",
            choices=[("public", "Public"), ("private", "Private")],
            default="public",
            when=lambda answers: bool(answers.get("create_github_repo")),
        ),
        Question.yes_no(
            key="git_init",
            prompt="Initialize a local git repository and create an initial commit?",
            default=True,
            when=lambda answers: not bool(answers.get("create_github_repo")),
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
        Question.yes_no(
            key="setup_readthedocs",
            prompt="Set up Read the Docs documentation?",
            help_text="Adds the Sphinx/Furo docs setup and Read the Docs config.",
            default=True,
        ),
        Question.yes_no(
            key="readme_badges",
            prompt="Include README badges?",
            default=True,
        ),
    ]


def apply(context: ManifestContext) -> list[Path]:
    created = sprout_render_templates(
        context.env,
        context.template_dir,
        context.destination,
        context.answers,
        skip=should_skip_file,
        render_paths=True,
    )

    run_git_post_actions(
        context.destination,
        context.answers,
        console=sprout_console,
        default_visibility="public",
        fallback_repo_name="my-package",
    )

    return created


extensions: Sequence[type[Extension]] = (
    GitDefaultsExtension,
    PythonVersionExtension,
    CurrentYearExtension,
)


template_dir = "template"
