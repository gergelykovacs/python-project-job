import json
from importlib.resources import files


class ProjectProperties:
    """Provides access to project properties."""

    def name(self) -> str:
        """Returns the configured name."""
        resource_path = files("my_job.resources").joinpath("project_properties.json")
        json_content = resource_path.read_text(encoding="utf-8")
        config = json.loads(json_content)
        return config.get("name")
