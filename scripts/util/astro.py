import json
import requests
import yaml

with open(r'airflow-connections.yaml') as file:
    connections = yaml.safe_load(file)
    astro = connections['astro']

class astroClient():
    def __init__(self):
        self.domain = astro['domain']
        self.headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "application/json"
        }
        self.astro_key_id = astro['key_id']
        self.astro_key_secret = astro['key_secret']

    def create_pool(self, name, slots, description=None):
        url = f"{self.domain}/api/v1/pools"
        payload = json.dumps({
            "name": name,
            "slots": slots,
            "description": description
        })
        response = requests.post(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Pool {name} successfully created")

    def update_pool(self, name, slots, description=None):
        url = f"{self.domain}/api/v1/pools/{name}"
        payload = json.dumps({
            "name": name,
            "slots": slots,
            "description": description
        })
        response = requests.patch(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Pool {name} successfully updated")

    def create_connection(self, conn_id, conn_type, host, login, schema, port, extra,description):
        url = f"{self.domain}/api/v1/connections"
        payload = json.dumps({
            "connection_id": conn_id,
            "conn_type": conn_type,
            "host": host,
            "login": login,
            "schema": schema,
            "port": port,
            "password": "pa$$word",
            "extra": extra,
            "description": description
        })
        response = requests.post(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Connection {conn_id} successfully created - please fill in password field manually")

    def update_connection(self, conn_id, conn_type, host, login, schema, port, extra, description):
        url = f"{self.domain}/api/v1/connections/{conn_id}"
        payload = json.dumps({
            "connection_id": conn_id,
            "conn_type": conn_type,
            "host": host,
            "login": login,
            "schema": schema,
            "port": port,
            "extra": extra,
            "description": description
        })
        response = requests.patch(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Connection {conn_id} successfully updated - please fill in password field manually")

    def create_variable(self, key, value):
        url = f'{self.domain}/api/v1/variables'
        payload = json.dumps({
            "key": key,
            "value": value
        })
        response = requests.post(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Variable {response.json()['key']} succcessfully created")

    def update_variable(self, key, value):
        url = f'{self.domain}/api/v1/variables/{key}'
        payload = json.dumps({
            "key": key,
            "value": value
        })
        response = requests.patch(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Variable {response.json()['key']} succcessfully updated")
            
    def list_providers(self):
        url = f'{self.domain}/api/v1/providers'
        response = requests.get(url=url, headers=self._build_headers()).json()
        return response['providers']

    def list_connections(self):
        url = f'{self.domain}/api/v1/connections'
        response = requests.get(url=url, headers=self._build_headers()).json()
        return response['connections']

    def list_pools(self):
        url = f'{self.domain}/api/v1/pools'
        response = requests.get(url=url, headers=self._build_headers()).json()
        return response['pools']

    def list_variables(self):
        url = f'{self.domain}/api/v1/variables'
        response = requests.get(url=url, headers=self._build_headers()).json()
        return response['variables']

    def _build_headers(self):
        authorized_headers = self.headers
        authorized_headers['authorization'] = f"Bearer {self._get_token()}"
        return authorized_headers

    def _get_token(self):
        headers = {
            "content-type": "application/json"
        }

        data = json.dumps({
            "client_id": self.astro_key_id,
            "client_secret": self.astro_key_secret,
            "audience": "astronomer-ee",
            "grant_type": "client_credentials"
        })

        response = requests.post(url="https://auth.astronomer.io/oauth/token", data=data, headers=headers).json()
        return response["access_token"]
