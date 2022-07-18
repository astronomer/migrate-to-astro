from datetime import datetime, timedelta
from typing import Dict
import requests
import json
import subprocess
from airflow.models import Variable
from airflow.decorators import dag, task
from airflow.utils.db import provide_session
from airflow.models import XCom
from cryptography.fernet import Fernet

@dag(
    start_date=datetime(2021, 6, 11),
    max_active_runs=1,
    schedule_interval=None,
    default_args={
        "owner": "community",
        "retries": 2,
        "retry_delay": timedelta(minutes=3),
    },
    catchup=False,
    tags=["migration"],
)
def conn_migration_dag():
    @task
    def gen_key():
        key = Fernet.generate_key()
        return key.decode("utf-8")

    @task
    def get_local_conns(key):
        cipher_suite = Fernet(key.encode("utf-8"))
        conns = subprocess.run(['airflow', 'connections', 'list', '-o', 'json'], capture_output=True, text=True)
        return cipher_suite.encrypt(conns.stdout.encode("utf-8")).decode("utf-8")

    @task
    def format_conns(conns,key):
        print(key)
        cipher_suite = Fernet(key.encode("utf-8"))
        # print(cipher_suite.decrypt(conns.encode('utf-8')).decode('utf-8'))
        conns = json.loads(cipher_suite.decrypt(conns.encode('utf-8')).decode('utf-8'))

        formatted_conns = []
        for conn in conns:
            formatted_conn = {
                "connection_id": conn["conn_id"],
                "conn_type": conn["conn_type"],
                "host": conn["host"],
                "login": conn["login"],
                "schema": conn["schema"],
                "port": int(conn["port"]) if conn["port"] else None,
                "password": conn["password"] if conn["password"] else "",
                "extra": str(conn["extra_dejson"])
            }
            formatted_conns.append(cipher_suite.encrypt(json.dumps(formatted_conn).encode("utf-8")).decode("utf-8"))
        return formatted_conns

    @task
    def push_conns(data, key):
        cipher_suite = Fernet(key.encode("utf-8"))
        data = cipher_suite.decrypt(data.encode('utf-8')).decode('utf-8')
        url = Variable.get("ASTRO_URL")
        token = Variable.get("ASTRO_ACCESS_KEY")
        headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        r = requests.post(f'{url}/api/v1/connections', data=data, headers=headers)
        if r.status_code != 200:
            raise ValueError('Connection not created')

    @task
    @provide_session
    def delete_xcoms(session=None, **kwargs):
        ti = kwargs['ti']
        print(ti.dag_id)
        session.query(XCom).filter(XCom.dag_id == ti.dag_id).delete()
    key=gen_key()
    push_conns.partial(key=key).expand(data=format_conns(get_local_conns(key),key)) >> delete_xcoms()


dag = conn_migration_dag()
