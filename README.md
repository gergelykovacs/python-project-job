# Python Project - Job

Python Project Blueprint

[![CI](https://github.com/gergelykovacs/python-project-job/actions/workflows/ci.yml/badge.svg)](https://github.com/gergelykovacs/python-project-job/actions/workflows/ci.yml)

## Development

Check the [Makefile](./Makefile) for automation as the initial step, it defines all project commands.

### Make Commands

| Make Command          | Description                                                                             |
|:----------------------|:----------------------------------------------------------------------------------------|
| `make venv`           | Creates a virtual environment in `.venv`.                                               |
| `make lock`           | Generates `requirements.txt` from `pyproject.toml` using `pip-compile`.                 |
| `make upgrade`        | Updates all packages in `requirements.txt` to the latest allowed versions.              |
| `make install`        | Syncs the environment with locked dependencies and installs the app in editable mode.   |
| `make setup`          | Installs dependencies and sets up git hooks (runs `install` and `pre-commit install`).  |
| `make outdated`       | Checks for newer versions of dependencies using `pip-check-updates`.                    |
| `make pip-upgrade`    | Upgrades `pip` to its latest version.                                                   |
| `make lint`           | Checks code style using `ruff` without modifying files.                                 |
| `make format`         | Automatically fixes code style issues using `ruff`.                                     |
| `make security`       | Runs `bandit` to check for security vulnerabilities.                                    |
| `make test`           | Runs unit and integration tests using `pytest` (also runs `security`).                  |
| `make sbom`           | Generates a Software Bill of Materials (SBOM) in `sbom.json`.                           |
| `make audit`          | Generates a security audit report in `audit.json`.                                      |
| `make build`          | Creates distribution files (Wheel & Tarball) in `dist/`.                                |
| `make publish`        | Uploads artifacts to the repository using `twine`.                                      |
| `make docker-build`   | Builds the Docker image for the application.                                            |
| `make docker-run`     | Runs the Docker container with mounted volumes for testing.                             |
| `make aws-login`      | Authenticates Docker with AWS ECR.                                                      |
| `make docker-publish` | Tags and pushes the Docker image to AWS ECR.                                            |
| `make docs`           | Generates documentation from docstrings into the `docs/` directory.                     |
| `make clean`          | Removes build artifacts, caches, and generated files.                                   |
| `make all`            | Runs the full development cycle: `lock`, `install`, `upgrade`, `lint`, `test`, `build`. |

The `make publish` require 

```shell
export TWINE_USERNAME=your_ldap_user
export TWINE_PASSWORD=your_ldap_password
export TWINE_REPOSITORY_URL="https://nexus.mycompany.com/repository/pypi-internal/"
```

environment variables.

## Usage

Build and run the job as:

```shell
make docker-build
make docker-run
```

## Notes

### Deployments

The containerised job can be deployed example to AWS or to Kubernetes.

- Place infrastructure IaC in the [infrastructure](./infrastructure) directory to build and maintain infrastructure as code.
- Place Helm Chart in the [charts](./charts) directory for Kubernetes deployment.

### Suggested App Structure

Under `src/my_job/` use

```shell
adapter/    # for extractors and loaders
config/     # to load and deal with application configurations e.g., resources
exception/  # for collection of internal exceptions
model/      # for domain models
resources/  # for static data and configuration
service/    # for the business logic, the transformers
main.py     # the job orchestration 
```

### Testing git hooks

Install git pre-commit hook by running `make setup`.

To test it, add the following `bad.py` to [src/my_job/](./src/my_job).

```python

import yaml
with open("bad.yaml") as f:
    data = yaml.load(f)
    print(data)
```

Run

```shell
git add -A
git commit -m 'Testing git hook' 
```

1. Fix linting issues by running `make format`.
2. Then observe security issue when trying to commit.

Finally remove the `bad.py` file.

### Troubleshooting

If virtualenv gets broken it will not expose binaries properly example:

```shell
make test
make: pytest: No such file or directory
```

In such case reset it by:

```shell
rm -rf .venv
make venv
make install
```

### Deployment alternative configuration

Twine accepts configuration from `~/.pypirc`

```toml
# ~/.pypirc
[distutils]
index-servers =
    nexus

[nexus]
# NOTE: Ensure this URL ends with a trailing slash
repository = https://nexus.mycompany.com/repository/pypi-internal/
username = your_ldap_user
password = your_ldap_password
```

and

```shell
make publish repo=nexus
```

command can be used to publish the artefacts.

## References

- [Prefect - Workflow Orchestration](https://docs.prefect.io/v3/get-started)
- [Prefect - Testing Guide](https://docs.prefect.io/v3/how-to-guides/workflows/test-workflows)
- [Python](https://www.python.org)
- [Python - Releases](https://www.python.org/downloads/)
- [Python 3.14 - Documentation](https://docs.python.org/3.14/)
- [PIP](https://pip.pypa.io/en/stable/)
- [PyPI - Package Index](https://pypi.org)
- [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PyTest](https://docs.pytest.org/en/stable/)
- [Ruff - Linting](https://docs.astral.sh/ruff/)
- [Twine - Package Publishing](https://twine.readthedocs.io/en/stable/)
- [Emoji Library](https://openmoji.org/library/) - Used in Makefile
