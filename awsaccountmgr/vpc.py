"""Remove default VPC and related resources."""
import logging

logger = logging.getLogger(__name__)
from time import sleep


def retry_function(function, max_retry_seconds=180):
    """Helper function to retry describe VPC related actions.

    Retrying the given describe_* call. Sometimes the VPC service
    is not ready when you've just created a new account.

    :param function: The function to call. NOTE: don't execute it but
                     pass it like client.describe_vpcs   without the closing brackets()
    :param max_retry_seconds: Maximum amount of seconds to try

    :return: The response of the function call
    """
    while True:
        try:
            response = function()
            break
        except Exception as e:
            logger.warning(
                f"Error running {function.__name__}: {e}. Sleeping for 2 second before trying again."
            )
            max_retry_seconds - 2
            sleep(2)
            if max_retry_seconds <= 0:
                raise Exception(
                    f"Could not successfully execute function {function.__name__} "
                    f"within retry limit {max_retry_seconds}."
                )

    return response


def delete_default_vpc(client, account_id, dry_run=False):
    """Delete the default VPC in the given account id.

    :param client: EC2 boto3 client instance
    :param account_id: AWS account id
    """
    # Check and remove default VPC
    default_vpc_id = None

    vpc_response = retry_function(client.describe_vpcs)

    for vpc in vpc_response["Vpcs"]:
        if vpc["IsDefault"] is True:
            default_vpc_id = vpc["VpcId"]
            break

    if default_vpc_id is None:
        logging.info(f"No default VPC found in account {account_id}")
        return

    logging.info(f"Found default VPC Id {default_vpc_id}")
    subnet_response = retry_function(client.describe_subnets)

    default_subnets = [
        subnet
        for subnet in subnet_response["Subnets"]
        if subnet["VpcId"] == default_vpc_id
    ]

    logging.info(f"Deleting default {len(default_subnets )} subnets")
    _ = [
        client.delete_subnet(SubnetId=subnet["SubnetId"], DryRun=dry_run)
        for subnet in default_subnets
    ]

    igw_response = retry_function(client.describe_internet_gateways)
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
        _ = client.detach_internet_gateway(
            InternetGatewayId=default_igw, VpcId=default_vpc_id, DryRun=dry_run
        )

        logging.info(f"Deleting Internet Gateway {default_igw}")
        _ = client.delete_internet_gateway(InternetGatewayId=default_igw)

    sleep(10)  # It takes a bit of time for the dependencies to clear
    logging.info(f"Deleting Default VPC {default_vpc_id}")
    delete_vpc_response = client.delete_vpc(VpcId=default_vpc_id, DryRun=dry_run)

    return delete_vpc_response
