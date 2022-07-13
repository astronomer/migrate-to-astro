import json
import requests
import yaml

with open(r'airflow-connections.yaml') as file:
    connections = yaml.safe_load(file)
    software = connections['software']

class softwareClient():
    def __init__(self):
        self.domain = f"https://deployments.{software['base_domain']}/{software['deployment_release_name']}/airflow/api/v1"
        self.headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "application/json",
            "Authorization": software['api_key']
        }

    def pause_unpausedags(self,dag_id, pauseflag):
        
        url = f"{self.domain}/dags/{dag_id}"
        payload = json.dumps({
            "is_paused": pauseflag
        })
        response = requests.patch(url=url, headers=self.headers, data = payload)
        
        if (response.status_code == 200) and (dag_id in response.text):
            
            if pauseflag:
                status = " SUCCESS: API call to pause the Dag " + dag_id + " is successful"
            
            else:
                status = " SUCCESS: API call to unpause the Dag " + dag_id + " is successful"
        else:
            
            if " ERROR: Cannot access requested deployment" in response.text:
                status = " ERROR: Please provide correct domain for the target deployment"
            
            elif "Dag with id: '"+dag_id+"' not found" in response.text:
                status = " ERROR: Dag with id " +  dag_id+ " not found in the deployment " + self.domain
                        
            elif "<title>Astronomer - 404</title>" in response.text:
                status = " ERROR: Dag with id " +  dag_id+ " not found in the deployment " + self.domain
                
            else:
                status = " ERROR: Unable to perform the requested action, Please check"
                print(status)
                exit()

        return status

    def list_dags(self):

            url = f"{self.domain}/dags"
        
            response = requests.get(url=url, headers=self.headers)
                
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