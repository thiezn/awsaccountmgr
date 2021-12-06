"""Model for handling AWS accounts within the organization.

The Account class allows you to create or update a new account.
"""

from typing import List


class AlternateContact:
    """Represent an alternate contact for an AWS Account."""

    def __init__(
        self,
        contact_type: str,
        name: str = None,
        email: str = None,
        phone: str = None,
        title: str = None,
    ):
        """Initialize AlternateContact."""
        self.type = contact_type
        self.name = name
        self.email = email

        if phone:
            # Ensuring phone numbers are string
            self.phone = str(phone)
        else:
            self.phone = None

        self.title = title

    @classmethod
    def load_from_config(cls, contact_type, config):
        """Initialize Account class from configuration AlternateContacts entry."""

        if not config:
            return None

        return cls(
            contact_type=contact_type,
            name=config.get("Name"),
            email=config.get("Email"),
            phone=config.get("PhoneNumber"),
            title=config.get("Title"),
        )


class Account:
    """Represents a single AWS account."""

    def __init__(
        self,
        full_name: str,
        email: str,
        ou_path: str,
        alias: str = None,
        delete_default_vpc: bool = False,
        allow_direct_move_between_ou: bool = False,
        allow_billing: bool = True,
        update_alternate_contacts: bool = False,
        operations_contact: AlternateContact = None,
        security_contact: AlternateContact = None,
        billing_contact: AlternateContact = None,
        tags: List = None,
    ):
        """Initialize Account object.

        :param full_name: Full name of the account
        :param email: Valid email address of account
        :param ou_path: Organizational Unit path. For nested OUs use / notation, eg. us/development.
                        Use root identifier to target root OU (eg. r-abc1) or just use '/'

        :param alias: Optional Alias to use, if None the alias will default to full_name
        :param delete_default_vpc: Set this to True to delete the default vpc from the account
        :param allow_direct_move_between_ou: Set this to False to prevent the script from moving
                                             an account directly from one OU to another. This is
                                             useful if you are using the AWS Deployment Framework
                                             as it requires you to first move an account to the root
                                             to trigger the base cloudformation stack updates.
        :param update_alternate_contacts: Set this to True to update the alternate contacts
        :param allow_billing: Set this to False to prevent account admins from using the billing console
        :param operations_contact: Contact email for AWS Operations
        :param security_contact: Contact email for AWS Security
        :param billing_contact: Contact email for AWS Billing
        :param tags: a dict containing optional tags for the account
        """
        self.full_name = full_name
        self.email = email
        self.ou_path = ou_path
        self.delete_default_vpc = delete_default_vpc
        self.allow_direct_move_between_ou = allow_direct_move_between_ou
        self.allow_billing = allow_billing

        if alias is None:
            self.alias = full_name
        else:
            self.alias = alias

        self.update_alternate_contacts = update_alternate_contacts
        self.operations_contact = operations_contact
        self.security_contact = security_contact
        self.billing_contact = billing_contact

        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    @classmethod
    def load_from_config(cls, config):
        """Initialize Account class from configuration object."""

        if config.get("AlternateContacts"):
            update_alternate_contacts = True
            operations_contact = AlternateContact.load_from_config(
                "OPERATIONS", config["AlternateContacts"].get("Operations")
            )
            security_contact = AlternateContact.load_from_config(
                "SECURITY", config["AlternateContacts"].get("Security")
            )
            billing_contact = AlternateContact.load_from_config(
                "BILLING", config["AlternateContacts"].get("Billing")
            )
        else:
            update_alternate_contacts = False
            operations_contact = None
            security_contact = None
            billing_contact = None

        return cls(
            config["AccountFullName"],
            config["Email"],
            config["OrganizationalUnitPath"],
            alias=config.get("Alias", None),
            delete_default_vpc=config.get("DeleteDefaultVPC", False),
            allow_direct_move_between_ou=config.get("AllowDirectMoveBetweenOU", False),
            allow_billing=config.get("AllowBilling", True),
            update_alternate_contacts=update_alternate_contacts,
            operations_contact=operations_contact,
            security_contact=security_contact,
            billing_contact=billing_contact,
            tags=config.get("Tags", []),
        )
