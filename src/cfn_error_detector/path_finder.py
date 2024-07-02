from pathlib import Path
from typing import Any

import yaml


def find_stack_template(template_file: Path, stack_path: list[str]) -> Path:
    if stack_path == []:
        return template_file

    template = load_template_file(template_file)
    url = template["Resources"][stack_path[0]]["Properties"]["TemplateURL"]

    file_path = template_file.parent / url

    return find_stack_template(file_path, stack_path[1:])


def load_template_file(file_path: Path) -> Any:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
