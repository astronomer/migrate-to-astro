Airflow V2 Upgrader Overview
========
This project aims to automate common tasks when upgrading DAGs from Airflow 1 to Airflow 2, 
making use of [RedBaron](https://redbaron.readthedocs.io/en/latest/) to parse and manipulate the Python syntax tree.

Running this against 15 customer-provided Airflow DAGs completely upgraded 8 DAGs without user intervention, while some of the upgraded DAGs failed to import due to missing Connections and Variables.


How to Use
================
The AirflowV2Upgrader class in ./airflow_v2_upgrader.py performs the upgrade by:
1. Builds an import map for classes in `airflow.hooks`, `airflow.operators`, `airflow.sensors`, and `airflow.providers`, which maps the classes to the current Airflow version import path.
2. Modifies Python files in a DAG directory to update
    * Imports
    * DAG access controls
    * XCOM push
    * XCOM pull
3. Writes updated DAG to either the same DAG directory or a parameter output directory with `_upgraded` added to the filename.

The script is currently configure to run against `./dags` and output in `./dags/upgraded` as shown below
```
upgrader = AirflowV2Upgrader(dag_dir="dags/", out_dir="dags/upgraded/")
upgrader.generate_import_map()
upgrader.upgrade_dag_files()
```

## Caveats

In order to load the Airflow import map, Airflow provider packages must be installed. There are often cross-dependencies within Airflow providers (eg `airflow.operators.s3_to_hive_operator` required the Hive provider), so make sure the `requirements.txt` file includes all necessary .

The script currently tries to correct imports that do not need to be changed going from Airflow 1 to 2, and logging does not include which files are currently being acted against.

The code uses Astronomer-centric opinions, like removing DAG-level RBAC. In the future, I'd rather have these decisions configurable at runtime, as well as generating per-DAG reports on the DAGs that can be used for further remediation, as well as understanding of DAG requirements, like the use of Connections and Variables.

Example Run
===========================
```
./airflow_v2_upgrader.py
INFO:airflow.configuration:Reading the config from /home/abella/airflow/airflow.cfg
INFO:airflow.settings:Configured default timezone Timezone('UTC')
DEBUG:airflow.settings:No airflow_local_settings to import.
Traceback (most recent call last):
  File "/home/abella/.pyenv/versions/3.8.5/envs/airflow-upgrader/lib/python3.8/site-packages/airflow/settings.py", line 453, in import_local_settings
    import airflow_local_settings
ModuleNotFoundError: No module named 'airflow_local_settings'
DEBUG:airflow.logging_config:Unable to load custom logging, using default config instead
[2022-07-21 18:42:20,499] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.docker_hook: No module named 'airflow.providers.docker'
[2022-07-21 18:42:20,499] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.druid_hook: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,500] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.hdfs_hook: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,500] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.hive_hooks: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,501] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.jdbc_hook: No module named 'airflow.providers.jdbc'
[2022-07-21 18:42:20,501] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.mssql_hook: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:20,501] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.mysql_hook: No module named 'airflow.providers.mysql'
[2022-07-21 18:42:20,501] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.oracle_hook: No module named 'airflow.providers.oracle'
[2022-07-21 18:42:20,502] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.pig_hook: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,510] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.presto_hook: No module named 'airflow.providers.presto'
[2022-07-21 18:42:20,510] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.samba_hook: No module named 'airflow.providers.samba'
[2022-07-21 18:42:20,511] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.slack_hook: No module named 'airflow.providers.slack'
[2022-07-21 18:42:20,512] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.webhdfs_hook: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,512] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.hooks.zendesk_hook: No module named 'airflow.providers.zendesk'
[2022-07-21 18:42:20,517] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.docker_operator: No module named 'airflow.providers.docker'
[2022-07-21 18:42:20,517] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.druid_check_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,646] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.hive_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,646] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.hive_stats_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,646] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.hive_to_druid: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,646] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.hive_to_mysql: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,647] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.hive_to_samba_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,648] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.jdbc_operator: No module named 'airflow.providers.jdbc'
[2022-07-21 18:42:20,648] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.mssql_operator: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:20,648] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.mssql_to_hive: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,649] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.mysql_operator: No module named 'airflow.providers.mysql'
[2022-07-21 18:42:20,649] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.mysql_to_hive: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,649] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.oracle_operator: No module named 'airflow.providers.oracle'
[2022-07-21 18:42:20,650] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.papermill_operator: No module named 'airflow.providers.papermill'
[2022-07-21 18:42:20,650] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.pig_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,795] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.presto_to_mysql: No module named 'airflow.providers.mysql'
/home/abella/.pyenv/versions/3.8.5/envs/airflow-upgrader/lib/python3.8/site-packages/airflow/operators/s3_file_transform_operator.py:25 DeprecationWarning: This module is deprecated. Please use `airflow.providers.amazon.aws.operators.s3`.
[2022-07-21 18:42:20,815] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.s3_to_hive_operator: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,815] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.operators.slack_operator: No module named 'airflow.providers.slack'
[2022-07-21 18:42:20,822] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.sensors.hdfs_sensor: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,823] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.sensors.hive_partition_sensor: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,823] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.sensors.metastore_partition_sensor: No module named 'airflow.providers.apache'
[2022-07-21 18:42:20,824] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.sensors.named_hive_partition_sensor: No module named 'airflow.providers.apache'
/home/abella/.pyenv/versions/3.8.5/envs/airflow-upgrader/lib/python3.8/site-packages/airflow/sensors/s3_key_sensor.py:22 DeprecationWarning: This module is deprecated. Please use `airflow.providers.amazon.aws.sensors.s3`.
/home/abella/.pyenv/versions/3.8.5/envs/airflow-upgrader/lib/python3.8/site-packages/airflow/sensors/s3_prefix_sensor.py:22 DeprecationWarning: This module is deprecated. Please use `airflow.providers.amazon.aws.sensors.s3`.
[2022-07-21 18:42:20,827] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.sensors.web_hdfs_sensor: No module named 'airflow.providers.apache'
[2022-07-21 18:42:21,092] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.amazon.aws.transfers.hive_to_dynamodb: No module named 'airflow.providers.apache'
[2022-07-21 18:42:21,095] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.amazon.aws.transfers.mongo_to_s3: No module named 'bson'
[2022-07-21 18:42:21,113] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.amazon.aws.transfers.salesforce_to_s3: No module named 'airflow.providers.salesforce'
[2022-07-21 18:42:21,723] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.hooks.cloud_sql: No module named 'airflow.providers.mysql'
[2022-07-21 18:42:21,760] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.hooks.dataflow: No module named 'airflow.providers.apache'
[2022-07-21 18:42:23,686] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.operators.cloud_sql: No module named 'airflow.providers.mysql'
[2022-07-21 18:42:23,692] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.operators.dataflow: No module named 'airflow.providers.apache'
[2022-07-21 18:42:23,724] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.sensors.dataflow: No module named 'airflow.providers.apache'
[2022-07-21 18:42:23,727] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.adls_to_gcs: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:23,728] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.azure_fileshare_to_gcs: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:23,729] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.bigquery_to_mssql: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:23,729] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.bigquery_to_mysql: No module named 'airflow.providers.mysql'
[2022-07-21 18:42:23,730] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.cassandra_to_gcs: No module named 'cassandra'
[2022-07-21 18:42:23,730] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.facebook_ads_to_gcs: No module named 'facebook_business'
[2022-07-21 18:42:23,732] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.gcs_to_sftp: No module named 'airflow.providers.sftp'
[2022-07-21 18:42:23,734] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.mssql_to_gcs: No module named 'airflow.providers.microsoft'
[2022-07-21 18:42:23,735] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.mysql_to_gcs: No module named 'MySQLdb'
[2022-07-21 18:42:23,735] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.oracle_to_gcs: No module named 'oracledb'
[2022-07-21 18:42:23,736] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.presto_to_gcs: No module named 'prestodb'
[2022-07-21 18:42:23,737] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.salesforce_to_gcs: No module named 'airflow.providers.salesforce'
[2022-07-21 18:42:23,737] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.sftp_to_gcs: No module named 'airflow.providers.sftp'
[2022-07-21 18:42:23,738] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.transfers.trino_to_gcs: No module named 'trino'
[2022-07-21 18:42:23,739] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.utils.mlengine_operator_utils: No module named 'airflow.providers.apache'
[2022-07-21 18:42:23,739] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.cloud.utils.mlengine_prediction_summary: No module named 'apache_beam'
[2022-07-21 18:42:23,745] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.leveldb.hooks.leveldb: No module named 'plyvel'
[2022-07-21 18:42:23,746] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.google.leveldb.operators.leveldb: No module named 'plyvel'
[2022-07-21 18:42:23,834] {airflow_v2_upgrader.py:98} ERROR - Cannot load modules from airflow.providers.snowflake.transfers.snowflake_to_slack: No module named 'airflow.providers.slack'
[2022-07-21 18:42:24,162] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:42:36,115] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
[2022-07-21 18:42:36,115] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:42:36,115] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:42:36,115] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:42:36,116] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:42:36,117] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
[2022-07-21 18:42:36,119] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
[2022-07-21 18:43:09,043] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import AirflowException
[2022-07-21 18:43:09,101] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'airflow_role'"]
[2022-07-21 18:43:09,411] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:12,332] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:43:12,332] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:43:12,332] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:43:12,362] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ['role']
[2022-07-21 18:43:12,641] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:12,641] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.utils.dates import timedelta, days_ago, datetime
[2022-07-21 18:43:12,641] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.utils.dates import timedelta, days_ago, datetime
[2022-07-21 18:43:12,641] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.utils.dates import timedelta, days_ago, datetime
[2022-07-21 18:43:12,642] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
[2022-07-21 18:43:12,642] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
[2022-07-21 18:43:12,976] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:12,978] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:43:12,978] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:31,920] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.configuration import conf
[2022-07-21 18:43:31,921] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import AirflowException
[2022-07-21 18:43:31,921] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:31,921] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.models import TaskInstance, DagRun
[2022-07-21 18:43:31,921] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.models import TaskInstance, DagRun
[2022-07-21 18:43:31,982] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'other_airflow_role'"]
[2022-07-21 18:43:32,549] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:32,549] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:43:39,829] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:39,829] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:43:39,877] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'other_airflow_role'"]
[2022-07-21 18:43:40,072] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:40,074] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:43:40,075] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:40,889] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.configuration import conf
[2022-07-21 18:43:40,889] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import AirflowException
[2022-07-21 18:43:40,890] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:40,890] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.models import TaskInstance, DagRun
[2022-07-21 18:43:40,890] {airflow_v2_upgrader.py:134} WARNING - Unhandled import: from airflow.models import TaskInstance, DagRun
[2022-07-21 18:43:40,905] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'third_airflow_role'"]
[2022-07-21 18:43:41,155] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:41,155] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:43:41,156] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:43:41,157] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:43:41,158] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:43:41,158] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:43:41,160] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
[2022-07-21 18:43:41,161] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
[2022-07-21 18:43:55,232] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'forth_airflow_role'"]
[2022-07-21 18:43:55,555] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:43:55,556] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:44:02,644] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:44:02,645] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:44:02,687] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'_airflow_role'"]
[2022-07-21 18:44:02,983] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:02,983] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:02,983] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:44:02,984] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:44:03,021] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'another_airflow_role'"]
[2022-07-21 18:44:03,258] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:04,964] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:44:04,965] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:44:04,965] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:04,992] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'another_one'"]
[2022-07-21 18:44:05,106] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:05,106] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:05,106] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:44:05,190] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:05,190] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:05,191] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:44:05,204] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'and_another_one'"]
[2022-07-21 18:44:05,540] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:05,540] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:05,541] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:44:05,541] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:44:05,569] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'yes'"]
[2022-07-21 18:44:05,684] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:05,684] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:05,685] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:44:05,864] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow import DAG
[2022-07-21 18:44:05,864] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.models import Variable
[2022-07-21 18:44:05,864] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.dates import timedelta
[2022-07-21 18:44:05,865] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email
[2022-07-21 18:44:05,866] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.email import send_email_smtp
[2022-07-21 18:44:05,866] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.utils.trigger_rule import TriggerRule
[2022-07-21 18:44:05,869] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
[2022-07-21 18:44:05,871] {airflow_v2_upgrader.py:122} WARNING - Unhandled import: from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
[2022-07-21 18:44:12,392] {airflow_v2_upgrader.py:155} WARNING - Contains DAG access controls. Setting to None: ["'svc-airflow'"]
```


Contact
=======
cabella@astronomer.io