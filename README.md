# Multi-Account management in AWS Organizations

***!IMPORTANT!*** - The code has not been tested properly yet in production and no unit/integration testing have been implemented. Use at your own risk.

This repository contains code that manages the process around AWS account creation. It assumes you are working with the [AWS Deployment Framework](https://github.com/awslabs/aws-deployment-framework) for managing deployments in a multi-account AWS organization.

*Current Features*

- Create new AWS accounts within existing AWS Organization
- Move accounts to the organizational unit defined in config files
- Optionally remove default VPC resources on accounts
- Create and update account aliasses
- Account tagging
- Optional protection from moving accounts directly between organizational units (Related to AWS Deployment Framework)
- Create and update account alternate contacts

*Not supported due to AWS Organization API limitations*

- Updating account names
- Updating account email addresses
- Removing accounts
- Handling root account credentials and MFA

## Installation & Configuration

Note we are only supporting python3.6 and up, I really like my f-strings..

Install the package using pip

```bash
pip3 install awsaccountmgr
```

Next define configuration files for the accounts you would like to manage. You can have multiple configuration files for logical separation. The script will iterate and validate each file before sequentially creating/updating the defined accounts.

Here is an example file

```yaml
Accounts:
  # Account with only mandatory parameters
  - AccountFullName: playgroundaccount
    OrganizationalUnitPath: playground/
    Email: playgroundaccount@moorspots.com

  # Delete the default VPC for this account
  - AccountFullName: usdevaccount
    OrganizationalUnitPath: us/dev
    Email: usdevaccount@moorspots.com
    DeleteDefaultVPC: True

  # Account with all available parameters
  - AccountFullName: myrootaccount
    OrganizationalUnitPath: /
    Email: myrootaccount@moorspots.com
    DeleteDefaultVPC: True
    AllowDirectMoveBetweenOU: True
    Alias: IDontWantMyAliasToBeTheSameAsTheAccountFullName
    AllowBilling: False
    AlternateContacts:
      Operations:
        Email: myops@moorspots.com
        Name: myname
        Title: Doctor
        PhoneNumber: +31307161111

      Security:
        Email: mysecurity@moorspots.com
        Name: myname
        Title: Doctor
        PhoneNumber: +31307161111

      Billing:
        Email: mybilling@moorspots.com
        Name: myname
        Title: Doctor
        PhoneNumber: +31307161111

    Tags:
      - CostCenter: 123456789
```

To create new accounts or move accounts to a different OU you only have to update the relevant account configuration file and re-run the script.

The OU name is the name of the direct parent of the account. If you want to move an account to the root you can provide the AWS organization id (eg "r-abc1"). If you are dealing with nested organizational units you can seperate them with a / (see examples above).

If you provide the 'AlternateContacts' key, all three alternate contact types will be fully updated with the declared configuration. If you for instance only provide an Operations contact entry, it will try to remove the Security and Billing contact information.

# Usage

Once the configuration files are defined you can start the script locally with:

```bash
awsaccountmgr <root_ou_id> <config folder path>
```

You will have to have AWS credentials stored (using AWS CLI or environment variables) on your machine. If the assumed role is not resided in the master account the script will try to assume the OrganizationAccountAccessRole role in the master account. This is useful for people using the AWS Deployment Framework to run this script from a pipeline in the deployment account.

To see all available command line options, run  ```awsaccountmgr --help```

# TODO: Describe how you can setup the AWS Deployment Framework pipeline to run this on updates and scheduled time. Quick summary

- Create cc-buildonly ADF pipeline
- add buildspec.yml similar to example-buildspec.yml
- Update the ADF global.yml files to ensure the deployment account is able to do organizations related stuff in the master account
- TIP: If you add a schedule to the ADF pipeline you can reasonably ensure the accounts are configured as defined in the yaml files.
- TIP2: perhaps this module can be used in combination with a lambda triggered by cloudwatch events related to relevant organizations actions. This will immediately correct any changes someone does to accounts to whats being defined in the configuration files.
