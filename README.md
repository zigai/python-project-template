# Python Project Template

A Sprout template for modern Python packages.

## Features

- [uv](https://docs.astral.sh/uv/) dependency management and an `uv_build` package backend
- A generated `pyproject.toml` with package metadata, dependency groups, project links, and tool configuration
- [just](https://github.com/casey/just) recipes for environment setup, checks, tests, coverage, formatting, builds, and documentation
- Code quality checks with [ruff](https://docs.astral.sh/ruff/), [pyrefly](https://pyrefly.org/), Codespell, Rattle, and pre-commit
- [pytest](https://docs.pytest.org/en/stable/) and coverage, with local tests across the selected Python version range
- GitHub Actions workflows for linting, tests, and PyPI publishing
- GitHub repository creation through [GitHub CLI](https://cli.github.com/)
- Read the Docs setup using Sphinx, Furo, MyST, and generated API documentation
- Destination-aware defaults using prior answers, Git configuration, and the detected GitHub identity
- README badges and license selection using [choosealicense.com](https://choosealicense.com/) text

## Requirements

- [Sprout](https://github.com/zigai/sprout)
- Git
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- [GitHub CLI](https://cli.github.com/) (optional, for GitHub repository creation)

## Usage

Create a project directly:

```bash
sprout new zigai/python-project-template ./my-project
```

Or:

```bash
uvx --from sprout-template sprout new zigai/python-project-template ./my-project
```

Or add the template for reuse:

```bash
sprout add zigai/python-project-template --name py
sprout new py ./my-project
```

Run `sprout new py --help` to inspect template-specific flags:

```text
Usage: sprout new [options] TEMPLATE DESTINATION

Generate a project from a Sprout manifest.

Positional arguments:
  TEMPLATE              Trusted name, local path, or Git repository containing
                        sprout.py
  DESTINATION           Target directory for the generated project

Options:
  --help                                 Show this help message and exit
  --force                                Overwrite files in the destination
                                         directory if they already exist

Project:
  --package-name <name>                  Python package name - Use a valid
                                         Python identifier (snake_case).
  --repo-name <name>                     Repository name - Typically the
                                         package name with dashes.
  --project-type <type>                  Project type (choices: library, cli)
                                         [default: library]
  --python-min-version <version>         Minimum supported Python version
                                         (choices: 3.10, 3.11, 3.12, 3.13,
                                         3.14) [default: 3.10]
  --python-max-version <version>         Maximum supported Python version
  --python-default-version <version>     Default development Python version

Metadata:
  --author-name <name>                   Author name
  --author-email <email>                 Author email
  --description <text>                   Project description
  --repository-url <url>                 Repository URL

Git:
  --[no-]create-github-repo              Create a GitHub repository now - Uses
                                         GitHub CLI (`gh repo create`) after
                                         files are generated and pushes the
                                         initial commit when available.
                                         [default: no]
  --github-repo-visibility <visibility>  GitHub repository visibility
                                         (choices: public, private) [default:
                                         public]
  --[no-]git-init                        Initialize a local git repository and
                                         create an initial commit [default:
                                         yes]

Features:
  --copyright-license <license>          Project license (choices: None, MIT,
                                         Apache-2.0, GPL-3.0, BSD-3-Clause,
                                         ...; 34 available) [default: None]
  --github-actions <workflow>            Select GitHub Actions workflows -
                                         Pick any workflows to include. Leave
                                         blank for none. (multiple values
                                         allowed) (choices: tests, lint,
                                         publish)
  --[no-]setup-readthedocs               Set up Read the Docs documentation -
                                         Adds the Sphinx/Furo docs setup and
                                         Read the Docs config. [default: yes]
  --[no-]readme-badges                   Include README badges - Adds test,
                                         lint, and publish workflow status
                                         badges to the README. [default: yes]
```

## Generated Project Structure

```text
your-project/
├── your_package/
│   ├── __init__.py
│   └── py.typed
├── .github/workflows/          # optional selected workflows
├── .python-version             # default local Python version
├── .python-versions            # local test matrix Python versions
├── .editorconfig
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── docs/                       # optional Read the Docs site
├── .readthedocs.yaml           # optional Read the Docs config
├── Justfile
├── LICENSE                     # omitted when no license is selected
└── .gitignore
```

## License

[MIT](LICENSE)
