from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()

    # identify existing connections
    existing_target_conn_ids = []
    for connection in astro.list_connections():
        existing_target_conn_ids.append(connection['connection_id'])

    # migrate the connections
    for connection in nebula.list_connections():
        src_conn = nebula.get_connection(connection['connection_id'])

        # TODO: Identify the version of Airflow where description is included in Payload
        # need to specify if description is in payload. Description was added in Airflow 2.3.0
        if 'description' in src_conn:
            description = src_conn['description']
        else:
            description = ''

        # update the existing connection in target instead of create
        if connection['connection_id'] in existing_target_conn_ids:
            astro.update_connection(
                conn_id=src_conn["connection_id"],
                conn_type=src_conn["conn_type"],
                host=src_conn["host"],
                login=src_conn["login"],
                schema=src_conn["schema"],
                port=src_conn["port"],
                extra=src_conn["extra"],
                description=description
            )
        # create connection if it doesn't exist
        else:
            astro.create_connection(
                conn_id=src_conn["connection_id"],
                conn_type=src_conn["conn_type"],
                host=src_conn["host"],
                login=src_conn["login"],
                schema=src_conn["schema"],
                port=src_conn["port"],
                extra=src_conn["extra"],
                description=description
            )
