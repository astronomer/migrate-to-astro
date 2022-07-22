#!/usr/bin/env bash

set -euo pipefail

# clean up
rm -rf slowtest config.yaml

# install
python -m venv slowtest
source slowtest/bin/activate

(set -x; pip install git+https://github.com/astronomer/astro-apply.git#egg=astro-apply)

# source .env
export $(grep -v '^#' .env | xargs)

# https://app.gcp0001.us-east4.astronomer.io/w/cku5ts93v10865546pinw23j7m7g/users
# https://cloud.astronomer.io/cl1pjmnpr63981fyo4whfab04/access
# fetch
(set -x; astro-apply fetch --source-workspace-id cku5ts93v10865546pinw23j7m7g --target-workspace-id cl1pjmnpr63981fyo4whfab04 --yes)

# apply
(set -x; astro-apply apply --yes)

# cleanup
rm -rf slowtest config.yaml
