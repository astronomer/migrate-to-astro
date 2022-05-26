from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()

    for connection in nebula.list_connections():
        src_conn = nebula.get_connection(connection['connection_id'])
        astro.create_connection(
            conn_id=src_conn["connection_id"],
            conn_type=src_conn["conn_type"],
            host=src_conn["host"],
            login=src_conn["login"],
            schema=src_conn["schema"],
            port=src_conn["port"],
            extra=src_conn["extra"]
        )