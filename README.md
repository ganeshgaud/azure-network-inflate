# azure-network-inflate

This project, **azure-network-inflate**, is designed to simplify and automate the process of managing Azure network configurations. It provides tools and scripts to streamline network setup, scaling, and optimization.

## Features

- Automates Azure network resource creation.
- Supports scaling and optimization of network configurations.
- Provides detailed logging and error handling.
- Easy-to-use and customizable scripts.

## Prerequisites

Before using this project, ensure you have the following:

- An active Azure subscription.
- Service principals for both frontend and backend authentication.
- Create .env file at root level
- A `.env` configuration file with the following variables:
    ```bash
    AZURE_FRONTEND_APP_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AZURE_TENANT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AZURE_BACKEND_APP_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AZURE_BACKEND_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AZURE_SUBSCRIPTION_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AZURE_BACKENDAUTH_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```
- Python 3.8 or higher (if you plan to use the provided scripts).


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/azure-network-inflate.git
    cd azure-network-inflate
    ```

2. Install dependencies (if applicable):
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Configure your Azure credentials and subscription.
2. Run the main script or command:
    ```bash
    uvicorn main:app --reload
    ```

# Azure VNet Provisioner API Set

This API set provides endpoints for managing Azure Virtual Networks (VNets) and their subnets. It is secured using Azure Active Directory authentication.

## Endpoints

### 1. Root Endpoint
**`GET /`**

- **Description**: Returns a message indicating that the API is operational.
- **Authentication**: Required.

---

### 2. Create or Update Virtual Network
**`POST /vnets`**
- **Description**: Creates or updates a virtual network based on the provided configuration.

| Parameter       | Type       | Required | Description                          | Example Data                          |
|-----------------|------------|----------|--------------------------------------|---------------------------------------|
| `resource_group` | `string`   | Yes      | Name of the resource group.          | `"demo-rg"`                           |
| `vnet_name`      | `string`   | Yes      | Name of the virtual network.         | `"myVNet"`                            |
| `location`       | `string`   | Yes      | Azure region for the VNet.           | `"eastus"`                            |
| `address_prefix` | `string`   | Yes      | Address space for the VNet.          | `"10.0.0.0/16"`                       |
| `subnets`        | `list`     | No       | List of subnets for the VNet.        | `[{"name": "subnet1", "address_prefix": "10.0.1.0/24"}]` |

## Example Usage
```json
{
    "resource_group": "demo-rg",
    "vnet_name": "myVNet",
    "location": "eastus",
    "address_prefix": "10.0.0.0/16",
    "subnets": [
        {
            "name": "subnet1",
            "address_prefix": "10.0.1.0/24"
        },
        {
            "name": "subnet2",
            "address_prefix": "10.0.2.0/24"
        },
        {
            "name": "subnet3",
            "address_prefix": "10.0.3.0/24"
        }
    ]
}
```
---

### 3. Retrieve VNet Data
**`GET /vnets`**

- **Description**: Retrieves details about a specific VNet or all VNets.
- **Authentication**: Required.

| Parameter   | Type       | Required | Description                          | Example Data |
|-------------|------------|----------|--------------------------------------|--------------|
| `vnet_name`  | `string`   | No       | Name of the virtual network to fetch. | `"my-vnet"`  |

---

### 4. Delete a Subnet
**`DELETE /vnets/subnet`**

- **Description**: Deletes a subnet from a specified VNet in a given resource group.
- **Authentication**: Required.

| Parameter       | Type       | Required | Description                          | Example Data                          |
|-----------------|------------|----------|--------------------------------------|---------------------------------------|
| `resource_group` | `string`   | Yes      | Name of the resource group.          | `"my-resource-group"`                 |
| `vnet_name`      | `string`   | Yes      | Name of the virtual network.         | `"my-vnet"`                           |
| `subnet_name`    | `string`   | Yes      | Name of the subnet to delete.        | `"subnet1"`                           |

## Example Usage
```bash
    {
    "resource_group": "demo-rg",
    "vnet_name": "myVNet",
    "subnet_name": "subnet2"
    }
```
---

### 5. Delete a Virtual Network
**`DELETE /vnets`**

- **Description**: Deletes a specified virtual network.
- **Authentication**: Required.

| Parameter       | Type       | Required | Description                          | Example Data                          |
|-----------------|------------|----------|--------------------------------------|---------------------------------------|
| `resource_group` | `string`   | Yes      | Name of the resource group.          | `"my-resource-group"`                 |
| `vnet_name`      | `string`   | Yes      | Name of the virtual network.         | `"my-vnet"`                           |


## Example Usage
```bash
    {
    "resource_group": "demo-rg",
    "vnet_name": "myVNet"
    }
```
---

## Authentication
- All endpoints are secured using Azure Active Directory authentication. Ensure you provide a valid token when accessing the API.
- [Reference for Authentication Mechanism -- https://intility.github.io/fastapi-azure-auth/single-tenant/azure_setup]