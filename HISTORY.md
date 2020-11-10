# Release History

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
