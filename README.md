# Overview
This repository is meant to contain scripts to assist customers moving from Nebula to Astro. See usage instructions below

# Pre-requisites
- Python 3

# Setup
  1. Use the command `git clone git@github.com:astronomer/cs-utility-nebula-to-astro.git` to clone this repo
  2. Use the command `cd cs-utility-nebula-to-astro` to change your working directory
  3. Run the `make init` command to generate the `airflow-connections.yaml` file
  4. In the `airflow-connections.yaml` update variables to match your Nebula deployment and Astro deployment
 
  - Astro Domain: From the Astronomer UI in the Astro product, this is the URL of your deployment after clicking the `Open Airflow` button (be sure to remove `/home` from the end of the URL
  - Astro Key ID: From the Astronomer UI in the Astro product, this is found in the **API Keys** section of your deployment
  - Astro Key Secret: From the Astronomer UI in the Astro product, this is found in the **API Keys** section of your deployment
  - Nebula API Key: From the Astronomer UI in the Nebula product, this is found under the **Service Accounts** section
  - Nebula Base Domain: From the Astronomer UI in the Nebula product, this is retrievable from the URL shown in your browser. Your URL will have the following format: `https://app.<BASE-DOMAIN>/w/<WORKSPACE-ID>/d/<DEPLOYMENT-RELEASE-NAME>`
  - Nebula Deployment Release Name: From the Astronomer UI in the Nebula product, this is retrievable from the URL shown in your browser. Your URL will have the following format: `https://app.<BASE-DOMAIN>/w/<WORKSPACE-ID>/d/<DEPLOYMENT-RELEASE-NAME>`

# Make Commands
*After completing the setup section above, you may use the following make commands:*
- Use the `make check-providers` command to view which providers are missing in your target environment
- Use the `make connections` command to migrate all connections. **Please note that this does not migrate the password field. Each migrated connection will require manually adding the password field**
- Use the `make pools` command to migrate all pools
- Use the `make variables` command to migrate all variables
