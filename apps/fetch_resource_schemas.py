import sys
import re
import json
import requests
import IPython as ipy
from functools import reduce
from operator import add
from dataclasses import dataclass, asdict
from copy import deepcopy
from typing import Any, List, Set, Optional
from toolz import first
from bs4 import BeautifulSoup, Tag

resource_index_url = "https://github.com/Snowflake-Labs/terraform-provider-snowflake/tree/main/docs/resources"
resource_detail_url_format = "https://github.com/Snowflake-Labs/terraform-provider-snowflake/blob/main/docs/resources/{}.md"

type_pat = re.compile("^\\s*\\(([^)]+)\\)")
max_pat = re.compile("Max:\\s*(\\d+)")
min_pat = re.compile("Min:\\s*(\\d+)")


@dataclass
class ResourceAttribute:
    name: str
    type: str
    options: Optional[List[str]] = None
    sensitive: bool = False
    required: bool = False
    optional: bool = False
    read_only: bool = False
    deprecated: bool = False
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Resource:
    name: str
    attributes: List[ResourceAttribute]


def fetch_resource_name_set() -> Set[str]:
    res = requests.get(resource_index_url)
    json = res.json()
    items = json["payload"]["tree"]["items"]
    return {
        file_name.replace(".md", "")
        for item in items
        for file_name in (item["name"],)
        if file_name.endswith(".md")
    }


def has_direct_child_tag(tag: Tag, child_tag_name: str) -> bool:
    return any([child for child in tag.children if child.name == child_tag_name])


def extract_li_tags(soup: BeautifulSoup, css_selector: str) -> List[Tag]:
    h3 = soup.select_one(css_selector)
    ul = h3.find_next("ul")
    lis = ul.select("li")
    return [li for li in lis if has_direct_child_tag(li, "code")]


def get_min_option(options: List[str]) -> int:
    matches = [m for opt in options for m in (min_pat.search(opt),) if not m is None]
    return int(first(matches).group(1)) if len(matches) == 1 else None


def get_max_option(options: List[str]) -> int:
    matches = [m for opt in options for m in (max_pat.search(opt),) if not m is None]
    return int(matches[0].group(1)) if len(matches) == 1 else None


def extract_resource_attribute(
    li: Tag, required: bool = False, optional: bool = False, read_only: bool = False
) -> ResourceAttribute:
    li = deepcopy(li)

    code = li.select_one("code")
    code.extract()

    m = type_pat.search(li.text)
    infos = [p.strip() for p in m.group(1).split(",")]
    type = infos[0]
    options = infos[slice(1, None)]

    return ResourceAttribute(
        name=code.text,
        type=type,
        sensitive="Sensitive" in infos,
        options=options if len(options) > 0 else None,
        required=required,
        optional=optional,
        read_only=read_only,
        deprecated="Deprecated" in infos,
        min=get_min_option(options),
        max=get_max_option(options),
    )


def fetch_resource(resource_name: str) -> Resource:
    res = requests.get(resource_detail_url_format.format(resource_name))
    json = res.json()
    html = json["payload"]["blob"]["richText"]
    soup = BeautifulSoup(html, "html.parser")
    lis_required = extract_li_tags(soup, "#user-content-required")
    lis_optional = extract_li_tags(soup, "#user-content-optional")
    lis_read_only = extract_li_tags(soup, "#user-content-read-only")
    required_attributes = (
        [extract_resource_attribute(li, required=True) for li in lis_required]
        if not lis_required is None
        else None
    )
    optional_attributes = (
        [extract_resource_attribute(li, optional=True) for li in lis_optional]
        if not lis_optional is None
        else None
    )
    read_only_attributes = (
        [extract_resource_attribute(li, read_only=True) for li in lis_read_only]
        if not lis_read_only is None
        else None
    )
    attributes = reduce(
        add,
        [
            attrs if attrs is not None else []
            for attrs in [
                required_attributes,
                optional_attributes,
                read_only_attributes,
            ]
        ],
    )
    resource = Resource(name=resource_name, attributes=attributes)
    return resource


def main():
    resource_name_set = fetch_resource_name_set()
    for resource_name in list(resource_name_set)[slice(None, None)]:
        resource = fetch_resource(resource_name)
        d = asdict(resource)
        print(json.dumps(d, ensure_ascii=False))


if __name__ == "__main__":
    main()
