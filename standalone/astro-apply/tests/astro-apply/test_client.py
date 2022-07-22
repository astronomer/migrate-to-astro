import pytest
from gql.transport.exceptions import TransportQueryError
from pytest_mock import MockerFixture

import astro_apply
from astro_apply import houston_basedomain_to_api
from astro_apply.client import CloudClient, SoftwareClient, get_users_to_update_for_workspace
from astro_apply.constants import ASTRO_CLOUD_PRIVATE_DELETE_WORKSPACE_USER, NEBULA_BASEDOMAIN_URL
from tests.conftest import manual_tests

# thanks frank!
e2e_test_user = "frank@astronomer.io"

# https://cloud.astronomer.io/cktvzwx95452932byvy2vfgas9q/access
e2e_test_workspace_id = "cktvzwx95452932byvy2vfgas9q"

# https://app.gcp0001.us-east4.astronomer.io/w/cku5ts93v10865546pinw23j7m7g/users
e2e_nebula_customer_success_workspace_id = "cku5ts93v10865546pinw23j7m7g"


@manual_tests
def test_software_client_get_workspace_users_and_roles():
    # uses `~/.astro/config.yaml` which is gained from `astro auth login gcp0001.us-east4.astronomer.io`
    actual = SoftwareClient(url=houston_basedomain_to_api(NEBULA_BASEDOMAIN_URL)).get_workspace_users_and_roles(
        e2e_nebula_customer_success_workspace_id
    )
    expected = {
        "chronek@astronomer.io": "WORKSPACE_ADMIN",
        "eric@astronomer.io": "WORKSPACE_ADMIN",
        "fcash@astronomer.io": "WORKSPACE_ADMIN",
        "fritz@astronomer.io": "WORKSPACE_ADMIN",
        "kelly.walsh@astronomer.io": "WORKSPACE_ADMIN",
        "magdalena.gultekin@astronomer.io": "WORKSPACE_EDITOR",
        "rocco@astronomer.io": "WORKSPACE_ADMIN",
        "shawn.mccauley@astronomer.io": "WORKSPACE_ADMIN",
        "tonyh@astronomer.io": "WORKSPACE_ADMIN",
    }
    assert actual == expected


@manual_tests
def test_cloud_client_get_workspace_users_and_roles():
    client = CloudClient()
    actual = client.get_workspace_users_and_roles(e2e_test_workspace_id)
    expected = {
        "aspain@astronomer.io": "WORKSPACE_VIEWER",
        "bas@astronomer.io": "WORKSPACE_ADMIN",
        "carlos@astronomer.io": "WORKSPACE_ADMIN",
        "constance@astronomer.io": "WORKSPACE_ADMIN",
        "douglas.tonkinson@astronomer.io": "WORKSPACE_EDITOR",
        "dylan.intorf@astronomer.io": "WORKSPACE_ADMIN",
        "dylan.storey@astronomer.io": "WORKSPACE_ADMIN",
        "fcash@astronomer.io": "WORKSPACE_ADMIN",
        "fritz@astronomer.io": "WORKSPACE_ADMIN",
        "peter@astronomer.io": "WORKSPACE_ADMIN",
        "philippe@astronomer.io": "WORKSPACE_ADMIN",
    }
    assert actual == expected


@manual_tests
def test_cloud_client_e2e():
    client = CloudClient()

    # setup - test user shouldn't be here yet. Clean up just in case...
    try:
        client.delete_workspace_user(e2e_test_user, e2e_test_workspace_id)
    except RuntimeError:
        pass  # user wasn't there

    client.add_workspace_user_with_role(e2e_test_user, "WORKSPACE_VIEWER", e2e_test_workspace_id)
    user_roles_for_workspace = client.get_workspace_users_and_roles(e2e_test_workspace_id)
    assert e2e_test_user in user_roles_for_workspace, "add user - test user not found"
    assert user_roles_for_workspace[e2e_test_user] == "WORKSPACE_VIEWER", "add user - test user has wrong role"

    with pytest.raises(TransportQueryError) as e:
        client.add_workspace_user_with_role(e2e_test_user, "WORKSPACE_VIEWER", e2e_test_workspace_id)
    assert e.type is TransportQueryError, "We can't add the user twice - the API kicks us back"

    client.update_workspace_user_with_role(e2e_test_user, "WORKSPACE_ADMIN", e2e_test_workspace_id)
    user_roles_for_workspace = client.get_workspace_users_and_roles(e2e_test_workspace_id)
    assert e2e_test_user in user_roles_for_workspace, "update user - test user not found"
    assert user_roles_for_workspace[e2e_test_user] == "WORKSPACE_ADMIN", "update user - test user has wrong role"

    client.delete_workspace_user(e2e_test_user, e2e_test_workspace_id)
    user_roles_for_workspace = client.get_workspace_users_and_roles(e2e_test_workspace_id)
    assert e2e_test_user not in user_roles_for_workspace, "delete user - test user still found"

    with pytest.raises(RuntimeError) as e:
        client.delete_workspace_user(e2e_test_user, e2e_test_workspace_id)
    assert e.type is RuntimeError, "When deleting a user, we first check to see if the user is there in the first place"


def test_cloud_client_get_users_to_update_for_workspace():
    existing_users_and_roles = {
        "shared": "WORKSPACE_ADMIN",
        "shared_wrong": "WORKSPACE_ADMIN",
        "client_only": "WORKSPACE_EDITOR",
    }

    org_users = {"shared", "shared_wrong", "client_only", "config_only"}

    test_users = {
        "shared": "WORKSPACE_ADMIN",
        "shared_wrong": "WORKSPACE_VIEWER",
        "config_only": "WORKSPACE_EDITOR",
        "config_not_org": "WORKSPACE_ADMIN",
    }

    (
        actual_to_update,
        actual_to_add,
        actual_to_delete,
        actual_in_both,
        actual_unable_to_add,
    ) = get_users_to_update_for_workspace(test_users, existing_users_and_roles, org_users)

    expected_to_update = {"shared_wrong": "WORKSPACE_VIEWER"}
    assert actual_to_update == expected_to_update

    expected_to_add = {"config_only": "WORKSPACE_EDITOR"}
    assert actual_to_add == expected_to_add

    expected_to_delete = {"client_only"}
    assert actual_to_delete == expected_to_delete

    expected_in_both = {"shared", "shared_wrong"}
    assert actual_in_both == expected_in_both

    expected_unable_to_add = {"config_not_org"}
    assert actual_unable_to_add == expected_unable_to_add


def test_mock_get_user_id_from_username(mocker: MockerFixture):
    test_user_id = "abcd12345"
    test_username = "boo@baz.com"

    # noinspection PyUnusedLocal
    def mock_get_user_id_from_username(*args):
        return test_user_id

    mocker.patch.object(CloudClient, "get_user_id_from_username", mock_get_user_id_from_username)
    mocker.patch("astro_apply.client._exec")

    cc = CloudClient()
    cc.delete_workspace_user(test_username, e2e_test_workspace_id)

    # noinspection PyUnresolvedReferences
    astro_apply.client._exec.assert_called_once_with(
        cc.private_client,
        ASTRO_CLOUD_PRIVATE_DELETE_WORKSPACE_USER,
        variables={"userId": test_user_id, "workspaceId": e2e_test_workspace_id},
    ), "it calls the private client, with the DELETE sql, with the user_id fetched from  "
