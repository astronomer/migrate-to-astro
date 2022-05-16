PYTHON3=$(shell which python3)

help:
	@grep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Generate airflow-connections.yaml file
	$(PYTHON3) 'scripts/init-connections.py'

variables: ## Migrate variables from nebula to astro
	$(PYTHON3) 'scripts/migrate-variables.py'
