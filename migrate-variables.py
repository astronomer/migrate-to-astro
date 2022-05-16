import json
import requests

class nebulaClient():
    def __init__(self, api_key, base_domain, deployment_release_name):
        self.domain = f'https://deployments.{base_domain}/{deployment_release_name}/airflow/api/v1'
        self.headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "application/json",
            "Authorization": api_key
        }

    def get_variables(self):
        response = requests.get(url=f"{self.domain}/variables", headers=self.headers)
        return response.json()['variables']


class astroClient():
    def __init__(self, domain, astro_key_id, astro_key_secret):
        self.domain = domain
        self.headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "application/json"
        }
        self.astro_key_id = astro_key_id
        self.astro_key_secret = astro_key_secret

    def create_variable(self, key, value):
        url = f'{self.domain}/api/v1/variables'
        payload = json.dumps({
            "key": key,
            "value": value
        })
        response = requests.post(url=url, headers=self._build_headers(), data=payload)
        if response.status_code == 200:
            print(f"Variable {response.json()['key']} succcessfully migrated")

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


if __name__ == '__main__':
    nebula_api_key = input("Enter Nebula API Key: ")
    nebula_base_domain = input("Enter Nebula Base Domain: ")
    nebula_deployment_release_name = input("Enter Nebula Deployment Release Name: ")
    astro_domain = input("Enter Astro Domain: ")
    astro_key_id = input("Enter Astro Key ID: ")
    astro_key_secret = input("Enter Astro Key Secret: ")

    nebula = nebulaClient(
        api_key=nebula_api_key,
        base_domain=nebula_base_domain,
        deployment_release_name=nebula_deployment_release_name
    )
    variables = nebula.get_variables()

    astro = astroClient(
        domain=astro_domain,
        astro_key_id=astro_key_id,
        astro_key_secret=astro_key_secret
    )

    for variable in variables:
        astro.create_variable(key=variable['key'], value=variable['value'])
