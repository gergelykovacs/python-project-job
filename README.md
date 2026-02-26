# Python Project - Job

Python Project Blueprint

## Development

Check the [Makefile](./Makefile) for automation as the initial step, it defines all project commands.

Short summary of commands in a desired order of use.

```shell
make venv # Create virtual environment (first step)

make install # Install dependencies (second step)
make setup   # Install dependencies and git hooks (runs install)

mske lock     # Lock dependencies
make upgrade  # Upgrade dependencies
make outdated # Check for outdated dependencies

make lint     # Check the code style
make format   # Fix style issues
make security # Check for security issues
make test     # Run tests

make sbom  # Generate Software Bill of Materials - run it when dependencies change
make audit # Run vulnerability audit - not tracked by Git

make build # Create distributable packages (artefacts)

make docker-build   # Build Docker image
make docker-run     # Run Docker container
make aws-login      # Login to the ECR repository
make docker-publish # Run Docker container

# Set repository access configurations
# Alternative configuration is provided in the notes section
export TWINE_USERNAME=your_ldap_user
export TWINE_PASSWORD=your_ldap_password
export TWINE_REPOSITORY_URL="https://nexus.mycompany.com/repository/pypi-internal/"
make publish # Publish the artefacts

make clean # Remove all generated files
make docs  # Generate documentation - not tracked by Git

make all # In development (lock install upgrade lint test build)
```

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
