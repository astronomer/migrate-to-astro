PYTHON3=$(shell which python3)

help:
	@grep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

migrate-variables: ## Migrate connections from nebula to astro
	$(PYTHON3) migrate-variables.py
