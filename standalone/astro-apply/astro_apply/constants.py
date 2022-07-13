ASTRO_CLOUD_API_URL = "https://api.astronomer.io/hub/graphql"  # public api
ASTRO_CLOUD_PRIVATE_API_URL = "https://api.astronomer.io/hub/v1"  # private api
ASTRO_CLOUD_BASEDOMAIN = "cloud.astronomer.io"

# From ValidateDomain, used in requestToken in https://github.com/astronomer/cloud-cli/blob/main/auth/auth.go
ASTRO_CLOUD_AUTH_DOMAIN = "https://auth.astronomer.io"
ASTRO_CLOUD_AUTH_CLIENT_ID = "5XYJZYf5xZ0eKALgBH3O08WzgfUfz7y9"
ASTRO_CLOUD_AUTH_AUDIENCE_ID = "astronomer-ee"

NEBULA_BASEDOMAIN_URL = "gcp0001.us-east4.astronomer.io"

SOFTWARE_TO_CLOUD_ROLE_MAPPINGS = {
    "WORKSPACE_ADMIN": ["WORKSPACE_ADMIN"],
    "WORKSPACE_EDITOR": ["WORKSPACE_EDITOR", "DEPLOYMENT_ADMIN", "DEPLOYMENT_EDITOR"],
    "WORKSPACE_VIEWER": ["WORKSPACE_VIEWER", "DEPLOYMENT_VIEWER"],
}

HOUSTON_WORKSPACES = """
query workspaces {
  workspaces {
    id
    label
    deployments {
      id
      label
      releaseName
    }
  }
}
"""

HOUSTON_WORKSPACE_USERS_AND_ROLES = """
query workspaceUsers($workspaceUuid: Uuid!) {
  workspaceUsers(workspaceUuid: $workspaceUuid) {
    emails {
      address
    }
    fullName
    username
    roleBindings {
      role
      workspace {
        id
      }
      deployment {
        id
        label
      }
    }
  }
}"""

HOUSTON_ENV_VARS = """
query deploymentVariables($deploymentUuid: Uuid!, $releaseName: String!) {
  deploymentVariables(deploymentUuid: $deploymentUuid, releaseName: $releaseName) {
    key
    value
    isSecret
  }
}
"""

ASTRO_CLOUD_WORKSPACES = """
query Workspaces($organizationId: Id!) {
  workspaces(organizationId: $organizationId) {
    id
    active
    description
    label
    createdAt
    updatedAt
  }
}
"""

ASTRO_CLOUD_WORKSPACES_AND_ROLES = """
query Workspaces($organizationId: Id!) {
  workspaces(organizationId: $organizationId) {
    id
    active
    description
    label
    createdAt
    updatedAt
    users {
      id
      username
      roleBindings {
        role
        workspace {
          id
        }
      }
    }
    roleBindings {
      role
      user {
        username
        id
      }
    }
  }
}
"""

ASTRO_CLOUD_PRIVATE_WORKSPACE_USERS_AND_ROLES = """
  fragment RoleBinding on RoleBinding {
    id
    role
    workspace {
      id
    }
    deployment {
      id
      label
    }
  }

  fragment WorkspaceUser on User {
    id
    fullName
    username
    avatarUrl
    roleBindings {
      ...RoleBinding
    }
    createdAt
  }

  query workspaceUsers($workspaceId: Id!) {
    workspaceUsers(workspaceId: $workspaceId) {
      ...WorkspaceUser
    }
  }
"""

ASTRO_CLOUD_ORGANIZATIONS = """
query Organizations {
  organizations {
    id
    name
  }
}
"""

ASTRO_CLOUD_SELF = """
  fragment RoleBinding on RoleBinding {
    id
    role
    workspace {
      id
    }
    deployment {
      id
      label
    }
  }

  fragment AuthZRoleBinding on AuthZRoleBinding {
    role {
      name
    }
    scope {
      type
      entityId
    }
  }


  fragment SelfUser on User {
    id
    username
    roleBindings {
      ...RoleBinding
    }
    roles {
      ...AuthZRoleBinding
    }
    avatarUrl
    fullName
    featureFlags
  }

  fragment Self on AuthUser {
    user {
      ...SelfUser
    }
    authenticatedOrganizationId
  }

  query self {
    self {
      ...Self
    }
  }
"""

ASTRO_CLOUD_PRIVATE_WORKSPACES = """
  fragment WorkspaceCapabilities on WorkspaceCapabilities {
    canUpdateIAM
    canUpdateWorkspace
    canDeleteWorkspace
    canCreateDeployment
    canUserInviteCreate
    canUpdateUser
    canDeleteUser
  }

  fragment Workspace on Workspace {
    id
    active
    description
    properties
    label
    deployments {
      id
      status
    }
    createdAt
    updatedAt
    organization {
      id
      name
      shortName
    }
    workspaceCapabilities {
      ...WorkspaceCapabilities
    }
    users {
      id
    }
  }

  query workspaces {
    workspaces {
      ...Workspace
    }
  }
"""

ASTRO_CLOUD_PRIVATE_ADD_WORKSPACE_USER_WITH_ROLE = """
mutation workspaceUserRoleCreate(
    $workspaceId: Id
    $email: String!
    $role: Role! = WORKSPACE_VIEWER
    $deploymentRoles: [DeploymentRoles!]
) {
    workspaceUserRoleCreate(
        workspaceId: $workspaceId
        email: $email
        role: $role
        deploymentRoles: $deploymentRoles
    ) {
        id
    }
}
"""

ASTRO_CLOUD_PRIVATE_UPDATE_WORKSPACE_USER_ROLE = """
  mutation workspaceUserRoleUpdate($workspaceId: Id!, $email: String!, $role: Role!) {
    workspaceUserRoleUpdate(workspaceId: $workspaceId, email: $email, role: $role)
  }
"""

ASTRO_CLOUD_PRIVATE_DELETE_WORKSPACE_USER = """
  mutation workspaceUserRoleDelete($workspaceId: Id!, $userId: Id!) {
    workspaceUserRoleDelete(workspaceId: $workspaceId, userId: $userId) {
      id
    }
  }
"""

ASTRO_CLOUD_WORKSPACE_USERS_AND_IDS = """
query WorkspaceUsers($workspaceUsersId: Id!) {
  workspaceUsers(id: $workspaceUsersId) {
    id
    username
  }
}
"""


ASTRO_CLOUD_PRIVATE_UPDATE_ENV_VARS = """
  fragment EnvironmentVariable on EnvironmentVariable {
    key
    value
    isSecret
    updatedAt
  }

  mutation deploymentVariablesUpdate($input: EnvironmentVariablesInput!) {
    deploymentVariablesUpdate(input: $input) {
      ...EnvironmentVariable
    }
  }
"""

ASTRO_CLOUD_PRIVATE_DEPLOYMENT_SPEC = """
  fragment EnvironmentVariable on EnvironmentVariable {
    key
    value
    isSecret
    updatedAt
  }

  fragment DeploymentSpec on DeploymentSpec {
    executor
    scheduler {
      au
      replicas
      cpuMillis
      memoryMiB
    }
    workers {
      au
      cpuMillis
      memoryMiB
    }
    environmentVariablesObjects {
      ...EnvironmentVariable
    }
    image {
      tag
    }
    updatedAt
  }

  query deploymentsSpec($input: DeploymentsInput) {
    deployments(input: $input) {
      id
      deploymentSpec {
        ...DeploymentSpec
      }
    }
  }
"""

ASTRO_CLOUD_PRIVATE_ORG_USERS = """  
  fragment AuthZRoleBinding on AuthZRoleBinding {
    role {
      name
    }
    scope {
      type
      entityId
    }
  }

  fragment User on User {
    id
    fullName
    username
    avatarUrl
    roles {
      ...AuthZRoleBinding
    }
    createdAt
  }

  query users($organizationId: Id) {
    users(organizationId: $organizationId) {
      ...User
    }
  }
"""
