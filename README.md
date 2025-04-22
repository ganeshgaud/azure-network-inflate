# azure-network-inflate

This project, **azure-network-inflate**, is designed to simplify and automate the process of managing Azure network configurations. It provides tools and scripts to streamline network setup, scaling, and optimization.

## Features

- Automates Azure network resource creation.
- Supports scaling and optimization of network configurations.
- Provides detailed logging and error handling.
- Easy-to-use and customizable scripts.

## Prerequisites

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

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
