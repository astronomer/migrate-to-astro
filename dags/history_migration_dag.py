"""Airflow History Migration DAG
Q: Why not pg_dump? A: You can do that, it'll certainly be faster.
    Airflow versions (or even metadata databases) may not be consistent between source and dest,
    This should alleviate some of, and migrate as much as is possible to migrate

Requirements:
- apache-airflow-providers-postgres (or equivalent)
- a tested Airflow connection
- similar-enough Airflow versions and database versions, YMMV
"""
import logging
import os
from datetime import datetime

import sqlalchemy
from airflow import settings
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.exc import NoSuchTableError


def migrate(hook, table_name: str, batch_size: int = 100000):
    def get_table(_metadata_obj, _engine, _table_name):
        try:
            return Table(f'airflow.{_table_name}', _metadata_obj, autoload_with=_engine)
        except NoSuchTableError:
            return Table(_table_name, _metadata_obj, autoload_with=_engine)

    logging.info(f"Creating source SQL Connections from {hook.get_conn()}...")
    source_engine = create_engine(hook.get_uri(), echo=False)
    source_metadata_obj = MetaData(bind=source_engine)
    source_table = get_table(source_metadata_obj, source_engine, table_name)

    logging.info(f"Creating dest SQL Connection from This Airflow...")
    dest_session = settings.Session()
    dest_engine = dest_session.get_bind()
    dest_metadata_obj = MetaData(bind=dest_engine)
    dest_table = get_table(dest_metadata_obj, dest_engine, table_name)

    columns_in_both = ','.join(
        {c.name for c in source_table.columns}
        .intersection(c.name for c in dest_table.columns)
        - {'id'}
    )
    logging.info(f"Found {len(columns_in_both)} columns that overlap in {table_name} "
                 f"between source and dest - not including 'id'...")

    # noinspection SqlInjection
    logging.info(f"Fetching data for {table_name} from source...")
    source_result = source_engine.execution_options(stream_results=True) \
        .execute(f"SELECT {columns_in_both} FROM {source_table.name}")
    while batch := source_result.fetchmany(batch_size):
        logging.info(f"Fetched and inserting batch of at most {batch_size} for {table_name} from source to dest...")
        dest_engine.execute(
            sqlalchemy.dialects.postgresql.insert(dest_table).on_conflict_do_nothing(),
            # ### ^POTENTIALLY CHANGE HERE^ ###
            [dict(row) for row in batch]
        )
    dest_session.commit()


@dag(
    schedule_interval=None, start_date=datetime(1970, 1, 1),
    tags=["migration"], default_args={"owner": "Astronomer", "retries": 0},
)
def airflow_history_migration():
    args = {
        "hook": PostgresHook(postgres_conn_id='pg'),
        "batch_size": 25000
    }
    # ### ^POTENTIALLY CHANGE HERE^ ###

    chain(
        *[
            task(migrate, task_id=f"migrate_{table_name}")(**args, table_name=table_name)
            for table_name in [
                "dag_run",
                "task_instance",
            ]
        ], [
            task(migrate, task_id=f"migrate_{table_name}")(**args, table_name=table_name)
            for table_name in [
                "task_reschedule",
                "trigger",
                "task_fail",
                "xcom",
                "rendered_task_instance_fields",
                "sensor_instance",
                "sla_miss",
            ]
        ]
    )


airflow_history_migration_dag = airflow_history_migration()

