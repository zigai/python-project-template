# Copier Python Template

My personal Copier template for Python projects.

## Features

* **Modern Python tooling** with [uv](https://docs.astral.sh/uv/) for dependency management and environment setup
* **Pre-configured ```pyproject.toml```**
* **Automated workflows** - [just](https://github.com/casey/just) commands for testing, linting, and building
* **Code quality tools**: [ruff](https://docs.astral.sh/ruff/) for linting and formatting, pre-commit hooks
* **Testing setup** with [pytest](https://docs.pytest.org/en/stable/) and [Hatch](https://hatch.pypa.io/latest/) for cross-version testing
* **GitHub Actions integration**: optional workflows for linting, testing and PyPI publishing
* **Licenses from** [choosealicense.com](https://choosealicense.com/)
* **Basic ```README.md```** with badges and installation instructions

## Requirements

* Python 3.8+
* [Copier](https://copier.readthedocs.io/) (`pip install copier copier_templates_extensions`)
* Git

## Quick Setup

Create a new Python project:

```bash
copier copy --trust "https://github.com/zigai/python-project-template.git" /path/to/your/project
```

or

```bash
copier copy --trust "gh:zigai/python-project-template" /path/to/your/project
```

## Generated Project Structure

```
your-project/
├── your_package/
│   └── __init__.py
├── tests/
│   └── test_your_package.py
├── .github/workflows/          
│   └── publish.yml
├── pyproject.toml             
├── README.md                  
├── CONTRIBUTING.md             
├── Justfile                    
├── LICENSE                    
└── .gitignore                  
```

## Similar Templates

* [copier-uv](https://github.com/pawamoy/copier-uv)
* [python-copier-template](https://github.com/DiamondLightSource/python-copier-template)

## License

This template is released under the [MIT License](https://github.com/zigai/python-project-template/blob/master/LICENSE).
