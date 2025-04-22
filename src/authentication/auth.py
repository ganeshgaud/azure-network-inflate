from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_FRONTEND_APP_CLIENT_ID = os.getenv("AZURE_FRONTEND_APP_CLIENT_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_BACKEND_APP_CLIENT_ID = os.getenv("AZURE_BACKEND_APP_CLIENT_ID")
AZURE_BACKEND_APP_SECRET = os.getenv("AZURE_BACKEND_APP_SECRET")
AZURE_SUBSCRITION_ID = os.getenv("AZURE_SUBSCRITION_ID")

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id = AZURE_FRONTEND_APP_CLIENT_ID,
    tenant_id = os.getenv("AZURE_TENANT_ID"),
    scopes={f'api://{AZURE_FRONTEND_APP_CLIENT_ID}/user_impersonation':'user_impersonation'},
    allow_guest_users=True
)

def get_cred_context():
    """
    Creates and returns a credential context using Azure's ClientSecretCredential.

    This function initializes a ClientSecretCredential object with the provided
    Azure tenant ID, client ID, and client secret. The credential can be used
    to authenticate and authorize requests to Azure services.

    Returns:
        ClientSecretCredential: An instance of ClientSecretCredential configured
        with the specified tenant ID, client ID, and client secret.
    """
    credential = ClientSecretCredential(
        tenant_id = AZURE_TENANT_ID,
        client_id = AZURE_BACKEND_APP_CLIENT_ID,
        client_secret = AZURE_BACKEND_APP_SECRET
    )
    return credential
    

def get_network_client():
    """
    Creates and returns an instance of the Azure NetworkManagementClient.

    This function retrieves the Azure subscription ID and credentials 
    to initialize the NetworkManagementClient, which is used to manage 
    Azure network resources.

    Returns:
        NetworkManagementClient: An instance of the Azure NetworkManagementClient 
        initialized with the provided credentials and subscription ID.
    """
    subscription_id = AZURE_SUBSCRITION_ID
    credential = get_cred_context()
    return NetworkManagementClient(credential, subscription_id)

def get_resource_client():
    """
    Creates and returns an instance of the ResourceManagementClient.

    This function initializes a ResourceManagementClient using the Azure subscription ID
    and credentials obtained from the current credential context.

    Returns:
        ResourceManagementClient: An instance of the Azure ResourceManagementClient
        configured with the provided subscription ID and credentials.
    """
    subscription_id = AZURE_SUBSCRITION_ID
    credential = get_cred_context()
    return ResourceManagementClient(credential, subscription_id)