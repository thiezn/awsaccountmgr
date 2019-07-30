"""
# vpc.py

Remove default VPC and related resources
"""
import logging
logger = logging.getLogger(__name__)
from time import sleep


def delete_default_vpc(client, account_id, dry_run=False):
    """Delete the default VPC in the given account id

        :param client: EC2 boto3 client instance
        :param account_id: AWS account id
        """
    # Check and remove default VPC
    default_vpc_id = None
    vpc_response = client.describe_vpcs()
    for vpc in vpc_response["Vpcs"]:
        if vpc["IsDefault"] is True:
            default_vpc_id = vpc["VpcId"]
            break

    if default_vpc_id is None:
        logging.info(f"No default VPC found in account {account_id}")
        return

    logging.info(f"Found default VPC Id {default_vpc_id}")
    subnet_response = client.describe_subnets()
    default_subnets = [
        subnet
        for subnet in subnet_response["Subnets"]
        if subnet["VpcId"] == default_vpc_id
    ]

    logging.info(f"Deleting default {len(default_subnets )} subnets")
    subnet_delete_response = [
        client.delete_subnet(SubnetId=subnet["SubnetId"], DryRun=dry_run)
        for subnet in default_subnets
    ]

    igw_response = client.describe_internet_gateways()
    try:
        default_igw = [
            igw["InternetGatewayId"]
            for igw in igw_response["InternetGateways"]
            for attachment in igw["Attachments"]
            if attachment["VpcId"] == default_vpc_id
        ][0]
    except IndexError:
        default_igw = None

    if default_igw:
        logging.info(f"Detaching Internet Gateway {default_igw}")
        detach_default_igw_response = client.detach_internet_gateway(
            InternetGatewayId=default_igw, VpcId=default_vpc_id, DryRun=dry_run
        )

        logging.info(f"Deleting Internet Gateway {default_igw}")
        delete_internet_gateway_response = client.delete_internet_gateway(
            InternetGatewayId=default_igw
        )

    sleep(10)  # It takes a bit of time for the dependencies to clear
    logging.info(f"Deleting Default VPC {default_vpc_id}")
    delete_vpc_response = client.delete_vpc(VpcId=default_vpc_id, DryRun=dry_run)

    return delete_vpc_response
