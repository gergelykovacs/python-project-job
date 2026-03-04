import json
import re
import sys
import urllib.request
from typing import List, Tuple


def parse_dependencies(file_path: str) -> List[Tuple[str, str]]:
    dependencies = []
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Extract [project] dependencies
    project_deps_match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if project_deps_match:
        raw_deps = project_deps_match.group(1)
        dependencies.extend(extract_deps_from_string(raw_deps))

    # Extract [project.optional-dependencies] dev
    dev_deps_match = re.search(r"dev\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if dev_deps_match:
        raw_deps = dev_deps_match.group(1)
        dependencies.extend(extract_deps_from_string(raw_deps))

    return dependencies


def extract_deps_from_string(raw_string: str) -> List[Tuple[str, str]]:
    deps = []
    matches = re.findall(r'"(.*?)"', raw_string)
    for match in matches:
        # Split package name and version specifier
        parts = re.split(r"==|>=|<=|~=", match)
        name = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else "latest"
        deps.append((name, version))
    return deps


def get_python_requires(package: str, version: str) -> str:
    if version == "latest":
        url = f"https://pypi.org/pypi/{package}/json"
    else:
        url = f"https://pypi.org/pypi/{package}/{version}/json"

    try:
        with urllib.request.urlopen(url) as response:  # nosec B310
            data = json.loads(response.read().decode())
            return data["info"].get("requires_python") or "Unknown"
    except Exception:
        # Fallback to latest if specific version fails
        try:
            url = f"https://pypi.org/pypi/{package}/json"
            with urllib.request.urlopen(url) as response:  # nosec B310
                data = json.loads(response.read().decode())
                return data["info"].get("requires_python") or "Unknown"
        except Exception as e:
            return f"Error: {e}"


def is_compatible(requires_python: str, target_version: str) -> bool:
    if requires_python == "Unknown" or requires_python.startswith("Error"):
        return True

    # Clean up the requires_python string
    req = requires_python.replace(" ", "")
    conditions = req.split(",")

    try:
        target_ver_tuple = tuple(map(int, target_version.split(".")))
    except ValueError:
        return True  # Invalid target version format, assume compatible

    def to_tuple(v_str):
        return tuple(map(int, v_str.split(".")))

    for condition in conditions:
        try:
            if condition.startswith(">="):
                v_tuple = to_tuple(condition[2:])
                if target_ver_tuple < v_tuple:
                    return False
            elif condition.startswith(">"):
                v_tuple = to_tuple(condition[1:])
                if target_ver_tuple <= v_tuple:
                    return False
            elif condition.startswith("<="):
                v_tuple = to_tuple(condition[2:])
                if target_ver_tuple > v_tuple:
                    return False
            elif condition.startswith("<"):
                v_tuple = to_tuple(condition[1:])
                if target_ver_tuple >= v_tuple:
                    return False
            # Ignoring ==, !=, ~= for simplicity as they are less common for python_requires
        except ValueError:
            continue  # Skip malformed version strings in requires_python

    return True


def main():
    """
    Check the minimum python version compatibility for each dependency in pyproject.toml.
    Accepts an optional target version parameter example "3.9" and marks dependencies that
    are not compatible with the given target version.
    If the optional parameter is not provided then marker is not displayed.

    Usage:
        python3 check_compatibility.py
        python3 check_compatibility.py 3.9
    """
    target_version = None
    if len(sys.argv) > 1:
        target_version = sys.argv[1]
        print(f"Checking compatibility for Python {target_version}...\n")

    print(f"{'':<2} {'Dependency':<25} | {'Version':<15} | {'Min Python Version'}")
    print("-" * 70)

    deps = parse_dependencies("pyproject.toml")

    for name, version in deps:
        requires_python = get_python_requires(name, version)

        marker = "  "
        if target_version:
            if not is_compatible(requires_python, target_version):
                marker = "* "

        print(f"{marker}{name:<25} | {version:<15} | {requires_python}")


if __name__ == "__main__":
    main()
