import os
import json
import re
import cryptography.hazmat.primitives.serialization as serialization
import snowflake.connector
import resource_tracker as rt
import IPython as ipy
from os.path import expanduser
from typing import List, TextIO
from uuid import uuid4
from pluralizer import Pluralizer
from cryptography.hazmat.backends import default_backend
from resource_tracker import *

resource_id_attr_names_map = {
    "database": ["name"],
    "database_grant": [
        "database_name",
        "privilege",
        "with_grant_option",
        "roles",
        "shares",
    ],
    "file_format": ["database", "schema", "name"],
    "file_format_grant": [
        "database_name",
        "schema_name",
        "file_format_name",
        "privilege",
        "with_grant_option",
        "on_future",
        "on_all",
        "roles",
    ],
    "integration_grant": [
        "integration_name",
        "privilege",
        "with_grant_option",
        "roles",
    ],
    "notification_integration": ["name"],
    "resource_monitor": ["name"],
    "resource_monitor_grant": [
        "monitor_name",
        "privilege",
        "with_grant_option",
        "roles",
    ],
    "role": ["name"],
    "role_grants": ["role_name", "roles", "users"],
    "schema": ["database", "name"],
    "schema_grant": [
        "database_name",
        "schema_name",
        "privilege",
        "with_grant_option",
        "on_future",
        "on_all",
        "roles",
        "shares",
    ],
    "stage": ["database", "schema", "name"],
    "stage_grant": [
        "database_name",
        "schema_name",
        "stage_name",
        "privilege",
        "with_grant_option",
        "on_future",
        "on_all",
        "roles",
    ],
    "storage_integration": ["name"],
    "task": ["database", "schema", "name"],
    "task_grant": [
        "database_name",
        "schema_name",
        "task_name",
        "privilege",
        "with_grant_option",
        "on_future",
        "on_all",
        "roles",
    ],
    "user": ["name"],
    "user_grant": [
        "user_name",
        "privilege",
        "with_grant_option",
        "roles",
    ],
    "warehouse": ["name"],
    "warehouse_grant": [
        "warehouse_name",
        "privilege",
        "with_grant_option",
        "roles",
    ],
}
imported_resource_types = [
    "database",
    "database_grant",
    "file_format",
    "file_format_grant",
    "integration_grant",
    "notification_integration",
    "resource_monitor",
    "resource_monitor_grant",
    "role",
    "role_grants",
    "schema",
    "schema_grant",
    "stage",
    "stage_grant",
    "storage_integration",
    "task",
    "task_grant",
    "user",
    "user_grant",
    "warehouse",
    "warehouse_grant",
]
PRIVATE_KEY_PATH = expanduser("~/.ssh/snowflake_tf_snow_key.p8")


def to_tf_resource_name(resource_name):
    return f"snowflake_{resource_name}"


def get_resource_name(resource_type_name: str, resource: SnowflakeResourceT) -> str:
    return (
        resource.name
        if resource_type_name not in ["stage", "file_format", "schema"]
        and hasattr(resource, "name")
        else "a_" + str(uuid4()).replace("-", "_")
    )


def write_resources(
    file: TextIO,
    resource_type_name: str,
    resource_names: List[str],
    resources: List[SnowflakeResourceT],
) -> None:
    tf_resource_type_name = to_tf_resource_name(resource_type_name)
    for [resource_name, resource] in zip(resource_names, resources):
        try:
            print(
                render_resource(tf_resource_type_name, resource_name, resource),
                file=file,
            )
            print("", file=file)
        except TypeError as e:
            ipy.embed()


def write_import_commands(
    w: TextIO,
    resource_type_name: str,
    resource_names: List[str],
    resources: List[SnowflakeResourceT],
) -> None:
    tf_resource_type_name = to_tf_resource_name(resource_type_name)
    for [resource_name, resource] in zip(resource_names, resources):
        resource_id_attr_names = resource_id_attr_names_map[resource_type_name]
        attrs = [getattr(resource, attr_name) for attr_name in resource_id_attr_names]

        resource_id_attrs = []
        for attr in attrs:
            if attr is None:
                resource_id_attrs.append("false")
            elif isinstance(attr, list):
                resource_id_attrs.append(",".join(attr))
            elif isinstance(attr, str):
                resource_id_attrs.append(attr)
            else:
                resource_id_attrs.append(json.dumps(attr))

        resource_id = "|".join(resource_id_attrs)
        print(
            f"terraform import '{tf_resource_type_name}.{resource_name}' '{resource_id}'",
            file=w,
        )


def main():
    with open(PRIVATE_KEY_PATH, "rb") as r:
        p_key = serialization.load_pem_private_key(
            r.read(), password=None, backend=default_backend()
        )

    conn = snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        private_key=p_key,
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WS"),
        database=os.environ.get("SNOWFLAKE_DATABASE"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC"),
        role=os.environ["SNOWFLAKE_ROLE"],
    )

    pluralizer = Pluralizer()
    fetchers = [
        getattr(rt, f"fetch_{typs}")
        for typ in imported_resource_types
        for typs in (pluralizer.pluralize(typ),)
    ]
    fetch_pat = re.compile("fetch_(.*)")
    import_w = open(f"outputs/import.sh", mode="w", encoding="utf-8")

    for [resource_type_name, fetch] in zip(imported_resource_types, fetchers):
        resources = fetch(conn)
        resource_names = [get_resource_name(resource_type_name, r) for r in resources]

        with open(f"outputs/{resource_type_name}.tf", mode="w", encoding="utf-8") as w:
            write_resources(w, resource_type_name, resource_names, resources)

        write_import_commands(import_w, resource_type_name, resource_names, resources)


if __name__ == "__main__":
    main()
