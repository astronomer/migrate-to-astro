import json
from datetime import datetime

from airflow import DAG
from airflow.models import Connection
from airflow.operators.python_operator import PythonOperator
from airflow.utils import db
from airflow.contrib.hooks.gcp_api_base_hook import GoogleCloudBaseHook
from google.cloud.secretmanager_v1 import SecretManagerServiceClient, Secret, SecretPayload

GCP_CONN_ID = "gcp_conn"  # Replace this
GCP_PROJECT_ID = "astronomer-solutions"  # Replace this


def migrate_conns():
    with db.create_session() as session:
        connections = session.query(Connection).all()

    conn_list = [
        [getattr(c, column.name) for column in Connection.__mapper__.columns]
        for c in connections
    ]

    for conn in conn_list:
        formatted_conn = {
            "connection_id": conn[3],
            "conn_type": conn[4],
            "host": conn[5],
            "login": conn[7],
            "schema": conn[6],
            "port": int(conn[8]) if conn[8] else None,
            "password": conn[0] if conn[0] else "",
            "extra": str(conn[1])
        }
        gcp_hook = GoogleCloudBaseHook(gcp_conn_id=GCP_CONN_ID)
        credentials = gcp_hook._get_credentials()
        client = SecretManagerServiceClient(credentials=credentials)
        parent = f"projects/{GCP_PROJECT_ID}"
        secret = client.create_secret(
            parent=parent,
            secret_id=f"airflow-connections-{conn[3]}",
            secret=Secret(replication={"automatic": {}}),
        )
        payload = SecretPayload(data=json.dumps(formatted_conn).encode("UTF-8"))
        # Add the secret version.
        client.add_secret_version(
            parent=secret.name,
            payload=payload
        )
        print(conn[3])
    print(conn_list)


with DAG(
        dag_id="migrate_conns_gsm",
        schedule_interval=None,
        start_date=datetime(2022, 1, 1),
        catchup=False,
        tags=["migration"],
) as dag:
    astro_auth_task = PythonOperator(
        task_id="migrate_conns",
        dag=dag,
        python_callable=migrate_conns,
    )
