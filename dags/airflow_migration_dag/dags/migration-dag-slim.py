    
  
    """
    This DAG facilitates the migration of connections, variables, pools, and other metadata between Airflow and Software/Astro.
    
    Simply set the following ENV Vars and then run the DAG:
    ASTRONOMER_KEY_ID=<ASTRONOMER_KEY_ID>
    ASTRONOMER_KEY_SECRET=<ASTRONOMER_KEY_SECRET>
    DESTINATION_AIRFLOW_URL=<DESTINATION_AIRFLOW_URL> (note: do not include "/home" from the Astro URL, for example: https://astronomer.astronomer.run/d13i7h22/home)
    
    Alternatively, trigger with DagRun config such as:
    {
      "ASTRONOMER_KEY_ID": "<ASTRONOMER_KEY_ID>",
      "ASTRONOMER_KEY_SECRET": "<ASTRONOMER_KEY_SECRET>",
      "DESTINATION_AIRFLOW_URL": "<DESTINATION_AIRFLOW_URL>"
    }
    """
    
    import os
    import urllib.parse
    from pprint import pprint
    from typing import Any, List
    import requests
    from airflow import DAG, settings
    from airflow.exceptions import AirflowNotFoundException
    from airflow.models.connection import Connection
    from airflow.models.dagrun import DagRun
    from airflow.models.pool import Pool
    from airflow.models.variable import Variable
    from airflow.operators.python import  PythonOperator
    from airflow.providers.http.hooks.http import HttpHook
    from airflow.utils.db import provide_session
    from datetime import datetime
    
    astro_hook = HttpHook(method="POST", http_conn_id="astro_auth")
    airflow_hook = HttpHook(method="POST", http_conn_id="destination_airflow")
    
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
    
    with DAG(
        dag_id="airflow_migration_dag",
        schedule_interval=None,
        start_date=datetime(2022, 1, 1),
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
    
        migration_tasks = [
            migrate_vars_task,
            migrate_conns_task,
            migrate_pools_task
        ]
    
        astro_auth_task >> migration_tasks
