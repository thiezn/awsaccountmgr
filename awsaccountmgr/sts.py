"""
# sts.py

Helper fuction for working with cross-account roles
"""
import boto3
import logging


def assume_role(account_id, role_name="OrganizationAccountAccessRole", source_role=None):
    """Assume a role in a different account

    :param account_id: The AWS account ID to assume role in
    :param role_name: The name of the role to assume
    :source_role: Tuple of (access_key_id, secret_access_key, session_token) of the role you want
                                to assume from

    :return: Tuple of (access_key_id, secret_access_key, session_token)
    """
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    if source_role is None:
        sts_client = boto3.client("sts")
    else:
        sts_client = boto3.client(
            "sts",
            aws_access_key_id=source_role[0],
            aws_secret_access_key=source_role[1],
            aws_session_token=source_role[2]
        )

    current_account = sts_client.get_caller_identity().get('Account')
    logging.debug(f"Account {current_account} assuming role {role_name} on account {account_id}")

    sts_response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='newsession'
    )

    return (
        sts_response["Credentials"]["AccessKeyId"],
        sts_response["Credentials"]["SecretAccessKey"],
        sts_response["Credentials"]["SessionToken"]
    )

def create_boto3_client(account_id, client_type, source_role_credentials=None, region_name=None):
        """Creates a boto3 client associated with the account_id you want to target.

        The client is created by first assuming a role in the master account and from there
        assume the OrganizationAccountAccessRole in a member account. This is done to get
        this code working through ADF running in the deployment account.

        :param account_id: The account_id you want to create an account in
        :param client_type: The type of boto3 client you want to create, eg. 'sts' or 'ec2'
        :param source_role_credentials: The assumed role to assume the new session from
        :param region_name: The region to intialize in
        """
        # Assume OrganizationAccountAccessRole through Master account
        if source_role_credentials is None:
            logging.debug(f'Creating client {client_type}.')
            access_key_id, secret_access_key, session_token = assume_role(account_id)
        else:
            logging.debug(f'Creating client {client_type} through a source_role.')
            access_key_id, secret_access_key, session_token = assume_role(
                account_id,
                source_role=source_role_credentials
            )

        client = boto3.client(
            client_type,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
            region_name=region_name
        )
        return client
