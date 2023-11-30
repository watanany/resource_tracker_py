import json
import re
import IPython as ipy
from dataclasses import asdict
from typing import Any, List, Tuple, Optional
from jinja2 import Environment, FileSystemLoader, Template
from .types import SnowflakeResourceT


def camel_case_to_snake_case(text: str) -> str:
    """CamelCase文字列をsnake_case文字列に変更する"""
    return re.sub("(?<!^)(?=[A-Z])", "_", text).lower()


def snake_case_to_camel_case(text: str) -> str:
    """snake_case文字列をCamelCase文字列に変更する"""
    words = text.split("_")
    lower_words = [word.lower() for word in words]
    camel_words = [word.capitalize() for word in lower_words]
    return "".join(camel_words)


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def get_template(template_path: str) -> Template:
    env = Environment(loader=FileSystemLoader("./data"))
    env.filters["to_json"] = to_json
    return env.get_template(template_path)


def get_resource_type_name(resource: SnowflakeResourceT) -> str:
    class_name = getattr(type(resource), "__name__")
    return camel_case_to_snake_case(class_name)


def dict_factory_without_none(items: List[Tuple[str, Any]]) -> dict[Any, Any]:
    """(k, v)のリストを辞書に変換する。値がNoneのものは取り入れない"""
    return {k: v for [k, v] in items if not v is None}


def render_resource(
    resource_type_name: str, resource_name: str, resource: SnowflakeResourceT
) -> str:
    template = get_template("snowflake_resource.tf.jinja")
    attr = asdict(resource, dict_factory=dict_factory_without_none)
    return template.render(
        resource_type_name=resource_type_name, name=resource_name, attr=attr
    )


def to_bool(s) -> Optional[bool]:
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        return None
