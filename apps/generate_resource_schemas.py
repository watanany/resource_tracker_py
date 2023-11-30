import json
import IPython as ipy
from typing import Optional
from resource_tracker import snake_case_to_camel_case, get_template

# fetch_resource_schemas.pyの出力
resources_path = "data/resources.jsonl"
with open(resources_path) as f:
    resources = list(map(json.loads, f.readlines()))


def map_type(typ: str) -> str:
    if typ == "List of String":
        return "list[str]"
    elif typ == "Set of String":
        return "set[str]"
    elif typ == "Map of String":
        return "list[dict[str, str]]"
    elif typ == "Set of Number":
        return "set[Num]"
    elif typ == "Block List":
        return "BlockList"
    elif typ == "Block Set":
        return "BlockSet"
    elif typ == "String":
        return "str"
    elif typ == "Number":
        return "Number"
    elif typ == "Boolean":
        return "bool"
    elif typ == "Block":
        return "Block"
    else:
        raise ValueError("Unknown typ: {}".format(typ))


def gen_read_only_attribute(name: str, type: str) -> str:
    return f"{name}: ReadOnly[{type}] = None"


def gen_optional_attribute(name: str, type: str) -> str:
    return f"{name}: Optional[{type}] = None"


def gen_required_attribute(name: str, type: str) -> str:
    return f"{name}: {type}"


def gen_resource_schema(resource: dict) -> str:
    resource_name = "snowflake_{}".format(resource["name"])
    resource_attributes = resource["attributes"]

    attr_exprs = []
    for attr in resource_attributes:
        if attr["required"]:
            a = gen_required_attribute(attr["name"], map_type(attr["type"]))
        elif attr["optional"]:
            a = gen_optional_attribute(attr["name"], map_type(attr["type"]))
        else:
            a = None

        attr_exprs.append(a)

    attr_exprs = [a for a in attr_exprs if a is not None]
    template = get_template("snowflake_resource.py.jinja")
    class_name = snake_case_to_camel_case(resource_name)
    return template.render(class_name=class_name, attrs=attr_exprs)


def main():
    for resource in resources:
        print(gen_resource_schema(resource))


if __name__ == "__main__":
    main()
