from pydantic import BaseModel
from typing import List

class SubnetRequest(BaseModel):
    name: str
    address_prefix: str

class VNetRequest(BaseModel):
    resource_group: str
    vnet_name: str
    location: str
    address_prefix: str
    subnets: List[SubnetRequest]

class SubnetDeleteRequest(BaseModel):
    resource_group: str
    vnet_name: str
    subnet_name: str

class VNetDeleteRequest(BaseModel):
    resource_group: str
    vnet_name: str
