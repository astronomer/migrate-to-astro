import json
import requests
import yaml

with open(r'airflow-connections.yaml') as file:
    connections = yaml.safe_load(file)
    nebula = connections['nebula']

class nebulaClient():
    def __init__(self):
        self.domain = f"https://deployments.{nebula['base_domain']}/{nebula['deployment_release_name']}/airflow/api/v1"
        self.headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "application/json",
            "Authorization": nebula['api_key']
        }

    def get_config(self):
        response = requests.get(url=f"{self.domain}/config", headers=self.headers)
        sections = response.json()['sections']
        for section in sections:
            if section['name'] == 'celery':
                options = section['options']
                for option in options:
                    if option['key'] == 'celery_result_backend':
                        conn_string = option['value']

        print(conn_string)

    def get_connection(self, conn_id):
        response = requests.get(url=f"{self.domain}/connections/{conn_id}", headers=self.headers).json()
        return response

    def list_providers(self):
        response = requests.get(url=f"{self.domain}/providers", headers=self.headers).json()
        return response['providers']

    def list_pools(self):
        response = requests.get(url=f"{self.domain}/pools", headers=self.headers).json()
        return response['pools']

    def list_connections(self):
        response = requests.get(url=f"{self.domain}/connections", headers=self.headers)
        return response.json()['connections']

    def get_variables(self):
        response = requests.get(url=f"{self.domain}/variables", headers=self.headers)
        return response.json()['variables']