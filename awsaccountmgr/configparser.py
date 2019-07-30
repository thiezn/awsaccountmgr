"""
# configparser.py

Module to parse and validate the yaml configuration files.
"""
import yaml
import os
from .account import Account


def read_config_files(folder):
    """Retrieve account objects from yaml configuration files in given folder.

    :param folder: Folder containing config files

    :return: list of tuples [(full_account_name, email, ou_path), ]
    """
    files = [os.path.join(folder, f) for f in os.listdir(folder)]

    accounts = []
    for filename in files:
        with open(filename, 'r') as stream:
            config = yaml.safe_load(stream)

            validate_config(config['Accounts'])

            for account in config['Accounts']:
                accounts.append(Account.load_from_config(account))

    return accounts

def validate_config(configuration):
    """Validate configuration"""
    supported_keys = [
        'OrganizationalUnitPath',
        'Email',
        'AccountFullName',
        'DeleteDefaultVPC',
        'AllowDirectMoveBetweenOU',
        'AllowBilling',
        'Alias',
        'Tags'
    ]

    if not isinstance(configuration, list):
        raise ValueError(f'Configuration invalid: {configuration}')

    for account in configuration:

        # Mandatory parameters
        if 'AccountFullName' not in account:
            raise ValueError(f'Missing AccountFullName in configuration: {account}')   
        if 'OrganizationalUnitPath' not in account:
            raise ValueError(f'Missing OrganizationalUnitPath in configuration: {account}')
        if 'Email' not in account:
            raise ValueError(f'Missing Email in configuration: {account}')

        # Optional parameters
        if 'DeleteDefaultVPC' in account and not isinstance(account['DeleteDefaultVPC'], bool):
                raise ValueError(f'{account["AccountFullName"]} DeleteDefaultVPC param should be Boolean')

        if 'AllowDirectMoveBetweenOU' in account and not isinstance(account['AllowDirectMoveBetweenOU'], bool):
                raise ValueError(f'{account["AccountFullName"]} AllowDirectMoveBetweenOU param should be Boolean')

        if 'AllowBilling' in account and not isinstance(account['AllowBilling'], bool):
                raise ValueError(f'{account["AccountFullName"]} AllowBilling param should be Boolean')

        if 'Alias' in account and not isinstance(account['Alias'], str):
                raise ValueError(f'{account["AccountFullName"]} Alias param should be String')

        if 'Tags' in account:
            if not isinstance(account['Tags'], list):
                raise ValueError(f'{account["AccountFullName"]} Tags param should be a List')
            for tag in account['Tags']:
                if not isinstance(tag, dict):
                    raise ValueError(f'{account["AccountFullName"]} Tags should be a Dict but found {tag}')

        # Invalid parameters
        for key in account:
            if key not in supported_keys:
                raise ValueError(f'Key {key} not supported in configuration: {account}')
