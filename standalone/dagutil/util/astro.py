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

    def _build_headers(self):
        authorized_headers = self.headers
        authorized_headers['authorization'] = f"Bearer {self._get_token()}"
        return authorized_headers

    def _get_token(self):

        try:
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

        except Exception as e:
            print("EXCEPTION: Got Exception while getting the Auth Token for Astro. Please check airflow-connections.yaml file. Terminating Execution")
            print(str(e))
            exit()

    def pause_unpausedags(self,dag_id, pauseflag):

        try: 

            url = f'{self.domain}/api/v1/dags/{dag_id}'
            payload = json.dumps({
                "is_paused": pauseflag
            })
            response = requests.patch(url=url, headers=self._build_headers(), data = payload)
            
            if response.status_code == 200:
                if pauseflag:
                    status = " SUCCESS: API call to pause the Dag " + dag_id + " is successful"
                else:
                    status = " SUCCESS: API call to unpause the Dag " + dag_id + " is successful"
            else:
                if " ERROR: Cannot access requested deployment" in response.text:
                    status = " ERROR: Please provide correct domain for the target deployment"
                
                elif "Dag with id: '"+dag_id+"' not found" in response.text:
                    status = " ERROR: Dag with id " +  dag_id+ " not found in the deployment " + self.domain
                
                else:
                    status = " ERROR: Unable to perform the requested action, Please check"
            
            return status
        
        except Exception as e:
            print(" EXCEPTION: Got Exception while performing the pause/unpause action")
            print(str(e))

    def list_dags(self,daglimit,dagoffset):
            
            url = f'{self.domain}/api/v1/dags?limit={daglimit}&offset={dagoffset}'
            response = requests.get(url=url, headers=self._build_headers())
            
            if response.status_code == 200:
                return response.text
            
            else:
                if " ERROR: Cannot access requested deployment" in response.text:
                    status = " ERROR: Please provide correct domain for the target deployment"
                    print(status)
                    exit()
                    
                else:
                    status = " ERROR: Unable to perform the requested action, Please check"
                    print(status)
                    exit()
                
                