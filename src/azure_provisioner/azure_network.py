from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

import json
from src.utility.models import VNetRequest, SubnetRequest
from src.authentication.auth import get_network_client, get_resource_client
from src.utility.logger import logger
from src.utility.db_ops import (
    insert_vnet_data,
    update_vnet_data,
    get_vnet_data,
    delete_vnet_data,
    delete_subnet_data
)


def create_or_update_vnet(req: VNetRequest) -> dict:
    """
    Creates or updates an Azure Virtual Network (VNet) and its associated subnets.
    This function ensures that the specified resource group exists, creates or updates
    the VNet within the resource group, and manages its subnets. If the VNet or subnets
    already exist, it verifies their configurations and updates them if necessary.
    Args:
        req (VNetRequest): An object containing the details of the VNet to be created or updated.
            Attributes of `req` include:
                - resource_group (str): The name of the resource group.
                - location (str): The Azure region where the VNet will be created.
                - vnet_name (str): The name of the Virtual Network.
                - address_prefix (str): The address space for the VNet.
                - subnets (list): A list of subnet configurations, where each subnet has:
                    - name (str): The name of the subnet.
                    - address_prefix (str): The address prefix for the subnet.
    Returns:
        dict: A dictionary containing details of the created or updated VNet, including:
            - vnet_name (str): The name of the VNet.
            - location (str): The Azure region of the VNet.
            - subnets (list): A list of subnet names within the VNet.
    Raises:
        HttpResponseError: If an Azure API call fails.
        ResourceNotFoundError: If a required resource is not found.
        Exception: For any other unexpected errors.
    Notes:
        - The function logs the progress of resource creation and updates.
        - If the VNet or subnets already exist with the correct configuration, no changes are made.
        - Updates to the VNet or subnets are performed only if discrepancies are detected.
    """
    try:
        net_client = get_network_client()
        res_client = get_resource_client()

        resource_groups = res_client.resource_groups.list()
        rg_names = [rg.name for rg in resource_groups]

        if req.resource_group not in rg_names:
            logger.info(f"Creating resource group: {req.resource_group}")
            res_client.resource_groups.create_or_update(
                req.resource_group, {"location": req.location}
            )

        vnets = net_client.virtual_networks.list(req.resource_group)
        vnet_names = [vnet.name for vnet in vnets]

        if req.vnet_name in vnet_names:
            logger.info(f"VNet '{req.vnet_name}' already exists. Checking subnets...")

            vnet = net_client.virtual_networks.get(req.resource_group, req.vnet_name)
            existing_subnet_map = {
                subnet.name: subnet.address_prefix for subnet in vnet.subnets
            }

            for sn in req.subnets:
                if sn.name not in existing_subnet_map:
                    logger.info(f"Creating new subnet '{sn.name}'...")
                    net_client.subnets.begin_create_or_update(
                        req.resource_group,
                        req.vnet_name,
                        sn.name,
                        {"address_prefix": sn.address_prefix}
                    ).result()
                elif existing_subnet_map[sn.name] != sn.address_prefix:
                    logger.info(f"Updating subnet '{sn.name}' with new address prefix...")
                    net_client.subnets.begin_create_or_update(
                        req.resource_group,
                        req.vnet_name,
                        sn.name,
                        {"address_prefix": sn.address_prefix}
                    ).result()
                else:
                    logger.info(f"Subnet '{sn.name}' already exists with correct address prefix. Skipping.")
            
            update_vnet_data(req.json())
            vnet = net_client.virtual_networks.get(req.resource_group, req.vnet_name)

        else:
            logger.info(f"Creating new VNet '{req.vnet_name}' with all subnets...")
            vnet = net_client.virtual_networks.begin_create_or_update(
                resource_group_name=req.resource_group,
                virtual_network_name=req.vnet_name,
                parameters={
                    "location": req.location,
                    "address_space": {"address_prefixes": [req.address_prefix]},
                    "subnets": [
                        {"name": sn.name, "address_prefix": sn.address_prefix}
                        for sn in req.subnets
                    ]
                }
            ).result()
            insert_vnet_data(req.json())
        return {
            "vnet_name": vnet.name,
            "location": vnet.location,
            "subnets": [subnet.name for subnet in vnet.subnets],
        }

    except HttpResponseError as e:
        logger.error(f"Azure API call failed: {e.message}")
        return {"error": f"Azure API call failed: {e.message}"}
    except ResourceNotFoundError as e:
        logger.error(f"Resource not found: {e.message}")
        return {"error": f"Resource not found: {e.message}"}
    except Exception as ex:
        logger.exception("Unexpected error occurred")
        return {"error": f"Unexpected error: {str(ex)}"}


def delete_subnet(resource_group: str, vnet_name: str, subnet_name: str) -> dict:
    """
    Deletes a specified subnet from a virtual network (VNet) in a given resource group.
    Args:
        resource_group (str): The name of the Azure resource group containing the VNet.
        vnet_name (str): The name of the virtual network (VNet) from which the subnet will be deleted.
        subnet_name (str): The name of the subnet to delete.
    Returns:
        dict: A dictionary containing a success message if the subnet was deleted successfully,
              or an error message if the operation failed.
    Raises:
        ResourceNotFoundError: If the specified resource group or VNet does not exist.
        HttpResponseError: If there is an issue with the HTTP request during the deletion process.
        Exception: For any unexpected errors that occur during the operation.
    Notes:
        - This function checks if the specified subnet exists in the VNet before attempting to delete it.
        - If the subnet does not exist, a message indicating this is returned.
        - Logs are generated for both successful and failed operations.
    """
    try:
        net_client = get_network_client()
        logger.info(f"Attempting to delete subnet '{subnet_name}' in VNet '{vnet_name}'...")

        vnet = net_client.virtual_networks.get(resource_group, vnet_name)
        existing_subnet_names = {subnet.name for subnet in vnet.subnets}

        if subnet_name not in existing_subnet_names:
            return {"message": f"Subnet '{subnet_name}' does not exist in VNet '{vnet_name}'."}

        net_client.subnets.begin_delete(
            resource_group_name=resource_group,
            virtual_network_name=vnet_name,
            subnet_name=subnet_name
        ).result()
        delete_subnet_data(resource_group, vnet_name)
        return {"message": f"Subnet '{subnet_name}' has been successfully deleted from VNet '{vnet_name}'."}

    except ResourceNotFoundError:
        logger.error(f"Resource group '{resource_group}' or VNet '{vnet_name}' not found.")
        return {"error": f"Resource group '{resource_group}' or VNet '{vnet_name}' not found."}
    except HttpResponseError as e:
        logger.error(f"Failed to delete subnet: {e.message}")
        return {"error": f"Failed to delete subnet: {e.message}"}
    except Exception as ex:
        logger.exception("Unexpected error during subnet deletion")
        return {"error": f"Unexpected error: {str(ex)}"}


def delete_vnet(resource_group: str, vnet_name: str) -> dict:
    """
    Deletes a virtual network (VNet) from a specified resource group in Azure.
    Args:
        resource_group (str): The name of the Azure resource group containing the VNet.
        vnet_name (str): The name of the VNet to be deleted.
    Returns:
        dict: A dictionary containing a message or error details. 
              Example:
              - On success: {"message": "VNet '<vnet_name>' successfully deleted from resource group '<resource_group>'."}
              - If VNet does not exist: {"message": "VNet '<vnet_name>' does not exist in resource group '<resource_group>'."}
              - On error: {"error": "<error_message>"}
    Raises:
        ResourceNotFoundError: If the specified resource group or VNet is not found.
        HttpResponseError: If there is an HTTP response error during the deletion process.
        Exception: For any unexpected errors during the operation.
    Notes:
        - This function uses the Azure SDK to interact with Azure resources.
        - The `delete_vnet_data` function is called to perform additional cleanup after the VNet is deleted.
        - Logs are generated for informational and error tracking purposes.
    """
    try:
        net_client = get_network_client()
        logger.info(f"Attempting to delete VNet '{vnet_name}'...")

        vnets = net_client.virtual_networks.list(resource_group)
        vnet_names = [vnet.name for vnet in vnets]

        if vnet_name not in vnet_names:
            return {"message": f"VNet '{vnet_name}' does not exist in resource group '{resource_group}'."}

        net_client.virtual_networks.begin_delete(
            resource_group_name=resource_group,
            virtual_network_name=vnet_name
        ).result()
        delete_vnet_data(vnet_name)
        return {"message": f"VNet '{vnet_name}' successfully deleted from resource group '{resource_group}'."}

    except ResourceNotFoundError:
        logger.error(f"Resource group '{resource_group}' or VNet '{vnet_name}' not found.")
        return {"error": f"Resource group '{resource_group}' or VNet '{vnet_name}' not found."}
    except HttpResponseError as e:
        logger.error(f"Failed to delete VNet: {e.message}")
        return {"error": f"Failed to delete VNet: {e.message}"}
    except Exception as ex:
        logger.exception("Unexpected error during VNet deletion")
        return {"error": f"Unexpected error: {str(ex)}"}
