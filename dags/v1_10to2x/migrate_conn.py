from datetime import datetime, timedelta
from typing import Dict
import requests
import json
import subprocess
from airflow import DAG, settings
from airflow.operators.python_operator import PythonOperator
from airflow.utils import db
from airflow.models import Connection
from airflow.models import Variable




def migrate_conns(**kwargs):
    """
    migrate_conns
    {"dry_run": true}
    """
    dry_run = False
    if 'dry_run' in kwargs['dag_run'].conf.keys():
        dry_run = True

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
        if dry_run == False:
            url = Variable.get("ASTRO_URL")
            token = Variable.get("ASTRO_ACCESS_KEY")
            headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
            r = requests.post(f'{url}/api/v1/connections', data=json.dumps(formatted_conn), headers=headers)
            print(conn[3])
            print(r.text)
        else:
            print(formatted_conn)

    print(conn_list)

with DAG(
    dag_id="migrate_conns",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=["migration"],
) as dag:
    astro_auth_task = PythonOperator(
        task_id="migrate_conns",
        python_callable=migrate_conns,
        provide_context=True,
        dag=dag
    )
