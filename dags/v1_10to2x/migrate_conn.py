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




def migrate_conns():
    with db.create_session() as session:
        variables: List[Variable] = session.query(Variable).all()
        # connections = session.query(Connection).all()
    for variable in variables:
        variable_data = {
            "key": variable.key,
            "value": variable.val,
        }


        url = Variable.get("ASTRO_URL")
        token = Variable.get("ASTRO_ACCESS_KEY")
        headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        r = requests.post(f'{url}/api/v1/variables', data=json.dumps(variable_data), headers=headers)
        print(r.text)

with DAG(
    dag_id="migrate_vars",
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
