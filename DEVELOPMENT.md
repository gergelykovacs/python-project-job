# Development Guidelines

## Environment Setup

### Prerequisites

- Python 3.10+
- Docker
- Make

### Installation

Create a virtual environment and install dependencies:

```bash
make venv
make setup
```

This will install the project in editable mode, install dev tools, and set up git hooks.

## Workflow

### Dependency Management

- **Lock dependencies**: Generates `requirements.txt` from `pyproject.toml`.
  ```bash
  make lock
  ```
- **Upgrade dependencies**: Updates packages to latest allowed versions.
  ```bash
  make upgrade
  ```
- **Verify compatibility of dependencies**: Checks each of the dependencies for python version compatibility, and marks dependencies that are not compatible with the given target version.
  ```bash
  # adjust py_version=3.xy as needed
  make compatibility py_version=3.10
  ```
- **Update SBOM**: Generate a Software Bill of Materials (SBOM) in `sbom.json` when dependencies are updated (tracked).
  ```bash
  make sbom
  ```
- **Audit dependencies**: Generates a security audit report in `audit.json` when dependencies are updated and review it (untracked).
  ```bash
  make audit
  ```

### Quality Assurance

- **Linting**: `make lint`
- **Formatting**: `make format`
- **Testing**: `make test`
- **Security Scan**: `make security`

## Branch Naming Convention

- `feature/`: For new features or functionality (e.g., `feature/add-login-page`).
- `fix/` or `bugfix/`: For fixing issues or bugs (e.g., `fix/header-formatting-issue`).
- `hotfix/`: For urgent, critical fixes in production (e.g., `hotfix/fix-db-connection-bug`).
- `release/`: For preparing new production releases (e.g., `release/v1.0.0` or `release/1.0.0`).
- `docs/`: For updating documentation.
- `chore/`: For maintenance tasks, dependency updates, or build improvements.