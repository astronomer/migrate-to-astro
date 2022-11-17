import json
from datetime import datetime
from typing import List

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.utils import db
from airflow.contrib.hooks.gcp_api_base_hook import GoogleCloudBaseHook
from google.cloud.secretmanager_v1 import SecretManagerServiceClient, Secret, SecretPayload

GCP_CONN_ID = "gcp_conn"  # Replace this
GCP_PROJECT_ID = "astronomer-solutions"  # Replace this


def migrate_vars():
    with db.create_session() as session:
        variables: List[Variable] = session.query(Variable).all()
    for variable in variables:
        gcp_hook = GoogleCloudBaseHook(gcp_conn_id=GCP_CONN_ID)
        credentials = gcp_hook._get_credentials()
        client = SecretManagerServiceClient(credentials=credentials)
        parent = f"projects/{GCP_PROJECT_ID}"
        secret = client.create_secret(
            parent=parent,
            secret_id=f"airflow-connections-{variable.key}",
            secret=Secret(replication={"automatic": {}}),
        )
        payload = SecretPayload(data=str(variable.val).encode('UTF-8'))
        # Add the secret version.
        client.add_secret_version(
            parent=secret.name,
            payload=payload
        )


with DAG(
        dag_id="migrate_vars_gsm",
        schedule_interval=None,
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["migration"],
) as dag:
    astro_auth_task = PythonOperator(
        task_id="migrate_conns",
        dag=dag,
        python_callable=migrate_vars,
    )
