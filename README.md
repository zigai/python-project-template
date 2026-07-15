# Python Project Template

My personal template for Python projects.

## Features

* [uv](https://docs.astral.sh/uv/) dependency management and an `uv_build` package backend
* A generated `pyproject.toml` with package metadata, dependency groups, project links, and tool configuration
* [just](https://github.com/casey/just) recipes for environment setup, checks, tests, coverage, formatting, builds, and documentation
* Code quality checks with [ruff](https://docs.astral.sh/ruff/), [pyrefly](https://pyrefly.org/), Codespell, Rattle, and pre-commit
* [pytest](https://docs.pytest.org/en/stable/) and coverage, with local tests across the selected Python version range
* GitHub Actions workflows for linting, tests, and PyPI publishing
* GitHub repository creation through [GitHub CLI](https://cli.github.com/)
* Read the Docs setup using Sphinx, Furo, MyST, and generated API documentation
* Destination-aware defaults using prior answers, Git configuration, and the detected GitHub identity
* README badges and license selection using [choosealicense.com](https://choosealicense.com/) text

## Requirements

* Python 3.12+
* [sprout](https://github.com/zigai/sprout)
* Git
* [GitHub CLI](https://cli.github.com/) (optional)

## Usage

Create a project directly:

```bash
sprout new "https://github.com/zigai/python-project-template.git" /path/to/your/project
```

Or add the template for reuse:

```bash
sprout add zigai/python-project-template --name python
sprout new python /path/to/your/project
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

[MIT](https://github.com/zigai/python-project-template/blob/master/LICENSE)
