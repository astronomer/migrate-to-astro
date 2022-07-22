import os

import pytest
import yaml
from click.testing import CliRunner
from dotenv import load_dotenv

from astro_apply.__main__ import cli
from tests.conftest import manual_tests

TEST_CONFIG = """
cktvzwx95452932byvy2vfgas9q:
  users:
    chronek@astronomer.io: WORKSPACE_ADMIN
    eric@astronomer.io: WORKSPACE_ADMIN
    fcash@astronomer.io: WORKSPACE_ADMIN
    fritz@astronomer.io: WORKSPACE_ADMIN
    kelly.walsh@astronomer.io: WORKSPACE_ADMIN
    magdalena.gultekin@astronomer.io: WORKSPACE_EDITOR
    rocco@astronomer.io: WORKSPACE_ADMIN
    shawn.mccauley@astronomer.io: WORKSPACE_ADMIN
    tonyh@astronomer.io: WORKSPACE_ADMIN
"""


# @manual_tests
@pytest.mark.skip(reason="Broke when switching to `astro auth login` auth over workspace SA token")
def test__main__fetch():
    load_dotenv()
    runner = CliRunner()
    with runner.isolated_filesystem():
        # noinspection PyTypeChecker
        result = runner.invoke(
            cli,
            [
                "fetch",
                "--basedomain",
                "gcp0001.us-east4.astronomer.io",
                "--source-workspace-id",
                "cku5ts93v10865546pinw23j7m7g",
                "--target-workspace-id",
                "cktvzwx95452932byvy2vfgas9q",
                "--output-file",
                "config.yaml",
                "--yes",
            ],
        )
        assert (
            result.exit_code == 0
        ), f"Exit Code: {result.exit_code}\n\nSTDERR:\n{result.stderr if result.stderr_bytes else ''}\n\nSTDOUT:\n{result.stdout}"

        with open("config.yaml") as f:
            actual = yaml.safe_load(f)

        expected = yaml.safe_load(TEST_CONFIG)
        assert (
            actual == expected
        ), f"Exit Code: {result.exit_code}\n\nSTDERR:\n{result.stderr if result.stderr_bytes else ''}\n\nSTDOUT:\n{result.stdout}"
