from pathlib import Path

import click
import deepmerge
import yaml
from click import UsageError
from click.exceptions import Exit
from dotenv import load_dotenv
from gql.transport.exceptions import TransportQueryError

from astro_apply import (
    add_users,
    confirm_or_exit,
    delete_users,
    echo_existing_users,
    get_config_from_users_and_roles,
    houston_basedomain_to_api,
    update_users,
)
from astro_apply.client import CloudClient, SoftwareClient, get_users_to_update_for_workspace
from astro_apply.constants import ASTRO_CLOUD_API_URL, ASTRO_CLOUD_BASEDOMAIN, NEBULA_BASEDOMAIN_URL

d = {"show_default": True, "show_envvar": True}
fd = {"show_default": True, "show_envvar": True, "is_flag": True}
rp = {"prompt": True, "required": True}

DEFAULT_FILE = "config.yaml"


@click.group()
@click.version_option()
def cli():
    """astro-apply - like kubectl apply but for Astronomer Cloud"""
    pass


@cli.command()
@click.option(
    "--target-workspace-id",
    **rp,
    **d,
    help="Target Workspace ID - should look something like cku5ts93v10865546pinw23j7m7g",
)
@click.option(
    "--source-workspace-id",
    **rp,
    **d,
    help="Source Workspace ID - should look something like cku5ts93v10865546pinw23j7m7g",
)
@click.option(
    "--basedomain",
    "-d",
    default=NEBULA_BASEDOMAIN_URL,
    **d,
    help="e.g. example.com if you access astronomer via https://app.example.com. "
    "If empty - defaults to Nebula. "
    "Can be cloud.astronomer.io to fetch from Astronomer Cloud",
)
@click.option(
    "--output-file",
    "-f",
    **d,
    type=click.Path(dir_okay=False, writable=True),
    help="Output file to write to or merge with",
)
@click.option(
    "--workspace-service-account-token",
    "-t",
    **d,
    help="Workspace Service Account Token - uses `astro auth login` config, if not given",
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompts")
def fetch(
    target_workspace_id: str,
    source_workspace_id: str,
    basedomain: str,
    output_file: str,
    workspace_service_account_token: str,
    yes: bool,
):
    """Fetch existing configuration from an Astronomer workspace"""
    if basedomain in ASTRO_CLOUD_BASEDOMAIN:
        client = CloudClient()
        url = ASTRO_CLOUD_API_URL
    else:
        url = houston_basedomain_to_api(basedomain)
        client = SoftwareClient(url, workspace_service_account_token)

    if output_file is None:
        if yes:
            output_file = DEFAULT_FILE
        else:
            output_file = click.prompt(
                text="Output file",
                default=DEFAULT_FILE,
                type=click.Path(dir_okay=False, writable=True),
                value_proc=click.Path(dir_okay=False, writable=True),
            )

    confirm_or_exit(
        f"Querying {url} for Workspace '{source_workspace_id}' configurations, saving to {output_file} - Continue?", yes
    )

    workspaces = client.get_workspaces().get("workspaces", {})
    all_deployments = [
        {
            "workspace_id": workspace.get("id"),
            "workspace_label": workspace.get("label"),
            "deployment_id": deployment.get("id"),
            "deployment_label": deployment.get("label"),
            "deployment_release_name": deployment.get("releaseName"),
        }
        for workspace in workspaces
        for deployment in workspace.get("deployments")
        if source_workspace_id == workspace.get("id")
    ]

    if source_workspace_id not in [_d["workspace_id"] for _d in all_deployments]:
        click.echo(f"Unable to find {source_workspace_id}, exiting!")
        raise Exit(1)
    else:
        ws_label = [_d["workspace_label"] for _d in all_deployments][0]
        click.echo(f"Found {source_workspace_id} as {ws_label}, with {len(all_deployments)} deployments")

    try:
        users_and_roles = client.get_workspace_users_and_roles(source_workspace_id)
        users_and_roles_sample = ", ".join([f"{u}: {r}" for u, r in list(users_and_roles.items())[:3]])
    except TransportQueryError as e:
        raise UsageError(str(e)) from e

    confirm_or_exit(f"Found {len(users_and_roles)} users and roles - {users_and_roles_sample}, ... - Continue?", yes)

    partial_config = get_config_from_users_and_roles(target_workspace_id, users_and_roles)
    if Path(output_file).exists():
        click.echo(f"Found existing content at {output_file}, merging content for Workspace '{source_workspace_id}'...")
        with click.open_file(output_file, mode="r") as f:
            config = deepmerge.always_merger.merge(yaml.safe_load(f), partial_config)
    else:
        click.echo(f"Writing content for Workspace '{source_workspace_id}' to {output_file}...")
        config = partial_config

    if basedomain not in ASTRO_CLOUD_BASEDOMAIN:
        for deployment in all_deployments:
            env_filename = f".{deployment['deployment_label'].replace(' ', '-').lower()}-env"
            env_vars = client.get_env_vars(
                deployment_uuid=deployment["deployment_id"], release_name=deployment["deployment_release_name"]
            )
            if len(env_vars):
                if yes or click.confirm(f"Save Astronomer Environmental Variables to {env_filename}?"):
                    with click.open_file(env_filename, "w", lazy=True) as f:
                        f.writelines(f"{v['key']}={v['value']}\n" for v in env_vars)
                    click.echo(
                        f"Saved {len(env_vars)} Astronomer Environmental Variables to {env_filename} - "
                        f"Make sure to fill in Secret values, as they will be blank!"
                    )
                else:
                    click.echo(f"Not saving Astronomer Environmental Variables to {env_filename}!")
            else:
                click.echo(f"No Astronomer Environmental Variables found to save to {env_filename} ... skipping...")

    with click.open_file(output_file, mode="w") as f:
        yaml.safe_dump(config, f)
    click.echo(f"Wrote to {output_file}!")


@cli.command()
@click.option(
    "--input-file",
    "-f",
    **d,
    type=click.Path(dir_okay=False, readable=True, exists=True),
    help="Input configuration file to read - see README.md for a sample",
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompts")
def apply(input_file: str, yes: bool):
    """Apply a configuration to an Astronomer Cloud workspaces"""

    if input_file is None:
        if yes:
            input_file = DEFAULT_FILE
        else:
            input_file = click.prompt(
                text="Input file",
                default=DEFAULT_FILE,
                type=click.Path(dir_okay=False, readable=True, exists=True),
                value_proc=click.Path(dir_okay=False, readable=True, exists=True),
            )

    with open(input_file) as f:
        config = yaml.safe_load(f)

    if not config or not len(config.keys()):
        raise UsageError(f"{input_file} is empty or an error occurred, exiting!")

    client = CloudClient()

    click.echo(f"Applying {input_file} and {len(config.keys())} workspace(s)...")

    for workspace_id, contents in config.items():
        config_users_and_roles = contents["users"]
        config_users_and_roles_sample = ", ".join([f"{u}: {r}" for u, r in list(config_users_and_roles.items())[:3]])

        confirm_or_exit(
            f"Found {len(config_users_and_roles)} users and roles in {input_file} - "
            f"{config_users_and_roles_sample}, ... - Continue?",
            yes,
        )

        _self = client.get_self()
        authenticated_organization_id = _self.get("self", {}).get("authenticatedOrganizationId")
        if not authenticated_organization_id:
            click.echo(
                "Unable to get 'authenticatedOrganizationId' from 'self' - "
                "possibly re-run `astrocloud auth login` or report a Github Issue?"
            )
            raise Exit(1)

        org_users = set(client.get_org_users_and_roles(organization_id=authenticated_organization_id).keys())

        existing_users_and_roles = client.get_workspace_users_and_roles(workspace_id)

        (
            users_to_update,
            users_to_add,
            users_to_delete,
            users_in_both,
            users_unable_to_add,
        ) = get_users_to_update_for_workspace(config_users_and_roles, existing_users_and_roles, org_users)

        echo_existing_users(users_in_both)
        echo_existing_users(
            users_unable_to_add, "unable to be added (no user account in Organization, probably need to log in)"
        )

        update_users(client, users_to_update, workspace_id, yes)

        add_users(client, users_to_add, workspace_id, yes)

        delete_users(users_to_delete, client, workspace_id, yes)


if __name__ == "__main__":
    # https://click.palletsprojects.com/en/8.1.x/options/#values-from-environment-variables
    load_dotenv()
    cli(auto_envvar_prefix="ASTRO_APPLY")
