#!/usr/bin/env python3
import boto3
from time import sleep
from .sts import create_boto3_client
from .account import Account, AlternateContact


class Organization:
    """Interact with AWS Organization API."""

    def __init__(self, root_ou_id, credentials):
        """Initialise the boto3 organisation session.

        :param org_client: A 'organizations' boto3 client in the Master account
        :param root_ou_id: The ID of the root Organizational Unit
        :param credentials: Tuple of (key, secret, token) of the master account
        """
        self._master_credentials = credentials
        self.root_ou_id = root_ou_id

        self._org_client = create_boto3_client(
            self.get_master_account_id(), "organizations", self._master_credentials
        )

        self._account_client = create_boto3_client(
            self.get_master_account_id(), "account", self._master_credentials
        )

    def list_organizational_units_for_parent(self, parent_ou):
        """Returns a list of OUs for the given parent."""
        organizational_units = [
            ou
            for org_units in self._org_client.get_paginator(
                "list_organizational_units_for_parent"
            ).paginate(ParentId=parent_ou)
            for ou in org_units["OrganizationalUnits"]
        ]
        return organizational_units

    def list_accounts(self):
        """Retrieves all accounts in organization."""
        existing_accounts = [
            account
            for accounts in self._org_client.get_paginator("list_accounts").paginate()
            for account in accounts["Accounts"]
        ]
        return existing_accounts

    def get_account_id(self, account_name):
        """Retrieves the account ID.

        :param account_name: The name of the account
        :return: Id of account, None if account does not exist
        """
        for account in self.list_accounts():
            if account["Name"].strip() == account_name.strip():
                return account["Id"]

        return None

    def get_ou_id(self, ou_path, parent_ou_id=None):
        """Retrieve an organisational unit id.

        :param ou_path: the name of the organisational unit. For nested ou's use / notation, eg. eu/eudev
        :param parent_ou_id: The parent from where to start parsing the ou_path, defaults to root
        :return: (ou_id, parent_id)
        """
        # Return root OU if '/' is provided
        if ou_path.strip() == "/":
            return self.root_ou_id

        # Set initial OU to start looking for given ou_path
        if parent_ou_id is None:
            parent_ou_id = self.root_ou_id

        # Parse ou_path and find the ID
        ou_hierarchy = ou_path.strip("/").split("/")
        hierarchy_index = 0

        while hierarchy_index < len(ou_hierarchy):
            org_units = self.list_organizational_units_for_parent(parent_ou_id)

            for ou in org_units:
                if ou["Name"] == ou_hierarchy[hierarchy_index]:
                    parent_ou_id = ou["Id"]
                    hierarchy_index += 1
                    break
            else:
                raise ValueError(
                    f"Could not find ou with name {ou_hierarchy} in OU list {org_units}."
                )

        return parent_ou_id

    def move_account(self, account_id, ou_path, allow_direct_move=False):
        """Move the account to an organisation unit.

        Note that we are not allowing an account to move from non-root to another ou. This
        is to avoid issues with the AWS Deployment Framework that requires you to first move
        an account to root before moving to another OU.

        :param account_id: ID of the account to move
        :param ou_path: The full path to the ou in slash notation (e.g. /europe/test )
        :param allow_direct_move: Set this to True to allow moving accounts directly between OUs
                                  without first moving to the root OU.
        """
        if ou_path != self.root_ou_id:
            ou_id = self.get_ou_id(ou_path)
        else:
            ou_id = self.root_ou_id

        # TODO error handling and check if an account always returns just one item
        response = self._org_client.list_parents(ChildId=account_id)
        source_parent_id = response["Parents"][0]["Id"]

        if source_parent_id == ou_id:
            # Account is already resided in ou_path
            return

        if (
            allow_direct_move is False
            and source_parent_id != self.root_ou_id
            and ou_id != self.root_ou_id
        ):
            raise ValueError(
                f"Trying to move an account from non-root OU to another OU. "
                "Move account to root ({self.root_ou_id}) first."
            )

        self._org_client.move_account(
            AccountId=account_id,
            SourceParentId=source_parent_id,
            DestinationParentId=ou_id,
        )

    def create_account_tags(self, account_id, tags):
        """Adds tags to given account.

        :param account_id: ID of the AWS account
        :param tags: Dict of tags to apply to account
        """
        # TODO: Make the tag definition fully declarative
        # meaning that any tag not referenced will be removed
        # from the account. use org_client.untag_resource()
        formatted_tags = [
            {"Key": key, "Value": value} for tag in tags for key, value in tag.items()
        ]
        self._org_client.tag_resource(ResourceId=account_id, Tags=formatted_tags)

    @staticmethod
    def get_master_account_id():
        """Retrieves the master account id from API."""
        org_client = boto3.client("organizations")
        response = org_client.describe_organization()
        return response["Organization"]["MasterAccountId"]

    def create_account_alias(self, account_id, account_alias):
        """Creates or updates the account alias for given account_id."""

        iam_client = create_boto3_client(account_id, "iam", self._master_credentials)

        try:
            iam_client.create_account_alias(AccountAlias=account_alias)
        except iam_client.exceptions.EntityAlreadyExistsException:
            pass  # Alias already exists

    def remove_alternate_contact(self, account_id, contact_type):
        """Removes the contact type from the account."""

        if contact_type.upper() not in ["BILLING", "OPERATIONS", "SECURITY"]:
            raise ValueError(f"Contact type {contact_type} is not supported.")

        self._account_client.delete_alternate_contact(
            AccountId=account_id, AlternateContactType=contact_type.upper()
        )

    def update_alternate_contact(
        self, account_id: str, contact_type: str, contact_details: AlternateContact
    ):
        """Create or update the account alternate contacts for given account.

        :param account_id: ID of the AWS account
        :param contact_type: Type of contact to update
        :param contact_details: AlternateContact class instance
        """

        if contact_type.upper() not in ["BILLING", "OPERATIONS", "SECURITY"]:
            raise ValueError(f"Contact type {contact_type} is not supported.")

        self._account_client.put_alternate_contact(
            AccountId=account_id,
            AlternateContactType=contact_type,
            EmailAddress=contact_details.email,
            Name=contact_details.name,
            PhoneNumber=contact_details.phone,
            Title=contact_details.title,
        )

    def create_account(self, account: Account):
        """Creates a new the account if it doesn't exist.

        :param account: Class instance of Account

        :return: account_id

            TODO: Move this to the documentation:
            # Dummy payload for account creation
                from datetime import datetime
                response = {
                    'Id': 'string',
                    'AccountName': self.full_name,
                    'State': 'SUCCEEDED',
                    'RequestedTimestamp': datetime(2015, 1, 1),
                    'CompletedTimestamp': datetime(2015, 1, 1),
                    'AccountId': '173289020951',
                    'FailureReason': 'ACCOUNT_LIMIT_EXCEEDED'
                }
        """
        if account.allow_billing is True:
            allow_billing = "ALLOW"
        else:
            allow_billing = "DENY"

        response = self._org_client.create_account(
            Email=account.email,
            AccountName=account.full_name,
            # RoleName=role_name,  # defaults to OrganizationAccountAccessRole
            IamUserAccessToBilling=allow_billing,
        )["CreateAccountStatus"]

        while response["State"] == "IN_PROGRESS":
            response = self._org_client.describe_create_account_status(
                CreateAccountRequestId=response["Id"]
            )["CreateAccountStatus"]

            if response.get("FailureReason"):
                raise IOError(
                    f"Failed to create account {account.full_name}: {response['FailureReason']}"
                )

            sleep(1)  # waiting for a sec before checking account status again

        account_id = response["AccountId"]
        # TODO: Instead of sleeping, query for the role.
        sleep(10)  # Wait until OrganizationalRole is created in new account

        return account_id
