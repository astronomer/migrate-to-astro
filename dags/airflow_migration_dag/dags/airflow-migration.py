"""This DAG facilitates the migration of connections, variables, pools, and other metadata between Airflow and Software/Astro."""

import json
import os
import pickle
import urllib.parse
from base64 import b64decode
from io import BytesIO
from pprint import pprint
from typing import Any, Callable, List
from unittest.util import strclass

import airflow.models as airflow_models
import requests
from airflow import DAG, settings
from airflow.exceptions import AirflowNotFoundException
from airflow.models.connection import Connection
from airflow.models.dagrun import DagRun
from airflow.models.pool import Pool
from airflow.models.variable import Variable
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import dates
from airflow.utils.db import provide_session
from sqlalchemy.orm import Session, sessionmaker

astro_hook = HttpHook(method="POST", http_conn_id="astro_auth")
airflow_hook = HttpHook(method="POST", http_conn_id="destination_airflow")

MODELS = [
    "DagRun",
    "RenderedTaskInstanceFields",
    "SensorInstance",
    "SlaMiss",
    "TaskFail",
    "TaskInstance",
    "TaskReschedule",
    "Trigger",
]


def _set_environment(config: dict[Any, Any]) -> None:
    """_set_environment updates the environment with the passed in config and sets connection strings

    Args:
        config (dict[Any, Any]): The provided DagRun config

    Raises:
        AirflowNotFoundException: If DESTINATION_AIRFLOW_URL is missing from environment or DagRun config
    """
    os.environ.update(config)
    os.environ["AIRFLOW_CONN_ASTRO_AUTH"] = "http://https%3A%2F%2Fauth.astronomer.io"

    try:
        destination_airflow_url = os.environ["DESTINATION_AIRFLOW_URL"]
        os.environ[
            "AIRFLOW_CONN_DESTINATION_AIRFLOW"
        ] = f"http://{urllib.parse.quote_plus(destination_airflow_url)}"
    except KeyError as e:
        raise AirflowNotFoundException(
            "Missing DESTINATION_AIRFLOW_URL in environment or DagRun config"
        )

    pg_user = os.environ.get("DESTINATION_PG_USER")
    pg_pass = os.environ.get("DESTINATION_PG_PASS")
    pg_host = os.environ.get("DESTINATION_PG_HOST")
    pg_db_name = os.environ.get("DESTINATION_PG_DB_NAME")
    pg_port = os.environ.get("DESTINATION_PG_PORT", 5432)
    if all([pg_user, pg_pass, pg_host, pg_db_name]):
        os.environ[
            "AIRFLOW_CONN_DESTINATION_POSTGRES"
        ] = f"postgres://{pg_user}:{urllib.parse.quote_plus(pg_pass)}@{pg_host}:{pg_port}/{pg_db_name}"

    aws_access_key_id = os.environ.get("DESTINATION_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("DESTINATION_AWS_SECRET_ACCESS_KEY")
    if aws_access_key_id is not None and aws_secret_access_key is not None:
        os.environ[
            "AIRFLOW_CONN_DESTINATION_S3"
        ] = f"aws://{aws_access_key_id}:{urllib.parse.quote_plus(aws_secret_access_key)}@"

    azure_storage_account = os.environ.get("DESTINATION_AZURE_STORAGE_ACCOUNT")
    azure_storage_key = os.environ.get("DESTINATION_AZURE_STORAGE_KEY")
    if all([azure_storage_account, azure_storage_key]):
        os.environ[
            "AIRFLOW_CONN_DESTINATION_WASB"
        ] = f"wasb://{azure_storage_account}:{azure_storage_key}@"

    gcp_key_file_path = os.environ.get("DESTINATION_GCP_KEY_FILE_PATH")
    gcp_b64_key_file_json = os.environ.get("DESTINATION_GCP_B64_KEY_FILE_JSON")
    if gcp_key_file_path:
        os.environ[
            "AIRFLOW_CONN_DESTINATION_GCS"
        ] = f"google-cloud-platform://?extra__google_cloud_platform__key_path={gcp_key_file_path}"
    elif gcp_b64_key_file_json:
        gcp_key_file_json = b64decode(gcp_b64_key_file_json).decode("utf-8")
        os.environ[
            "AIRFLOW_CONN_DESTINATION_GCS"
        ] = f"google-cloud-platform://?extra__google_cloud_platform__keyfile_dict={gcp_key_file_json}"


def _upload_to_s3(model: str, data: bytes, bucket: str) -> None:
    s3_hook = S3Hook(aws_conn_id="destination_s3")
    s3_key_path = os.environ.get("DESTINATION_S3_KEY_PATH", "")
    s3_key = os.path.join(s3_key_path, f"{model}.pickle")

    print(f"Saving {model} to {bucket}/{s3_key}")
    s3_hook.load_bytes(
        bucket_name=bucket,
        key=s3_key,
        bytes_data=data,
        replace=True,
    )


def _upload_to_wasb(model: str, data: bytes, bucket: str) -> None:
    wasb_hook = WasbHook(wasb_conn_id="destination_wasb")
    azure_container_path = os.environ.get("DESTINATION_AZURE_CONTAINER_PATH", "")
    wasb_key = os.path.join(azure_container_path, f"{model}.pickle")

    print(f"Saving {model} to {bucket}/{wasb_key}")
    wasb_hook.upload(
        container_name=bucket,
        blob_name=wasb_key,
        data=data,
        overwrite=True,
    )


def _upload_to_gcs(model: str, data: bytes, bucket: str) -> None:
    gcs_hook = GCSHook(gcp_conn_id="destination_gcs")
    gcs_key_path = os.environ.get("DESTINATION_GCS_KEY_PATH", "")

    gcs_key = os.path.join(gcs_key_path, f"{model}.pickle")

    print(f"Saving {model} to {bucket}/{gcs_key}")
    gcs_hook.upload(
        bucket_name=bucket,
        object_name=gcs_key,
        data=data,
    )


def _upload_to_db(model: str, objs: List[object]) -> None:
    postgres_hook = PostgresHook(postgres_conn_id="destination_postgres")
    destination_session: Session = sessionmaker(
        bind=postgres_hook.get_sqlalchemy_engine(
            engine_kwargs={"connect_args": {"options": "-csearch_path=airflow"}}
        )
    )()

    print(f"Saving {model} to destination db")
    for obj in objs:
        destination_session.merge(obj)
        destination_session.commit()


def astro_auth(dag_run: DagRun, **context) -> str:
    """astro_auth authenticates with Astronomer Software or Astro and returns a token

    Args:
        dag_run (DagRun): The DagRun context

    Raises:
        AirflowNotFoundException: If ASTRONOMER_API_KEY or ASTRONOMER_KEY_ID and ASTRONOMER_KEY_SECRET are missing

    Returns:
        str: The authentication token
    """
    _set_environment(dag_run.conf)

    astronomer_api_key = os.environ.get("ASTRONOMER_API_KEY")
    if astronomer_api_key is not None:
        return astronomer_api_key

    astronomer_key_id = os.environ.get("ASTRONOMER_KEY_ID")
    astronomer_key_secret = os.environ.get("ASTRONOMER_KEY_SECRET")
    if astronomer_key_id is not None and astronomer_key_secret is not None:
        api_response: requests.Response = astro_hook.run(
            endpoint="oauth/token",
            headers={"content-type": "application/json"},
            json={
                "client_id": astronomer_key_id,
                "client_secret": astronomer_key_secret,
                "audience": "astronomer-ee",
                "grant_type": "client_credentials",
            },
        )
        return api_response.json()["access_token"]

    raise AirflowNotFoundException(
        "Missing Astronomer authentication credentials in environment or DagRun config"
    )


@provide_session
def migrate_conns(
    access_token: str = None,
    session: settings.SASession = None,
    dag_run: DagRun = None,
    **context,
) -> None:
    """migrate_conns queries Connections from the Airflow DB and creates them in the destination Airflow

    Args:
        access_token (str, optional): The authentication token for the destination Airflow. Defaults to None.
        session (settings.SASession, optional): The Airflow DB session. Defaults to None.
        dag_run (DagRun, optional): The DagRun context. Defaults to None.
    """
    _set_environment(dag_run.conf)
    connections: List[Connection] = session.query(Connection).all()

    for connection in connections:
        connection_data = {
            "connection_id": connection.conn_id,
            "conn_type": connection.conn_type,
            "host": connection.host,
            "login": connection.login,
            "schema": connection.schema,
            "port": connection.port,
            "password": connection.password or "",
            "extra": connection.extra,
        }

        # create connection
        api_response: requests.Response = airflow_hook.run(
            endpoint="api/v1/connections",
            json=connection_data,
            headers={
                "content-type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            extra_options={"check_response": False},
        )
        print(api_response.content.decode("utf-8"))
        if api_response.status_code == 409:
            print(f"Connection {connection.conn_id} already exists.")
        else:
            airflow_hook.check_response(api_response)
        pprint(api_response.json())


@provide_session
def migrate_vars(
    access_token: str = None,
    session: settings.SASession = None,
    dag_run: DagRun = None,
    **context,
) -> None:
    """migrate_vars queries Variables from the Airflow DB and creates them in the destination Airflow

    Args:
        access_token (str, optional): The authentication token for the destination Airflow. Defaults to None.
        session (settings.SASession, optional): The Airflow DB session. Defaults to None.
        dag_run (DagRun, optional): The DagRun context. Defaults to None.
    """
    _set_environment(dag_run.conf)
    variables: List[Variable] = session.query(Variable).all()

    for variable in variables:
        variable_data = {
            "key": variable.key,
            "value": variable.val,
        }

        # create variable
        api_response: requests.Response = airflow_hook.run(
            endpoint="api/v1/variables",
            json=variable_data,
            headers={
                "content-type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        pprint(api_response.json())


@provide_session
def migrate_pools(
    access_token: str = None,
    session: settings.SASession = None,
    dag_run: DagRun = None,
    **context,
) -> None:
    """migrate_pools queries Pools from the Airflow DB and creates them in the destination Airflow

    Args:
        access_token (str, optional): The authentication token for the destination Airflow. Defaults to None.
        session (settings.SASession, optional): The Airflow DB session. Defaults to None.
        dag_run (DagRun, optional): The DagRun context. Defaults to None.
    """
    _set_environment(dag_run.conf)
    pools: List[Pool] = session.query(Pool).all()

    for pool in pools:
        pool_data = {
            "name": pool.pool,
            "slots": pool.slots,
        }

        # create pool
        api_response: requests.Response = airflow_hook.run(
            endpoint="api/v1/pools",
            json=pool_data,
            headers={
                "content-type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            extra_options={"check_response": False},
        )
        if api_response.status_code == 409:
            print(f"Pool {pool.pool} already exists.")
        else:
            airflow_hook.check_response(api_response)
        pprint(api_response.json())


@provide_session
def export_metadata_to_storage(
    bucket_var: str,
    upload_callable: Callable,
    session: settings.SASession = None,
    dag_run: DagRun = None,
    **context,
) -> None:
    """export_metadata_to_s3 migrates the Airflow metadata for DAG history to an S3 bucket

    Args:
        session (settings.SASession, optional): The Airflow DB session. Defaults to None.
        dag_run (DagRun, optional): The DagRun context. Defaults to None.
    """
    _set_environment(dag_run.conf)

    bucket = os.environ.get(bucket_var)

    for model in MODELS:
        print(f"Querying {model}")
        objs = session.query(getattr(airflow_models, model)).all()

        if bucket is not None:
            upload_callable(model=model, data=pickle.dumps(objs), bucket=bucket)

        print(f"Saved {model} ({len(objs)})")


@provide_session
def export_metadata_to_db(
    model: str,
    session: settings.SASession = None,
    dag_run: DagRun = None,
    **context,
) -> None:
    """export_metadata_to_db exports the Airflow metadata for DAG history to the destination Airflow DB

    Args:
        session (settings.SASession, optional): The Airflow DB session. Defaults to None.
        dag_run (DagRun, optional): The DagRun context. Defaults to None.
    """
    _set_environment(dag_run.conf)

    print(f"Querying {model}")
    objs = session.query(getattr(airflow_models, model)).all()
    _upload_to_db(model=model, objs=objs)
    print(f"Merged {model} ({len(objs)})")


with DAG(
    dag_id="airflow_migration",
    schedule_interval=None,
    start_date=dates.days_ago(1),
    catchup=False,
    tags=["migration"],
) as dag:
    # authenticate with Astronomer
    astro_auth_task = PythonOperator(
        task_id="astro_auth",
        dag=dag,
        python_callable=astro_auth,
    )

    # migrate variables
    migrate_vars_task = PythonOperator(
        task_id="migrate_vars",
        dag=dag,
        python_callable=migrate_vars,
        op_kwargs={"access_token": "{{ ti.xcom_pull(task_ids='astro_auth') }}"},
    )

    # migrate connections
    migrate_conns_task = PythonOperator(
        task_id="migrate_conns",
        dag=dag,
        python_callable=migrate_conns,
        op_kwargs={"access_token": "{{ ti.xcom_pull(task_ids='astro_auth') }}"},
    )

    # migrate pools
    migrate_pools_task = PythonOperator(
        task_id="migrate_pools",
        dag=dag,
        python_callable=migrate_pools,
        op_kwargs={"access_token": "{{ ti.xcom_pull(task_ids='astro_auth') }}"},
    )

    export_metadata_s3_task = PythonOperator(
        task_id="export_metadata_to_s3",
        dag=dag,
        python_callable=export_metadata_to_storage,
        op_kwargs={
            "bucket_var": "DESTINATION_S3_BUCKET",
            "upload_callable": _upload_to_s3,
        },
    )

    export_metadata_wasb_task = PythonOperator(
        task_id="export_metadata_to_wasb",
        dag=dag,
        python_callable=export_metadata_to_storage,
        op_kwargs={
            "bucket_var": "DESTINATION_AZURE_CONTAINER",
            "upload_callable": _upload_to_wasb,
        },
    )

    export_metadata_gcs_task = PythonOperator(
        task_id="export_metadata_to_gcs",
        dag=dag,
        python_callable=export_metadata_to_storage,
        op_kwargs={
            "bucket_var": "DESTINATION_GCS_BUCKET",
            "upload_callable": _upload_to_gcs,
        },
    )

    migration_tasks = [
        migrate_vars_task,
        migrate_conns_task,
        migrate_pools_task,
        export_metadata_s3_task,
        export_metadata_wasb_task,
        export_metadata_gcs_task,
    ]

    for model in MODELS:
        export_metadata_db_task = PythonOperator(
            task_id=f"export_{model}_to_db",
            dag=dag,
            python_callable=export_metadata_to_db,
            op_kwargs={"model": model},
        )
        migration_tasks.append(export_metadata_db_task)

    astro_auth_task >> migration_tasks
