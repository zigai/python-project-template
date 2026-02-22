from __future__ import annotations

import re
import shutil
import subprocess
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


def _is_github_repo_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    return value.strip().startswith("https://github.com/")


def _github_repo_target(answers: dict[str, Any]) -> str:
    repository_url = str(answers.get("repository_url") or "").strip()
    match = re.match(
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
        repository_url,
    )
    if match:
        owner = match.group("owner")
        repo = match.group("repo")
        return f"{owner}/{repo}"

    repo_name = str(answers.get("repo_name") or "").strip()
    return repo_name or "my-package"


def _ensure_git_repo(destination: Path, *, console: Any) -> bool:
    git_executable = shutil.which("git")
    if git_executable is None:
        console.print(
            "[yellow]Git is not installed; skipping local repository initialization.[/yellow]"
        )
        return False

    if (destination / ".git").exists():
        return True

    result = subprocess.run(
        [git_executable, "init"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True

    details = result.stderr.strip() or result.stdout.strip() or "unknown error"
    console.print(f"[yellow]Failed to initialize git repository: {details}[/yellow]")
    return False


def _has_git_commits(destination: Path, *, git_executable: str) -> bool:
    result = subprocess.run(
        [git_executable, "rev-parse", "--verify", "HEAD"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _create_initial_commit(destination: Path, answers: dict[str, Any], *, console: Any) -> bool:
    git_executable = shutil.which("git")
    if git_executable is None:
        console.print("[yellow]Git is not installed; skipping initial commit.[/yellow]")
        return False

    if not _ensure_git_repo(destination, console=console):
        return False

    add_result = subprocess.run(
        [git_executable, "add", "--all"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    if add_result.returncode != 0:
        details = add_result.stderr.strip() or add_result.stdout.strip() or "unknown error"
        console.print(f"[yellow]Failed to stage files for initial commit: {details}[/yellow]")
        return _has_git_commits(destination, git_executable=git_executable)

    staged_diff_result = subprocess.run(
        [git_executable, "diff", "--cached", "--quiet", "--exit-code"],
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    if staged_diff_result.returncode == 0:
        return _has_git_commits(destination, git_executable=git_executable)
    if staged_diff_result.returncode != 1:
        details = (
            staged_diff_result.stderr.strip()
            or staged_diff_result.stdout.strip()
            or "unknown error"
        )
        console.print(f"[yellow]Failed to inspect staged changes: {details}[/yellow]")
        return _has_git_commits(destination, git_executable=git_executable)

    commit_command: list[str] = [git_executable]
    author_name = str(answers.get("author_name") or "").strip()
    author_email = str(answers.get("author_email") or "").strip()
    if author_name:
        commit_command.extend(["-c", f"user.name={author_name}"])
    if author_email:
        commit_command.extend(["-c", f"user.email={author_email}"])
    commit_command.extend(["commit", "-m", "chore: initialize project"])

    commit_result = subprocess.run(
        commit_command,
        cwd=destination,
        check=False,
        capture_output=True,
        text=True,
    )
    if commit_result.returncode == 0:
        return True

    details = commit_result.stderr.strip() or commit_result.stdout.strip() or "unknown error"
    console.print(f"[yellow]Failed to create initial commit: {details}[/yellow]")
    return _has_git_commits(destination, git_executable=git_executable)


def _create_github_repo(
    destination: Path, answers: dict[str, Any], *, console: Any, push: bool = False
) -> None:
    gh_executable = shutil.which("gh")
    if gh_executable is None:
        console.print(
            "[yellow]GitHub CLI not found; skipping repository creation.[/yellow]"
        )
        return

    visibility = str(answers.get("github_repo_visibility") or "public").strip().lower()
    if visibility not in {"public", "private"}:
        visibility = "public"

    repo_target = _github_repo_target(answers)
    description = str(answers.get("description") or "").strip()

    command = [
        gh_executable,
        "repo",
        "create",
        repo_target,
        f"--{visibility}",
    ]

    if description:
        command.extend(["--description", description])

    if _ensure_git_repo(destination, console=console):
        command.extend(["--source", str(destination), "--remote", "origin"])
        if push:
            command.append("--push")
    else:
        console.print(
            "[yellow]Proceeding to create GitHub repository without connecting the local folder.[/yellow]"
        )

    result = subprocess.run(
        command,
        cwd=destination,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return

    details = result.stderr.strip() or result.stdout.strip() or "unknown error"
    console.print(f"[yellow]Failed to create GitHub repository: {details}[/yellow]")


# Sprout manifest entrypoints


def should_skip_file(relative_path: str, answers: dict[str, Any]) -> bool:
    github_actions = answers.get("github_actions", [])

    if relative_path == "LICENSE.jinja" and answers.get("copyright_license") == "None":
        return True
    if (
        relative_path == ".github/workflows/test.yml.jinja"
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
    gh_available = shutil.which("gh") is not None

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
        Question.yes_no(
            key="create_github_repo",
            prompt="Create GitHub repository now?",
            help_text=(
                "Uses GitHub CLI (`gh repo create`) after files are generated and pushes "
                "the initial commit when available."
            ),
            default=False,
            when=gh_available,
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
            key="readme_badges",
            prompt="Include README badges?",
            default=True,
        ),
    ]


def apply(
    *,
    env: Environment,
    template_dir: Path,
    destination: Path,
    answers: dict[str, Any],
    console: Any,
    render_templates: Any,
) -> list[Path]:
    created = render_templates(
        env,
        template_dir,
        destination,
        answers,
        skip=should_skip_file,
        render_paths=True,
    )

    if bool(answers.get("create_github_repo")):
        if not _is_github_repo_url(answers.get("repository_url")):
            console.print(
                "[yellow]Repository URL is not a GitHub URL; GitHub repository will use repo name only.[/yellow]"
            )
        has_commits = _create_initial_commit(destination, answers, console=console)
        _create_github_repo(destination, answers, console=console, push=has_commits)
    elif bool(answers.get("git_init")):
        _create_initial_commit(destination, answers, console=console)

    return created


extensions: Sequence[type[Extension]] = (
    GitDefaultsExtension,
    PythonVersionExtension,
    CurrentYearExtension,
)


template_dir = "template"
