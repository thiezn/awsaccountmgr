# Release History

## 0.0.16 (2021-12-06)

- FIX: Use standalone context for updating master account

## 0.0.15 (2021-12-06)

- FIX: Avoid raising an error when trying to remove an alternate contact thats non existing

## 0.0.14 (2021-12-06)

- FIX: The API has a more strict formatting for the phone field. Default to "00000000" when phone field is not provided

## 0.0.13 (2021-12-06)

- FIX: / is an invalid character for Alternate contact fields. Defaulting to NotApplicable and not@applicable.com

## 0.0.12 (2021-12-06)

- FIX: all alternate contact fields are mandatory. Defaulting to N/A when not provided

## 0.0.11 (2021-12-06)

- Added capability to update AWS account alternate contacts
- FIX: configuration example showed Tags as dict items, corrected to list of dicts

## 0.0.10 (2020-11-10)

- FIX: Retrying subnet and IGW describe calls. Sometimes they are not yet available after a new account creation.

## 0.0.9 (2019-10-09)

- FIX: AllowDirectMoveBetweenOU parameter now works as intended

## 0.0.8 (2019-10-09)

- FIX: Using pagination when listing Org Units

## 0.0.7 (2019-09-23)

- setup.py now includes dependency libraries
- FIX: describe_vpcs call sometimes failed on creating new account

## 0.0.6 (2019-08-01)

- Configuration files now support '/' to target root

## 0.0.5 (2019-08-01)

- FIX: Removing VPCs through threads working properly

## 0.0.4 (2019-07-31)

- Retrieving master_account_id from API
- Deleting VPCs now using threads

## 0.0.3 (2019-07-30)

- Removing default VPCs in all regions

## 0.0.2 (2019-07-30)

- config_directory is now a mandatory parameter

## 0.0.1 (2019-07-30)

Thanks to @deltagarrett for testing!

- Initial version
