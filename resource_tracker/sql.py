import pandas as pd
import IPython as ipy
from datetime import datetime
from typing import Optional
from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import SnowflakeCursor
from .types import *
from .utils import to_bool


def fetch_pandas_all(cursor: SnowflakeCursor) -> pd.DataFrame:
    """SQLを実行して、結果をpandas.DataFrameで返す(cursor起点)"""
    data = cursor.fetchall()
    try:
        return pd.DataFrame(
            data, columns=[d.name for d in cursor.description], dtype=str
        )
    except ValueError as e:
        ipy.embed()


def pd_execute(conn: SnowflakeConnection, sql: str) -> pd.DataFrame:
    """SQLを実行して、結果をpandas.DataFrameで返す"""
    cur = conn.cursor()
    cur.execute(sql)
    return fetch_pandas_all(cur)


def fetch_warehouses(conn: SnowflakeConnection) -> List[SnowflakeWarehouse]:
    """Snowflakeのウェアハウス一覧を取得する"""
    df = pd_execute(conn, "show warehouses in account")
    return [
        SnowflakeWarehouse(
            name=row.name,
            comment=row.comment,
            warehouse_size=row.size,
            max_concurrency_level=8,
            statement_queued_timeout_in_seconds=0,
            statement_timeout_in_seconds=172800,
        )
        for row in df.itertuples()
    ]


def fetch_databases(conn: SnowflakeConnection) -> List[SnowflakeDatabase]:
    """Snowflakeのデータベース一覧を取得する"""
    df = pd_execute(conn, "show databases in account")
    return [
        SnowflakeDatabase(name=row.name, comment=row.comment) for row in df.itertuples()
    ]


def fetch_schemata(conn: SnowflakeConnection) -> List[SnowflakeSchema]:
    """Snowflakeのスキーマ一覧を取得する"""
    df = pd_execute(conn, "show schemas in account")
    return [
        SnowflakeSchema(database=row.database_name, name=row.name, comment=row.comment)
        for row in df.itertuples()
    ]


def fetch_stages(conn: SnowflakeConnection) -> List[SnowflakeStage]:
    """Snowflakeのステージ一覧を取得する"""
    df = pd_execute(conn, "show stages in account")
    return [
        SnowflakeStage(
            database=row.database_name,
            schema=row.schema_name,
            name=row.name,
            url=row.url,
            comment=row.comment,
        )
        for row in df.itertuples()
    ]


def fetch_roles(conn: SnowflakeConnection) -> List[SnowflakeRole]:
    """Snowflakeのロール一覧を取得する"""
    df = pd_execute(conn, "show roles in account")
    return [
        SnowflakeRole(name=row.name, comment=row.comment) for row in df.itertuples()
    ]


def fetch_users(conn: SnowflakeConnection) -> List[SnowflakeUser]:
    """Snowflakeのユーザー一覧を取得する"""
    df = pd_execute(conn, "show users in account")
    return [
        SnowflakeUser(
            email=row.email, name=row.name, default_warehouse=row.default_warehouse
        )
        for row in df.itertuples()
    ]


def get_property(df: pd.DataFrame, name: str) -> Optional[dict]:
    """補助関数: get-property-valueの内部で使用される"""
    df2 = df[df.get("property") == name].reset_index(drop=True)
    try:
        return df2.loc[0][slice(None)].to_dict()
    except KeyError:
        return None


def get_property_value(df: pd.DataFrame, name: str) -> Optional[str]:
    """補助関数"""
    property = get_property(df, name)
    return property["property_value"] if property is not None else None


def fetch_storage_integrations(
    conn: SnowflakeConnection,
) -> List[SnowflakeStorageIntegration]:
    """Snowflakeのストレージ統合一覧を取得する"""
    df = pd_execute(conn, "show storage integrations")
    resources = []

    for p in df.itertuples():
        df2 = pd_execute(conn, f"desc storage integration {p.name}")
        storage_blocked_locations_str = get_property_value(
            df2, "STORAGE_BLOCKED_LOCATIONS"
        )
        resource = SnowflakeStorageIntegration(
            name=p.name,
            storage_allowed_locations=get_property_value(
                df2, "STORAGE_ALLOWED_LOCATIONS"
            ).split(","),
            storage_provider=get_property_value(df2, "STORAGE_PROVIDER"),
            comment=get_property_value(df2, "COMMENT"),
            enabled=get_property_value(df2, "ENABLED") == "true",
            storage_blocked_locations=storage_blocked_locations_str.split(",")
            if storage_blocked_locations_str != ""
            else None,
        )
        resources.append(resource)

    return resources


def get_notification_integration_type(typ: str) -> str:
    if typ.startswith("QUEUE - "):
        return "QUEUE"
    else:
        raise ValueError(f"Not supported notification integration type: '{typ}'")


def fetch_notification_integrations(
    conn: SnowflakeConnection,
) -> List[SnowflakeNotificationIntegration]:
    """Snowflakeの通知統合一覧を取得する"""
    df = pd_execute(conn, "show notification integrations")
    resources = []

    for p in df.itertuples():
        df2 = pd_execute(conn, f"desc notification integration {p.name}")
        resource = SnowflakeNotificationIntegration(
            name=p.name,
            aws_sns_role_arn=get_property_value(df2, "AWS_SNS_ROLE_ARN"),
            aws_sns_topic_arn=get_property_value(df2, "AWS_SNS_TOPIC_ARN"),
            comment=get_property_value(df2, "COMMENT"),
            direction=get_property_value(df2, "DIRECTION"),
            enabled=get_property_value(df2, "ENABLED") == "true",
            gcp_pubsub_subscription_name=get_property_value(
                df2, "GCP_PUBSUB_SUBSCRIPTION_NAME"
            ),
            notification_provider=get_property_value(df2, "NOTIFICATION_PROVIDER"),
            type=get_notification_integration_type(p.type),
        )
        resources.append(resource)

    return resources


def fetch_database_grants(conn: SnowflakeConnection) -> List[SnowflakeDatabaseGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'DATABASE' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeDatabaseGrant(
            database_name=p.NAME,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_file_formats(conn: SnowflakeConnection) -> List[SnowflakeFileFormat]:
    df = pd_execute(conn, "show file formats in account")
    resources = []

    for p in df.itertuples():
        if p.name != "MYPARQUET":
            df2 = pd_execute(conn, f"desc file format {p.name}")
            resource = SnowflakeFileFormat(
                database=p.database_name,
                format_type=p.type,
                name=p.name,
                schema=p.schema_name,
                allow_duplicate=get_property_value(df2, "ALLOW_DUPLICATE"),
                binary_format=get_property_value(df2, "BINARY_FORMAT"),
                compression=get_property_value(df2, "COMPRESSION"),
                date_format=get_property_value(df2, "DATE_FORMAT"),
                encoding=get_property_value(df2, "ENCODING"),
                escape=get_property_value(df2, "ESCAPE"),
                escape_unenclosed_field=get_property_value(
                    df2, "ESCAPE_UNENCLOSED_FIELD"
                ),
                field_delimiter=get_property_value(df2, "FIELD_DELIMITER"),
                field_optionally_enclosed_by=get_property_value(
                    df2, "FIELD_OPTIONALLY_ENCLOSED_BY"
                ),
                file_extension=get_property_value(df2, "FILE_EXTENSION"),
                null_if=get_property_value(df2, "NULL_IF").split(","),
                record_delimiter=get_property_value(df2, "RECORD_DELIMITER"),
                skip_blank_lines=get_property_value(df2, "SKIP_BLANK_LINES"),
                skip_byte_order_mark=get_property_value(df2, "SKIP_BYTE_ORDER_MARK"),
                time_format=get_property_value(df2, "TIME_FORMAT"),
                timestamp_format=get_property_value(df2, "TIMESTAMP_FORMAT"),
                trim_space=get_property_value(df2, "TRIM_SPACE"),
            )
            resources.append(resource)

    return resources


def fetch_file_format_grants(
    conn: SnowflakeConnection,
) -> List[SnowflakeFileFormatGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'FILE FORMAT' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeFileFormatGrant(
            database_name=p.TABLE_CATALOG,
            roles=[p.GRANTEE_NAME],
            file_format_name=p.NAME,
            schema_name=p.TABLE_SCHEMA,
            privilege=p.PRIVILEGE,
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_integration_grants(
    conn: SnowflakeConnection,
) -> List[SnowflakeIntegrationGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'INTEGRATION' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeIntegrationGrant(
            integration_name=p.NAME,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def convert_timestamp_format(timestamp_str: str) -> str:
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S%z")
    return timestamp.strftime("%Y-%m-%dT%H:%M:%S%Z")


def fetch_resource_monitors(
    conn: SnowflakeConnection,
) -> List[SnowflakeResourceMonitor]:
    df = pd_execute(conn, "show resource monitors in account")
    return [
        SnowflakeResourceMonitor(
            name=p.name,
            credit_quota=p.credit_quota,
            end_timestamp=p.end_time,
            frequency=p.frequency,
            notify_triggers=None,
            notify_users=p.notify_users.split(",") if p.notify_users != "" else None,
            start_timestamp=convert_timestamp_format(p.start_time),
        )
        for p in df.itertuples()
    ]


def fetch_resource_monitor_grants(
    conn: SnowflakeConnection,
) -> List[SnowflakeResourceMonitorGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'RESOURCE MONITOR' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeResourceMonitorGrant(
            monitor_name=p.NAME,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_role_grants(conn: SnowflakeConnection) -> List[SnowflakeRoleGrants]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'ROLE' and granted_to = 'ROLE' and privilege = 'USAGE' and deleted_on is null",
    )
    resources_to_roles = [
        SnowflakeRoleGrants(
            role_name=p.NAME, roles=[p.GRANTEE_NAME], enable_multiple_grants=True
        )
        for p in df.itertuples()
    ]
    merged_for_roles = merge_resources_by_roles(resources_to_roles)
    df = pd_execute(conn, "select * from snowflake.account_usage.grants_to_users")
    resources_to_users = [
        SnowflakeRoleGrants(
            role_name=p.ROLE, users=[p.GRANTEE_NAME], enable_multiple_grants=True
        )
        for p in df.itertuples()
    ]
    merged_for_users = merge_resources_by_users(resources_to_users)
    return merged_for_roles + merged_for_users


def fetch_schema_grants(conn: SnowflakeConnection) -> List[SnowflakeSchemaGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'SCHEMA' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeSchemaGrant(
            database_name=p.TABLE_CATALOG,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            schema_name=p.TABLE_SCHEMA,
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_stage_grants(conn: SnowflakeConnection) -> List[SnowflakeStageGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'STAGE' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeStageGrant(
            database_name=p.TABLE_CATALOG,
            roles=[p.GRANTEE_NAME],
            privilege=p.PRIVILEGE,
            schema_name=p.TABLE_SCHEMA,
            stage_name=p.NAME,
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_warehouse_grants(conn: SnowflakeConnection) -> List[SnowflakeWarehouseGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'WAREHOUSE' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeWarehouseGrant(
            warehouse_name=p.NAME,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_table_grants(conn: SnowflakeConnection) -> List[SnowflakeTableGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'TABLE' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeTableGrant(
            database_name=p.TABLE_CATALOG,
            privilege=p.PRIVILEGE,
            roles=[p.GRANTEE_NAME],
            schema_name=p.TABLE_SCHEMA,
            table_name=p.NAME,
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_tasks(conn: SnowflakeConnection) -> List[SnowflakeTask]:
    df = pd_execute(conn, "show tasks in account")
    return [
        SnowflakeTask(
            database=p.database_name,
            name=p.name,
            schema=p.schema_name,
            sql_statement=p.definition,
            allow_overlapping_execution=p.allow_overlapping_execution,
            comment=p.comment,
            error_integration=p.error_integration
            if p.error_integration is not None
            else None,
            schedule=p.schedule,
            warehouse=p.warehouse,
        )
        for p in df.itertuples()
    ]


def fetch_task_grants(conn: SnowflakeConnection) -> List[SnowflakeTaskGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'TASK' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeTaskGrant(
            database_name=p.TABLE_CATALOG,
            roles=[p.GRANTEE_NAME],
            privilege=p.PRIVILEGE,
            schema_name=p.TABLE_SCHEMA,
            task_name=p.NAME,
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)


def fetch_user_grants(conn: SnowflakeConnection) -> List[SnowflakeUserGrant]:
    df = pd_execute(
        conn,
        "select * from snowflake.account_usage.grants_to_roles where granted_on = 'USER' and granted_to = 'ROLE' and deleted_on is null",
    )
    resources = [
        SnowflakeUserGrant(
            privilege=p.PRIVILEGE,
            user_name=p.NAME,
            roles=[p.GRANTEE_NAME],
            with_grant_option=to_bool(p.GRANT_OPTION),
        )
        for p in df.itertuples()
    ]
    return merge_resources_by_roles(resources)
