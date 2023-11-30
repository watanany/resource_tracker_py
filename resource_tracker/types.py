import dataclasses
import IPython as ipy
from dataclasses import dataclass, asdict
from operator import add
from functools import partial, reduce
from typing import List, Optional, TypeAlias, Callable, TypeVar
from numbers import Number

ReadOnly: TypeAlias = Optional

SnowflakeResourceT = TypeVar("SnowflakeResourceT", bound="SnowflakeResource")
Num = TypeVar("Num", bound=Number)


@dataclass
class BlockList:
    pass


@dataclass
class BlockSet:
    pass


@dataclass
class Block:
    pass


def dict_except_keys(d, except_keys):
    return dict(((k, v) for [k, v] in d.items() if k not in except_keys))


@dataclass
class SnowflakeResource:
    @staticmethod
    def equals_except(
        r0: SnowflakeResourceT, r1: SnowflakeResourceT, except_keys: List[str]
    ) -> bool:
        """except_keys以外の属性が等しいかどうかを返す"""
        return dict_except_keys(asdict(r0), except_keys) == dict_except_keys(
            asdict(r1), except_keys
        )

    @staticmethod
    def merge_field(
        r0: SnowflakeResourceT, r1: SnowflakeResourceT, key: str, merge: Callable = add
    ) -> SnowflakeResourceT:
        """r0.keyとr1.keyをマージして返す"""
        assert type(r0) == type(r1)
        assert SnowflakeResource.equals_except(r0, r1, [key])

        merged_value = merge(getattr(r0, key), getattr(r1, key))
        return dataclasses.replace(r0, **{key: merged_value})

    @staticmethod
    def band(
        rs: List[SnowflakeResourceT], except_key: str
    ) -> List[List[SnowflakeResourceT]]:
        """except_key以外の属性が等しいrs内の要素をグルーピングする"""
        if len(rs) > 0:
            indice = [
                i
                for [i, r] in enumerate(rs)
                if SnowflakeResource.equals_except(rs[0], r, [except_key])
            ]
            targets = [r for [i, r] in enumerate(rs) if i in indice]
            rest = [r for [i, r] in enumerate(rs) if i not in indice]
            return [targets] + SnowflakeResource.band(rest, except_key=except_key)
        else:
            return []


def merge_resources_by_roles(
    resources: List[SnowflakeResourceT],
) -> List[SnowflakeResourceT]:
    key = "roles"
    bands = SnowflakeResource.band(resources, except_key=key)
    merge_field = partial(SnowflakeResource.merge_field, key=key)
    return [reduce(merge_field, band) for band in bands]


def merge_resources_by_users(
    resources: List[SnowflakeResourceT],
) -> List[SnowflakeResourceT]:
    key = "users"
    bands = SnowflakeResource.band(resources, except_key=key)
    merge_field = partial(SnowflakeResource.merge_field, key=key)
    return [reduce(merge_field, band) for band in bands]


# ----------------------------------------------------------------------
# 以下はgenerate_resource_schemas.pyで生成されたもの
# ----------------------------------------------------------------------


@dataclass
class SnowflakeIntegrationGrant(SnowflakeResource):
    integration_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeUserPublicKeys(SnowflakeResource):
    name: str
    rsa_public_key: Optional[str] = None
    rsa_public_key_2: Optional[str] = None


@dataclass
class SnowflakeExternalTable(SnowflakeResource):
    column: BlockList
    database: str
    file_format: str
    location: str
    name: str
    schema: str
    auto_refresh: Optional[bool] = None
    aws_sns_topic: Optional[str] = None
    comment: Optional[str] = None
    copy_grants: Optional[bool] = None
    partition_by: Optional[list[str]] = None
    pattern: Optional[str] = None
    refresh_on_create: Optional[bool] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeOauthIntegration(SnowflakeResource):
    name: str
    oauth_client: str
    blocked_roles_list: Optional[set[str]] = None
    comment: Optional[str] = None
    enabled: Optional[bool] = None
    oauth_client_type: Optional[str] = None
    oauth_issue_refresh_tokens: Optional[bool] = None
    oauth_redirect_uri: Optional[str] = None
    oauth_refresh_token_validity: Optional[Num] = None
    oauth_use_secondary_roles: Optional[str] = None


@dataclass
class SnowflakePipe(SnowflakeResource):
    copy_statement: str
    database: str
    name: str
    schema: str
    auto_ingest: Optional[bool] = None
    aws_sns_topic_arn: Optional[str] = None
    comment: Optional[str] = None
    error_integration: Optional[str] = None
    integration: Optional[str] = None


@dataclass
class SnowflakeRoleOwnershipGrant(SnowflakeResource):
    on_role_name: str
    to_role_name: str
    current_grants: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None


@dataclass
class SnowflakeStreamGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    stream_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeAccountGrant(SnowflakeResource):
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeNotificationIntegration(SnowflakeResource):
    name: str
    aws_sns_role_arn: Optional[str] = None
    aws_sns_topic_arn: Optional[str] = None
    aws_sqs_arn: Optional[str] = None
    aws_sqs_role_arn: Optional[str] = None
    azure_storage_queue_primary_uri: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    comment: Optional[str] = None
    direction: Optional[str] = None
    enabled: Optional[bool] = None
    gcp_pubsub_subscription_name: Optional[str] = None
    gcp_pubsub_topic_name: Optional[str] = None
    notification_provider: Optional[str] = None
    type: Optional[str] = None


@dataclass
class SnowflakeGrantPrivilegesToRole(SnowflakeResource):
    role_name: str
    all_privileges: Optional[bool] = None
    on_account: Optional[bool] = None
    on_account_object: Optional[BlockList] = None
    on_schema: Optional[BlockList] = None
    on_schema_object: Optional[BlockList] = None
    privileges: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeRowAccessPolicyGrant(SnowflakeResource):
    database_name: str
    row_access_policy_name: str
    schema_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeManagedAccount(SnowflakeResource):
    admin_name: str
    admin_password: str
    name: str
    comment: Optional[str] = None
    type: Optional[str] = None


@dataclass
class SnowflakeExternalTableGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    external_table_name: Optional[str] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeDatabaseGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeScimIntegration(SnowflakeResource):
    name: str
    provisioner_role: str
    scim_client: str
    network_policy: Optional[str] = None


@dataclass
class SnowflakeMaskingPolicyGrant(SnowflakeResource):
    database_name: str
    masking_policy_name: str
    schema_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeResourceMonitorGrant(SnowflakeResource):
    monitor_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeRoleGrants(SnowflakeResource):
    role_name: str
    enable_multiple_grants: Optional[bool] = None
    roles: Optional[set[str]] = None
    users: Optional[set[str]] = None


@dataclass
class SnowflakeTagGrant(SnowflakeResource):
    database_name: str
    schema_name: str
    tag_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeExternalOauthIntegration(SnowflakeResource):
    enabled: bool
    issuer: str
    name: str
    snowflake_user_mapping_attribute: str
    token_user_mapping_claims: set[str]
    type: str
    allowed_roles: Optional[set[str]] = None
    any_role_mode: Optional[str] = None
    audience_urls: Optional[set[str]] = None
    blocked_roles: Optional[set[str]] = None
    comment: Optional[str] = None
    jws_keys_urls: Optional[set[str]] = None
    rsa_public_key: Optional[str] = None
    rsa_public_key_2: Optional[str] = None
    scope_delimiter: Optional[str] = None
    scope_mapping_attribute: Optional[str] = None


@dataclass
class SnowflakeSequenceGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    sequence_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeTableColumnMaskingPolicyApplication(SnowflakeResource):
    column: str
    masking_policy: str
    table: str


@dataclass
class SnowflakeDatabaseRole(SnowflakeResource):
    database: str
    name: str
    comment: Optional[str] = None


@dataclass
class SnowflakeAlert(SnowflakeResource):
    action: str
    condition: str
    database: str
    name: str
    schema: str
    warehouse: str
    alert_schedule: Optional[BlockList] = None
    comment: Optional[str] = None
    enabled: Optional[bool] = None


@dataclass
class SnowflakeTask(SnowflakeResource):
    database: str
    name: str
    schema: str
    sql_statement: str
    after: Optional[list[str]] = None
    allow_overlapping_execution: Optional[bool] = None
    comment: Optional[str] = None
    enabled: Optional[bool] = None
    error_integration: Optional[str] = None
    schedule: Optional[str] = None
    session_parameters: Optional[list[dict[str, str]]] = None
    user_task_managed_initial_warehouse_size: Optional[str] = None
    user_task_timeout_ms: Optional[Num] = None
    warehouse: Optional[str] = None
    when: Optional[str] = None


@dataclass
class SnowflakeDatabase(SnowflakeResource):
    name: str
    comment: Optional[str] = None
    data_retention_time_in_days: Optional[Num] = None
    from_database: Optional[str] = None
    from_replica: Optional[str] = None
    from_share: Optional[list[dict[str, str]]] = None
    is_transient: Optional[bool] = None
    replication_configuration: Optional[BlockList] = None


@dataclass
class SnowflakeProcedureGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    argument_data_types: Optional[list[str]] = None
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    procedure_name: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeWarehouseGrant(SnowflakeResource):
    warehouse_name: str
    enable_multiple_grants: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeResourceMonitor(SnowflakeResource):
    name: str
    credit_quota: Optional[Num] = None
    end_timestamp: Optional[str] = None
    frequency: Optional[str] = None
    notify_triggers: Optional[set[Num]] = None
    notify_users: Optional[set[str]] = None
    set_for_account: Optional[bool] = None
    start_timestamp: Optional[str] = None
    suspend_immediate_trigger: Optional[Num] = None
    suspend_immediate_triggers: Optional[set[Num]] = None
    suspend_trigger: Optional[Num] = None
    suspend_triggers: Optional[set[Num]] = None
    warehouses: Optional[set[str]] = None


@dataclass
class SnowflakeStageGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    stage_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeFileFormat(SnowflakeResource):
    database: str
    format_type: str
    name: str
    schema: str
    allow_duplicate: Optional[bool] = None
    binary_as_text: Optional[bool] = None
    binary_format: Optional[str] = None
    comment: Optional[str] = None
    compression: Optional[str] = None
    date_format: Optional[str] = None
    disable_auto_convert: Optional[bool] = None
    disable_snowflake_data: Optional[bool] = None
    empty_field_as_null: Optional[bool] = None
    enable_octal: Optional[bool] = None
    encoding: Optional[str] = None
    error_on_column_count_mismatch: Optional[bool] = None
    escape: Optional[str] = None
    escape_unenclosed_field: Optional[str] = None
    field_delimiter: Optional[str] = None
    field_optionally_enclosed_by: Optional[str] = None
    file_extension: Optional[str] = None
    ignore_utf8_errors: Optional[bool] = None
    null_if: Optional[list[str]] = None
    preserve_space: Optional[bool] = None
    record_delimiter: Optional[str] = None
    replace_invalid_characters: Optional[bool] = None
    skip_blank_lines: Optional[bool] = None
    skip_byte_order_mark: Optional[bool] = None
    skip_header: Optional[Num] = None
    strip_null_values: Optional[bool] = None
    strip_outer_array: Optional[bool] = None
    strip_outer_element: Optional[bool] = None
    time_format: Optional[str] = None
    timestamp_format: Optional[str] = None
    trim_space: Optional[bool] = None


@dataclass
class SnowflakeFailoverGroupGrant(SnowflakeResource):
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    failover_group_name: Optional[str] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeStream(SnowflakeResource):
    database: str
    name: str
    schema: str
    append_only: Optional[bool] = None
    comment: Optional[str] = None
    insert_only: Optional[bool] = None
    on_stage: Optional[str] = None
    on_table: Optional[str] = None
    on_view: Optional[str] = None
    show_initial_rows: Optional[bool] = None


@dataclass
class SnowflakeApiIntegration(SnowflakeResource):
    api_allowed_prefixes: list[str]
    api_provider: str
    name: str
    api_aws_role_arn: Optional[str] = None
    api_blocked_prefixes: Optional[list[str]] = None
    api_gcp_service_account: Optional[str] = None
    api_key: Optional[str] = None
    azure_ad_application_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    comment: Optional[str] = None
    enabled: Optional[bool] = None
    google_audience: Optional[str] = None


@dataclass
class SnowflakePasswordPolicy(SnowflakeResource):
    database: str
    name: str
    schema: str
    comment: Optional[str] = None
    if_not_exists: Optional[bool] = None
    lockout_time_mins: Optional[Num] = None
    max_age_days: Optional[Num] = None
    max_length: Optional[Num] = None
    max_retries: Optional[Num] = None
    min_length: Optional[Num] = None
    min_lower_case_chars: Optional[Num] = None
    min_numeric_chars: Optional[Num] = None
    min_special_chars: Optional[Num] = None
    min_upper_case_chars: Optional[Num] = None
    or_replace: Optional[bool] = None


@dataclass
class SnowflakeSchema(SnowflakeResource):
    database: str
    name: str
    comment: Optional[str] = None
    data_retention_days: Optional[Num] = None
    is_managed: Optional[bool] = None
    is_transient: Optional[bool] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeUserGrant(SnowflakeResource):
    privilege: str
    user_name: str
    enable_multiple_grants: Optional[bool] = None
    roles: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeUserOwnershipGrant(SnowflakeResource):
    on_user_name: str
    to_role_name: str
    current_grants: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None


@dataclass
class SnowflakeTagMaskingPolicyAssociation(SnowflakeResource):
    masking_policy_id: str
    tag_id: str


@dataclass
class SnowflakeMaterializedView(SnowflakeResource):
    database: str
    name: str
    schema: str
    statement: str
    warehouse: str
    comment: Optional[str] = None
    is_secure: Optional[bool] = None
    or_replace: Optional[bool] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeStorageIntegration(SnowflakeResource):
    name: str
    storage_allowed_locations: list[str]
    storage_provider: str
    azure_tenant_id: Optional[str] = None
    comment: Optional[str] = None
    enabled: Optional[bool] = None
    storage_aws_object_acl: Optional[str] = None
    storage_aws_role_arn: Optional[str] = None
    storage_blocked_locations: Optional[list[str]] = None
    type: Optional[str] = None


@dataclass
class SnowflakeObjectParameter(SnowflakeResource):
    key: str
    value: str
    object_identifier: Optional[BlockList] = None
    object_type: Optional[str] = None
    on_account: Optional[bool] = None


@dataclass
class SnowflakeNetworkPolicyAttachment(SnowflakeResource):
    network_policy_name: str
    set_for_account: Optional[bool] = None
    users: Optional[set[str]] = None


@dataclass
class SnowflakeSamlIntegration(SnowflakeResource):
    name: str
    saml2_issuer: str
    saml2_provider: str
    saml2_sso_url: str
    saml2_x509_cert: str
    enabled: Optional[bool] = None
    saml2_enable_sp_initiated: Optional[bool] = None
    saml2_force_authn: Optional[bool] = None
    saml2_post_logout_redirect_url: Optional[str] = None
    saml2_requested_nameid_format: Optional[str] = None
    saml2_sign_request: Optional[bool] = None
    saml2_snowflake_acs_url: Optional[str] = None
    saml2_snowflake_issuer_url: Optional[str] = None
    saml2_snowflake_x509_cert: Optional[str] = None
    saml2_sp_initiated_login_page_label: Optional[str] = None


@dataclass
class SnowflakeFileFormatGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    file_format_name: Optional[str] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeSequence(SnowflakeResource):
    database: str
    name: str
    schema: str
    comment: Optional[str] = None
    increment: Optional[Num] = None


@dataclass
class SnowflakeRole(SnowflakeResource):
    name: str
    comment: Optional[str] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeExternalFunction(SnowflakeResource):
    api_integration: str
    database: str
    name: str
    return_behavior: str
    return_type: str
    schema: str
    url_of_proxy_and_resource: str
    arg: Optional[BlockList] = None
    comment: Optional[str] = None
    compression: Optional[str] = None
    context_headers: Optional[list[str]] = None
    header: Optional[BlockSet] = None
    max_batch_rows: Optional[Num] = None
    null_input_behavior: Optional[str] = None
    request_translator: Optional[str] = None
    response_translator: Optional[str] = None
    return_null_allowed: Optional[bool] = None


@dataclass
class SnowflakeRowAccessPolicy(SnowflakeResource):
    database: str
    name: str
    row_access_expression: str
    schema: str
    signature: list[dict[str, str]]
    comment: Optional[str] = None


@dataclass
class SnowflakeTableConstraint(SnowflakeResource):
    columns: list[str]
    name: str
    table_id: str
    type: str
    comment: Optional[str] = None
    deferrable: Optional[bool] = None
    enable: Optional[bool] = None
    enforced: Optional[bool] = None
    foreign_key_properties: Optional[BlockList] = None
    initially: Optional[str] = None
    rely: Optional[bool] = None
    validate: Optional[bool] = None


@dataclass
class SnowflakeFunctionGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    argument_data_types: Optional[list[str]] = None
    enable_multiple_grants: Optional[bool] = None
    function_name: Optional[str] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeStage(SnowflakeResource):
    database: str
    name: str
    schema: str
    aws_external_id: Optional[str] = None
    comment: Optional[str] = None
    copy_options: Optional[str] = None
    credentials: Optional[str] = None
    directory: Optional[str] = None
    encryption: Optional[str] = None
    file_format: Optional[str] = None
    snowflake_iam_user: Optional[str] = None
    storage_integration: Optional[str] = None
    tag: Optional[BlockList] = None
    url: Optional[str] = None


@dataclass
class SnowflakeEmailNotificationIntegration(SnowflakeResource):
    allowed_recipients: set[str]
    enabled: bool
    name: str
    comment: Optional[str] = None


@dataclass
class SnowflakeTaskGrant(SnowflakeResource):
    database_name: str
    roles: set[str]
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    schema_name: Optional[str] = None
    task_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeView(SnowflakeResource):
    database: str
    name: str
    schema: str
    statement: str
    comment: Optional[str] = None
    copy_grants: Optional[bool] = None
    is_secure: Optional[bool] = None
    or_replace: Optional[bool] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeShare(SnowflakeResource):
    name: str
    accounts: Optional[list[str]] = None
    comment: Optional[str] = None


@dataclass
class SnowflakeTableGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    table_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeNetworkPolicy(SnowflakeResource):
    allowed_ip_list: set[str]
    name: str
    blocked_ip_list: Optional[set[str]] = None
    comment: Optional[str] = None


@dataclass
class SnowflakeAccountParameter(SnowflakeResource):
    key: str
    value: str


@dataclass
class SnowflakeAccount(SnowflakeResource):
    admin_name: str
    edition: str
    email: str
    name: str
    admin_password: Optional[str] = None
    admin_rsa_public_key: Optional[str] = None
    comment: Optional[str] = None
    first_name: Optional[str] = None
    grace_period_in_days: Optional[Num] = None
    last_name: Optional[str] = None
    must_change_password: Optional[bool] = None
    region: Optional[str] = None
    region_group: Optional[str] = None


@dataclass
class SnowflakeAccountPasswordPolicyAttachment(SnowflakeResource):
    password_policy: str


@dataclass
class SnowflakePipeGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    on_future: Optional[bool] = None
    pipe_name: Optional[str] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    schema_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeMaskingPolicy(SnowflakeResource):
    database: str
    masking_expression: str
    name: str
    return_data_type: str
    schema: str
    signature: BlockList
    comment: Optional[str] = None
    exempt_other_policies: Optional[bool] = None
    if_not_exists: Optional[bool] = None
    or_replace: Optional[bool] = None


@dataclass
class SnowflakeProcedure(SnowflakeResource):
    database: str
    name: str
    return_type: str
    schema: str
    statement: str
    arguments: Optional[BlockList] = None
    comment: Optional[str] = None
    execute_as: Optional[str] = None
    handler: Optional[str] = None
    imports: Optional[list[str]] = None
    language: Optional[str] = None
    null_input_behavior: Optional[str] = None
    packages: Optional[list[str]] = None
    return_behavior: Optional[str] = None
    runtime_version: Optional[str] = None


@dataclass
class SnowflakeSessionParameter(SnowflakeResource):
    key: str
    value: str
    on_account: Optional[bool] = None
    user: Optional[str] = None


@dataclass
class SnowflakeTag(SnowflakeResource):
    database: str
    name: str
    schema: str
    allowed_values: Optional[list[str]] = None
    comment: Optional[str] = None


@dataclass
class SnowflakeMaterializedViewGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    materialized_view_name: Optional[str] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeSchemaGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeViewGrant(SnowflakeResource):
    database_name: str
    enable_multiple_grants: Optional[bool] = None
    on_all: Optional[bool] = None
    on_future: Optional[bool] = None
    privilege: Optional[str] = None
    revert_ownership_to_role_name: Optional[str] = None
    roles: Optional[set[str]] = None
    schema_name: Optional[str] = None
    shares: Optional[set[str]] = None
    view_name: Optional[str] = None
    with_grant_option: Optional[bool] = None


@dataclass
class SnowflakeTagAssociation(SnowflakeResource):
    object_identifier: BlockList
    object_type: str
    tag_id: str
    tag_value: str
    object_name: Optional[str] = None
    skip_validation: Optional[bool] = None
    timeouts: Optional[Block] = None


@dataclass
class SnowflakeWarehouse(SnowflakeResource):
    name: str
    auto_resume: Optional[bool] = None
    auto_suspend: Optional[Num] = None
    comment: Optional[str] = None
    enable_query_acceleration: Optional[bool] = None
    initially_suspended: Optional[bool] = None
    max_cluster_count: Optional[Num] = None
    max_concurrency_level: Optional[Num] = None
    min_cluster_count: Optional[Num] = None
    query_acceleration_max_scale_factor: Optional[Num] = None
    resource_monitor: Optional[str] = None
    scaling_policy: Optional[str] = None
    statement_queued_timeout_in_seconds: Optional[Num] = None
    statement_timeout_in_seconds: Optional[Num] = None
    wait_for_provisioning: Optional[bool] = None
    warehouse_size: Optional[str] = None
    warehouse_type: Optional[str] = None


@dataclass
class SnowflakeUser(SnowflakeResource):
    name: str
    comment: Optional[str] = None
    default_namespace: Optional[str] = None
    default_role: Optional[str] = None
    default_secondary_roles: Optional[set[str]] = None
    default_warehouse: Optional[str] = None
    disabled: Optional[bool] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login_name: Optional[str] = None
    must_change_password: Optional[bool] = None
    password: Optional[str] = None
    rsa_public_key: Optional[str] = None
    rsa_public_key_2: Optional[str] = None


@dataclass
class SnowflakeFailoverGroup(SnowflakeResource):
    name: str
    allowed_accounts: Optional[set[str]] = None
    allowed_databases: Optional[set[str]] = None
    allowed_integration_types: Optional[set[str]] = None
    allowed_shares: Optional[set[str]] = None
    from_replica: Optional[BlockList] = None
    ignore_edition_check: Optional[bool] = None
    object_types: Optional[set[str]] = None
    replication_schedule: Optional[BlockList] = None


@dataclass
class SnowflakeTable(SnowflakeResource):
    column: BlockList
    database: str
    name: str
    schema: str
    change_tracking: Optional[bool] = None
    cluster_by: Optional[list[str]] = None
    comment: Optional[str] = None
    data_retention_days: Optional[Num] = None
    data_retention_time_in_days: Optional[Num] = None
    primary_key: Optional[BlockList] = None
    tag: Optional[BlockList] = None


@dataclass
class SnowflakeFunction(SnowflakeResource):
    database: str
    name: str
    return_type: str
    schema: str
    statement: str
    arguments: Optional[BlockList] = None
    comment: Optional[str] = None
    handler: Optional[str] = None
    imports: Optional[list[str]] = None
    is_secure: Optional[bool] = None
    language: Optional[str] = None
    null_input_behavior: Optional[str] = None
    packages: Optional[list[str]] = None
    return_behavior: Optional[str] = None
    runtime_version: Optional[str] = None
    target_path: Optional[str] = None
