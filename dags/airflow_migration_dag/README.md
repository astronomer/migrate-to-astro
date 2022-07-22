# Airflow Migration DAG

This DAG can be used to facilitate automating the migration of metadata from one Airflow instance to either Astronomer Software or Astro.

## Requirements

The Airflow Migration DAG requires several configuration items in order to create connections and variables in the destination Airflow environment:

1. Airflow API Credentials
2. Destination Airflow URL

Retrieving the required configuration depends on the Astronomer platform that the destination Airflow is deployed in. The different methods are described in the configuration steps below.

## Migrating to Astro

### Step 1: Creating Airflow API Credentials

For Airflow API credentials in Astro, we need to create a Deployment API Key. Follow these steps:

1. Open your Deployment in the Cloud UI
2. In the **API Keys** menu, click **Add API Key**
3. Give the key a name and description, then click **Create API Key**
4. Copy the values for the **API Key ID** and **Secret** and save them somewhere safe

[see documentation](https://docs.astronomer.io/astro/api-keys#create-an-api-key)

### Step 2: Retrieving the Destination Airflow URL

To retrieve your Deployment URL:

1. Open your Deployment in the Cloud UI
2. Click **Open Airflow**
3. Copy the URL for the Airflow UI and save it somewhere, this is your Destination Airflow URL

> The URL includes the name of your Organization and a short Deployment ID. For example, your Deployment URL will look similar to `https://mycompany.astronomer.run/dhbhijp0`.

### Step 3: Configuring the DAG

The DAG can be configured in one of two ways, either through environment variables or triggering the DAG with config. Below are examples of both configurations:

To configure with environment variables:

```ini
ASTRONOMER_KEY_ID=<ASTRONOMER_KEY_ID>
ASTRONOMER_KEY_SECRET=<ASTRONOMER_KEY_SECRET>
DESTINATION_AIRFLOW_URL=<DESTINATION_AIRFLOW_URL>

# migrate metadata to s3
DESTINATION_AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
DESTINATION_AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
DESTINATION_S3_BUCKET=<S3_BUCKET>
DESTINATION_S3_KEY_PATH=<S3_KEY_PATH> # defaults to root of bucket

# migrate metadata to db
DESTINATION_PG_USER=<PG_USER>
DESTINATION_PG_PASS=<PG_PASS>
DESTINATION_PG_HOST=<PG_HOST>
DESTINATION_PG_PORT=<PG_PORT> # defaults to 5432
```

To configure with a DagRun trigger config:

```json
{
  "ASTRONOMER_KEY_ID": "<ASTRONOMER_KEY_ID>",
  "ASTRONOMER_KEY_SECRET": "<ASTRONOMER_KEY_SECRET>",
  "DESTINATION_AIRFLOW_URL": "<DESTINATION_AIRFLOW_URL>",

  // migrate metadata to s3
  "DESTINATION_AWS_ACCESS_KEY_ID": "<AWS_ACCESS_KEY_ID>",
  "DESTINATION_AWS_SECRET_ACCESS_KEY": "<AWS_SECRET_ACCESS_KEY>",
  "DESTINATION_S3_BUCKET": "<S3_BUCKET>",
  "DESTINATION_S3_KEY_PATH": "<S3_KEY_PATH>", // defaults to root of bucket

  // migrate metadata to db
  "DESTINATION_PG_USER": "<PG_USER>",
  "DESTINATION_PG_PASS": "<PG_PASS>",
  "DESTINATION_PG_HOST": "<PG_HOST>",
  "DESTINATION_PG_PORT": "<PG_PORT>", // defaults to 5432
}
```

## Migrating to Software

### Step 1: Creating Airflow API Credentials

For Airflow API credentials in Software, we need to create a Deployment Service Account. Follow these steps:

1. Log in to the Software UI
2. Go to **Deployment** > **Service Accounts**
3. Give your Service Account a **Name**, **User Role** *(Deployment Admin)*, and **Category** *(Optional)*
4. Copy the API Key that was generated and save it somewhere safe

[see documentation](https://docs.astronomer.io/software/airflow-api#step-1-create-a-service-account-on-astronomer)

### Step 2: Retrieving the Destination Airflow URL

To retrieve your Deployment URL:

1. Open your Deployment in the Astro UI
2. Click **Open Airflow**
3. Copy the URL for the Airflow UI up to `/airflow` and save it somewhere, this is your Destination Airflow URL

> The URL includes the Astronomer base domain and the Airflow deployment release name. Be sure to capture the entire URL up to `/airflow`. For example, your Deployment URL will look similar to `https://deployments.astro.mycompany.io/galactic-stars-1234/airflow`.

### Step 3: Configuring the DAG

The DAG can be configured in one of two ways, either through environment variables or triggering the DAG with config. Below are examples of both configurations:

To configure with environment variables:

```ini
ASTRONOMER_API_KEY=<DEPLOYMENT_SERVICE_ACCOUNT_KEY>
DESTINATION_AIRFLOW_URL=<DESTINATION_AIRFLOW_URL>

# migrate metadata to s3
DESTINATION_AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
DESTINATION_AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
DESTINATION_S3_BUCKET=<S3_BUCKET>
DESTINATION_S3_KEY_PATH=<S3_KEY_PATH> # defaults to root of bucket

# migrate metadata to db
DESTINATION_PG_USER=<PG_USER>
DESTINATION_PG_PASS=<PG_PASS>
DESTINATION_PG_HOST=<PG_HOST>
DESTINATION_PG_PORT=<PG_PORT> # defaults to 5432
```

To configure with a DagRun trigger config:

```json
{
  "ASTRONOMER_API_KEY": "<DEPLOYMENT_SERVICE_ACCOUNT_KEY>",
  "DESTINATION_AIRFLOW_URL": "<DESTINATION_AIRFLOW_URL>",

  // migrate metadata to s3
  "DESTINATION_AWS_ACCESS_KEY_ID": "<AWS_ACCESS_KEY_ID>",
  "DESTINATION_AWS_SECRET_ACCESS_KEY": "<AWS_SECRET_ACCESS_KEY>",
  "DESTINATION_S3_BUCKET": "<S3_BUCKET>",
  "DESTINATION_S3_KEY_PATH": "<S3_KEY_PATH>", // defaults to root of bucket

  // migrate metadata to db
  "DESTINATION_PG_USER": "<PG_USER>",
  "DESTINATION_PG_PASS": "<PG_PASS>",
  "DESTINATION_PG_HOST": "<PG_HOST>",
  "DESTINATION_PG_PORT": "<PG_PORT>", // defaults to 5432
}
```
