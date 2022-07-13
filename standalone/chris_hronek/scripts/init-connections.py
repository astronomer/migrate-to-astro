import yaml

if __name__ == '__main__':
    dict_file = {
        'astro': {
            'domain': "<INSERT DOMAIN HERE>",
            'key_id': "<INSERT KEY ID HERE>",
            'key_secret': "<INSERT KEY SECRET HERE>"
        },
        'nebula': {
            'api_key': "<INSERT API KEY HERE>",
            'base_domain': "<INSERT BASE DOMAIN HERE>",
            'deployment_release_name': "<INSERT DEPLOYMENT RELEASE NAME HERE>"
        }
    }

    with open(r'airflow-connections.yaml', 'w') as file:
        documents = yaml.dump(dict_file, file)
