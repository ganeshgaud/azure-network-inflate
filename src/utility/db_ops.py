import sqlite3
import json
from src.utility.logger import logger
from src.authentication.auth import get_network_client


db_file = 'network_config.db'
db_name = db_file.split('.')[0]

def create_connection(db_file):
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def create_table(cursor):
    """Create the network_config table if it doesn't exist."""
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {db_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_group TEXT NOT NULL,
        vnet_name TEXT NOT NULL,
        location TEXT NOT NULL,
        address_prefix TEXT NOT NULL,
        subnets TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')

def insert_network_config(cursor, data):
    """Insert the network configuration data into the database."""
    subnets_json = json.dumps(data['subnets'])
    cursor.execute(f'''
    INSERT INTO {db_name} (resource_group, vnet_name, location, address_prefix, subnets, status) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['resource_group'], data['vnet_name'], data['location'], data['address_prefix'], subnets_json, data['status']))

def update_network_config(cursor, new_data):
    """Update network configuration data based on vnet_name."""
    subnets_json = json.dumps(new_data['subnets'])
    cursor.execute(f'''
    UPDATE {db_name}
    SET resource_group = ?, location = ?, address_prefix = ?, subnets = ?, status = ?
    WHERE vnet_name = ?
    ''', (new_data['resource_group'], new_data['location'], new_data['address_prefix'], subnets_json, new_data['status'], new_data['vnet_name']))

def update_subnet_config(cursor, vnet_name, subnets):
    """Update network configuration data based on vnet_name."""
    subnets_json = str(subnets)
    cursor.execute(f'''
    UPDATE {db_name}
    SET subnets = ?, status = ?
    WHERE vnet_name = ?
    ''', (subnets_json, 'UPDATED', vnet_name))

def delete_network_config(cursor, vnet_name):
    """Soft-delete a network configuration by updating its status."""
    cursor.execute(f'''
    UPDATE {db_name}
    SET status = ?
    WHERE vnet_name = ?
    ''', ('DELETED', vnet_name))

def query_single_record(cursor, vnet_name):
    """Fetch a single record based on vnet_name."""
    cursor.execute(f'SELECT * FROM {db_name} WHERE vnet_name = ?', (vnet_name,))
    return cursor.fetchone()

def display_result(row):
    """Display a single query result."""
    if row:
        logger.info(f"ID: {row[0]}, Resource Group: {row[1]}, VNet Name: {row[2]}, Location: {row[3]}, Address Prefix: {row[4]}, Subnets: {row[5]}")
    else:
        logger.info("No matching record found.")

def insert_vnet_data(data):
    """Insert VNet data into the database."""
    try:
        net_client = get_network_client()

        data = json.loads(data)
        data["status"] = "AVAILABLE"
        vnet = net_client.virtual_networks.get(data['resource_group'], data['vnet_name'])
        existing_subnet_map = [
            {"name": subnet.name, "address_prefix": subnet.address_prefix}
            for subnet in vnet.subnets
        ]
        data["subnets"] = existing_subnet_map

        conn = create_connection(db_file)
        cursor = conn.cursor()
        create_table(cursor)
        insert_network_config(cursor, data)
        conn.commit()
        logger.info("VNet data inserted successfully.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def update_vnet_data(data):
    """Update VNet data in the database."""
    conn = None
    try:
        net_client = get_network_client()
        data = json.loads(data)
        data["status"] = "UPDATED"
        vnet = net_client.virtual_networks.get(data['resource_group'], data['vnet_name'])
        existing_subnet_map = [
            {"name": subnet.name, "address_prefix": subnet.address_prefix}
            for subnet in vnet.subnets
        ]
        data["subnets"] = existing_subnet_map
        logger.info(f"Updating VNet data for {data["vnet_name"]}...")
        conn = create_connection(db_file)
        cursor = conn.cursor()
        update_network_config(cursor, data)
        conn.commit()
        logger.info("VNet data updated successfully.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def delete_subnet_data(resource_group, vnet_name):
    """Update VNet data in the database."""
    conn = None
    try:
        net_client = get_network_client()
        vnet = net_client.virtual_networks.get(resource_group, vnet_name)
        existing_subnet_map = [
            {"name": subnet.name, "address_prefix": subnet.address_prefix}
            for subnet in vnet.subnets
        ]
        logger.info(f"Updating VNet data for {vnet_name}...")
        conn = create_connection(db_file)
        cursor = conn.cursor()
        update_subnet_config(cursor, vnet_name, existing_subnet_map)
        conn.commit()
        logger.info("VNet data updated successfully.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()



def delete_vnet_data(vnet_name):
    """Mark VNet data as deleted in the database."""
    conn = None
    try:
        logger.info(f"Deleting VNet data for {vnet_name}...")
        conn = create_connection(db_file)
        cursor = conn.cursor()
        delete_network_config(cursor, vnet_name)
        conn.commit()
        logger.info("VNet data marked as DELETED.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def get_vnet_data(vnetName=None):
    """Fetch specific VNet data if vnetName is provided, else fetch all VNet records."""
    conn = None
    try:
        conn = create_connection(db_file)
        cursor = conn.cursor()

        if vnetName:
            valid_statuses = ["AVAILABLE", "UPDATED"]
            placeholders = ','.join(['?'] * len(valid_statuses))  # e.g. ?,?
            query = f'SELECT * FROM {db_name} WHERE vnet_name = ? AND status IN ({placeholders})'
            cursor.execute(query, (vnetName, *valid_statuses))
            row = cursor.fetchone()
            return row
        else:
            cursor.execute(f'SELECT * FROM {db_name}')
            rows = cursor.fetchall()
            return rows

    except sqlite3.DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    data = {
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
    insert_vnet_data(data)
