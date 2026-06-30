# Python Project Template

My personal template for Python projects.

## Features

* **Modern Python tooling** with [uv](https://docs.astral.sh/uv/) for dependency management and environment setup
* **Generated `pyproject.toml`** with metadata, dependencies, and uv build config
* **Just recipes** with [just](https://github.com/casey/just) for checking, coverage, testing, linting, formatting, and building
* **Code quality tooling** with [ruff](https://docs.astral.sh/ruff/), [pyrefly](https://pyrefly.org/), and pre-commit hooks
* **Testing setup** with [pytest](https://docs.pytest.org/en/stable/), coverage, and uv-powered local cross-version test runs from `.python-versions`
* **Optional GitHub Actions workflows** for linting, testing, and PyPI publishing
* **Optional GitHub repository setup** through [GitHub CLI](https://cli.github.com/)
* **License selection** using [choosealicense.com](https://choosealicense.com/) license text
* **Generated `README.md`** with badges and installation instructions
* **Optional documentation setup** with Read the Docs, Sphinx, Furo, MyST, API docs, and project links

## Requirements

* Python 3.12+
* [sprout](https://github.com/zigai/sprout)
* Git
* [GitHub CLI](https://cli.github.com/) (optional)

## Usage

```bash
sprout "https://github.com/zigai/python-project-template.git" /path/to/your/project
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

## Similar Templates

* [cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv)
* [copier-uv](https://github.com/pawamoy/copier-uv)
* [python-copier-template](https://github.com/DiamondLightSource/python-copier-template)

## License

[MIT](https://github.com/zigai/python-project-template/blob/master/LICENSE)
