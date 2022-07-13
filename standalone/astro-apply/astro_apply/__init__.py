from typing import Dict, Set

import click
import yaml
from click.exceptions import Exit

from astro_apply.client import CloudClient


def confirm_or_exit(msg: str, yes: bool = False) -> None:
    if not (yes or click.confirm(msg)):
        click.echo("Exiting...")
        raise Exit(1)


def houston_basedomain_to_api(source_basedomain: str) -> str:
    return f"https://houston.{source_basedomain}/v1"


def get_config_from_users_and_roles(
    workspace_id: str, users_and_roles: Dict[str, str]
) -> Dict[str, Dict[str, Dict[str, str]]]:
    r"""Creates config.yaml structure from a dump of username to workspace roles, for a given workspace
    :param workspace_id:
    :param users_and_roles:
    :return:
    >>> yaml.dump(get_config_from_users_and_roles(workspace_id="workspace_abcd1234", users_and_roles={"username_a": "WORKSPACE_ADMIN", "username_b": "WORKSPACE_EDITOR", "username_c": "WORKSPACE_VIEWER"}))
    'workspace_abcd1234:\n  users:\n    username_a: WORKSPACE_ADMIN\n    username_b: WORKSPACE_EDITOR\n    username_c: WORKSPACE_VIEWER\n'
    """
    return {workspace_id: {"users": users_and_roles}}


def echo_existing_users(users: Set[str], msg: str = "in both") -> None:
    if len(users):
        click.echo(f"Found {len(users)} users {msg}: {users}")


def update_users(_client: CloudClient, users_to_update: Dict[str, str], workspace_id: str, yes: bool) -> None:
    if len(users_to_update) and (
        yes or click.confirm(f"Found {len(users_to_update)} users to update: {users_to_update} - Continue?")
    ):
        for user, role in users_to_update.items():
            click.echo(f"Updating user: {user} with role: {role}")
            _client.update_workspace_user_with_role(user, role, workspace_id)


def add_users(_client: CloudClient, users_to_add: Dict[str, str], workspace_id: str, yes: bool) -> None:
    if len(users_to_add) and (
        yes or click.confirm(f"Found {len(users_to_add)} users to add: {users_to_add} - Continue?")
    ):
        for user, role in users_to_add.items():
            click.echo(f"Adding user: {user} with role: {role}")
            _client.add_workspace_user_with_role(user, role, workspace_id)


def delete_users(users_to_delete: Set[str], _client: CloudClient, workspace_id: str, yes: bool) -> None:
    if len(users_to_delete) and (
        yes or click.confirm(f"Found {len(users_to_delete)} users in to delete: {users_to_delete} - Continue?")
    ):
        for user in users_to_delete:
            click.echo(f"Deleting user: {user}")
            _client.delete_workspace_user(user, workspace_id)
