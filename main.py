from src.utility.models import VNetRequest, SubnetDeleteRequest, VNetDeleteRequest
from src.azure_provisioner.azure_network import (
    create_or_update_vnet, 
    delete_subnet, 
    delete_vnet
)
from src.utility.db_ops import get_vnet_data
from src.utility.logger import logger
import requests
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.middleware.cors import CORSMiddleware
from src.authentication.auth import azure_scheme
from fastapi import FastAPI, Security
from dotenv import load_dotenv
import os
import json
from fastapi import FastAPI, Depends, Query
from typing import Optional, List
from fastapi.responses import JSONResponse

load_dotenv()

AZURE_BACKENDAUTH_CLIENT_ID = os.getenv("AZURE_BACKENDAUTH_CLIENT_ID")
AZURE_FRONTEND_APP_CLIENT_ID = os.getenv("AZURE_FRONTEND_APP_CLIENT_ID")


app = FastAPI(
    title="Azure VNet Provisioner", 
    version="1.0.0",
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': AZURE_BACKENDAUTH_CLIENT_ID,
        'scopes':f'api://{AZURE_FRONTEND_APP_CLIENT_ID}/user_impersonation'
    },
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:8000'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.get("/", dependencies=[Security(azure_scheme)])
async def network_inflate_root():
    """
    Handles the root endpoint of the Azure network provisioning API.

    This endpoint is secured using Azure Active Directory authentication 
    via the `azure_scheme` dependency. When accessed, it returns a 
    message indicating that the API is operational.

    Returns:
        dict: A JSON response containing a message about the API status.
    """
    return {"message": "Azure network provisioning API in Action!"}


@app.post("/vnet/create", dependencies=[Security(azure_scheme)])
async def create_virtual_network(request: VNetRequest):
    """
    Endpoint to create or update a virtual network.
    This endpoint is secured with Azure authentication and requires a valid token.
    It processes a request to create or update a virtual network based on the 
    provided configuration.
    Args:
        request (VNetRequest): The request payload containing the virtual network 
        configuration details.
    Returns:
        dict: A dictionary containing the result of the operation. If successful, 
        it includes the details of the created or updated virtual network. If an 
        error occurs, an HTTPException is raised with a 500 status code and the 
        error details.
    Raises:
        HTTPException: If an error occurs during the creation or update process, 
        an HTTPException is raised with a 500 status code and the error message.
    """
    result = create_or_update_vnet(request)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@app.get("/vnets/data", dependencies=[Security(azure_scheme)])
async def read_vnet_data(vnet_name: Optional[str] = Query(None, alias="vnetName")):
    """
    Endpoint to retrieve virtual network (VNet) data.
    This endpoint fetches details about a specified virtual network (VNet) or all VNets if no specific name is provided.
    The data is formatted and returned as a JSON response.
    Args:
        vnet_name (Optional[str]): The name of the virtual network to retrieve. Passed as a query parameter with the alias "vnetName".
    Returns:
        JSONResponse:
            - 200: A JSON object containing the formatted VNet data.
            - 404: A JSON object with a message indicating that the VNet was not found.
            - 500: A JSON object with a message indicating an internal server error.
    Raises:
        Exception: Logs an error and returns a 500 response if an unexpected error occurs.
    Notes:
        - The `subnets` field in the VNet data is parsed from a JSON string. If the parsing fails, it defaults to an empty list.
        - The endpoint uses Azure authentication via the `azure_scheme` dependency.
    """
    try:
        result = get_vnet_data(vnet_name)

        if not result:
            return JSONResponse(status_code=404, content={"message": "VNet not found"})

        if isinstance(result, tuple):
            result = [result]

        columns = ["id", "resource_group", "vnet_name", "location", "address_space", "subnets", "status"]

        formatted = []
        for row in result:
            record = dict(zip(columns, row))
            try:
                # Fix malformed JSON (e.g. single quotes or double-escaped)
                subnets_raw = record["subnets"].replace("'", '"')
                record["subnets"] = json.loads(subnets_raw)
            except json.JSONDecodeError:
                record["subnets"] = []
            formatted.append(record)

        return {"data": formatted}

    except Exception as e:
        logger.error(f"Failed to retrieve VNet data: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})


@app.delete("/vnet/subnet/delete",dependencies=[Security(azure_scheme)])
async def delete_vnet_subnet(req: SubnetDeleteRequest):
    """
    Deletes a subnet from a specified virtual network (VNet) in a given resource group.
    This endpoint is secured using Azure authentication and requires a valid token.
    Args:
        req (SubnetDeleteRequest): The request object containing the following fields:
            - resource_group (str): The name of the resource group.
            - vnet_name (str): The name of the virtual network.
            - subnet_name (str): The name of the subnet to be deleted.
    Raises:
        HTTPException: If an error occurs during the deletion process, an HTTP 500 error is raised with the error details.
    Returns:
        dict: A dictionary containing the result of the subnet deletion operation.
    """
    
    result = delete_subnet(
        resource_group=req.resource_group,
        vnet_name=req.vnet_name,
        subnet_name=req.subnet_name
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.delete("/vnet/delete", dependencies=[Security(azure_scheme)])
async def delete_virtual_network(req: VNetDeleteRequest):
    """
    Deletes a specified virtual network.
    This endpoint allows the deletion of a virtual network within a specified resource group.
    It requires authentication using the Azure security scheme.
    Args:
        req (VNetDeleteRequest): The request object containing the resource group and virtual network name.
    Returns:
        dict: A dictionary containing the result of the deletion operation. If successful, it will
            contain details of the operation. If an error occurs, an HTTPException with status
            code 500 is raised.
    Raises:
        HTTPException: If an error occurs during the deletion process, an HTTPException is raised
                    with a status code of 500 and the error details.
    """
    result = delete_vnet(
        resource_group=req.resource_group,
        vnet_name=req.vnet_name
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
