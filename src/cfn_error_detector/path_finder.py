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
    class IgnoreUnknownTagsLoader(yaml.SafeLoader):
        def ignore_unknown(self, suffix, node):  # type: ignore
            if isinstance(node, yaml.ScalarNode):
                return self.construct_scalar(node)
            elif isinstance(node, yaml.SequenceNode):
                return self.construct_sequence(node)
            elif isinstance(node, yaml.MappingNode):
                return self.construct_mapping(node)

    IgnoreUnknownTagsLoader.add_multi_constructor("", IgnoreUnknownTagsLoader.ignore_unknown)

    with open(file_path, "r") as file:
        return yaml.load(file, Loader=IgnoreUnknownTagsLoader)
