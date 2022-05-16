# Overview
This repository is meant to contain scripts to assist customers moving from Nebula to Astro. See usage instructions below

# Pre-requisites
- Python 3

# Setup
  1. Use the command `git clone git@github.com:astronomer/cs-utility-nebula-to-astro.git` to clone this repo
  2. Use the command `cd cs-utility-nebula-to-astro` to change your working directory
  3. Create a new file called `airflow-connections.yaml` using the command `touch airflow-connections.yaml`
  4. Paste the following contents into the newly created `airflow-connections.yaml` file:

  ```yaml
  astro:
    domain: '<INSERT DOMAIN HERE>'
    key_id: '<INSERT KEY ID HERE>'
    key_secret: '<INSERT KEY SECRET HERE>'

  nebula:
    api_key: '<INSERT API KEY HERE>'
    base_domain: '<INSERT BASE DOMAIN HERE>'
    deployment_release_name: '<INSERT DEPLOYMENT RELEASE NAME HERE>'
  ```
  
  5. In the `airflow-connections.yaml` update variables to match your Nebula deployment and Astro deployment
 
  - Astro Domain: From the Astronomer UI in the Astro product, this is the URL of your deployment after clicking the `Open Airflow` button (be sure to remove `/home` from the end of the URL
  - Astro Key ID: From the Astronomer UI in the Astro product, this is found in the **API Keys** section of your deployment
  - Astro Key Secret: From the Astronomer UI in the Astro product, this is found in the **API Keys** section of your deployment
  - Nebula API Key: From the Astronomer UI in the Nebula product, this is found under the **Service Accounts** section
  - Nebula Base Domain: From the Astronomer UI in the Nebula product, this is retrievable from the URL shown in your browser. Your URL will have the following format: `https://app.<BASE-DOMAIN>/w/<WORKSPACE-ID>/d/<DEPLOYMENT-RELEASE-NAME>`
  - Nebula Deployment Release Name: From the Astronomer UI in the Nebula product, this is retrievable from the URL shown in your browser. Your URL will have the following format: `https://app.<BASE-DOMAIN>/w/<WORKSPACE-ID>/d/<DEPLOYMENT-RELEASE-NAME>`

# Make Commands
- After completing setup section above, use the `make variables` command to migrate all variables
