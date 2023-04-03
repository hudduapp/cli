# Huddu CLI

> WARNING: The cli is not stable and may throw odd errors. Try at your own risk

This is the repository for the official huddu cli. Here are a few examples of what it can do:

- Connect to a machine via ssh
- List all of your stores
- Delete resources
- View your profile

... without opening the dashboard once.

### Installation

Here's a catch: hcli currently needs python3 to be installed (we recommend python version 3.9+). If that requirement is
met you should be able to simply install Huddu CLI via pip:

> pip install hcli

The latest (somewhat) stable version is 1.0.7

### Usage

To use the cli simply call `hcli` followed by the method you want to run.
e.g.:

- `hcli auth login` | log into your account
- `hcli auth logout` | log out of your account
- `hcli set organization` | set your organization id
- `hcli stores list` | if project_id and organization_id are set this displays the first 25 stores from the given
  project

... and many more.

Documentation is directly built into the `hcli`. Here's how that works:

- `hcli --help` | displays what commands can follow the hcli keyword
- `hcli stores --help` | follows up with commands that can follow `hcli stores`