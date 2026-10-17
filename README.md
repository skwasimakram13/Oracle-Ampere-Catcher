# Oracle Ampere Catcher

A simple Python script for retrying OCI instance launches until a free Oracle Ampere A1 slot becomes available.

This repository is a sanitized template. Do not commit real OCI keys, private SSH keys, or live OCIDs.

## What this repo contains

- `oci_ampere_catcher.py` — the launcher script
- `oci_config` — example OCI config template
- `your_ssh_key` and `your_ssh_key.pub` — example key placeholders only
- `requirements.txt` — Python package dependency
- `.gitignore` — protects secrets and local artifacts

## Prerequisites

Before running this script, make sure you have:

- Python 3.8+
- An Oracle Cloud account
- OCI API key configured locally
- A valid OCI compartment, subnet, and image ID
- A public SSH key for the launched instance

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Create your local OCI config

Create a local OCI config file such as:

```bash
mkdir -p ~/.oci
nano ~/.oci/config
```

Example content:

```ini
[DEFAULT]
user=<USER_OCID>
fingerprint=<API_KEY_FINGERPRINT>
tenancy=<TENANCY_OCID>
region=<REGION>
key_file=/home/your-user/.oci/oci_api_key.pem
```

Important:
- Keep this file outside the repository.
- Never push it to GitHub.
- Replace `<...>` values with your real ones locally only.

## Create SSH key pair

If you do not already have an SSH key pair:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/your_ssh_key
```

This creates:
- `~/.ssh/your_ssh_key` — private key
- `~/.ssh/your_ssh_key.pub` — public key

Use the public key path in the script environment.

## Set environment variables

Set these before running the script:

```bash
export OCI_CONFIG_PATH="$HOME/.oci/config"
export OCI_CONFIG_PROFILE="DEFAULT"
export COMPARTMENT_ID="ocid1.compartment.oc1..REPLACE_WITH_YOURS"
export AVAILABILITY_DOMAIN="REPLACE_WITH_YOURS"
export SUBNET_ID="ocid1.subnet.oc1..REPLACE_WITH_YOURS"
export IMAGE_ID="ocid1.image.oc1..REPLACE_WITH_YOURS"
export SSH_PUB_KEY_PATH="$HOME/.ssh/your_ssh_key.pub"
export CATCHER_LOG_PATH="$HOME/ampere_catcher_log.txt"
export SUCCESS_FILE="$HOME/SERVER_CAUGHT_SUCCESS.txt"
```

Optional tuning variables:

```bash
export OCPUS="1"
export MEMORY_IN_GBS="6"
export BOOT_VOLUME_GB="50"
export SHAPE="VM.Standard.A1.Flex"
export DISPLAY_NAME="your-server"
```

## Run the script

From the repository root:

```bash
python oci_ampere_catcher.py
```

The script will:
- load your OCI configuration
- read your public SSH key
- repeatedly attempt to launch an Ampere A1 flex instance
- retry on capacity or rate-limit errors
- save a success file when the instance is created

## What to replace locally

Before using this on your Oracle account, replace these values with your own local values:

- `COMPARTMENT_ID`
- `AVAILABILITY_DOMAIN`
- `SUBNET_ID`
- `IMAGE_ID`
- `SSH_PUB_KEY_PATH`
- `OCI_CONFIG_PATH`
- Your actual OCI config file contents in `~/.oci/config`

## Safety and cost notes

- This script launches real OCI instances.
- Free-tier capacity is not guaranteed.
- You may incur charges depending on your tenancy, shape, and quota.
- Never commit private keys, API keys, or real OCIDs.
- Keep all secrets outside the repository.

## Troubleshooting

### Authentication errors

Check that:
- `OCI_CONFIG_PATH` points to the correct file
- the file contains valid `user`, `fingerprint`, `tenancy`, `region`, and `key_file`
- the private key exists and matches the uploaded API key

### Permission errors

Make sure the identity used by the OCI key has permission to launch compute instances in the target compartment.

### Capacity errors

If the script keeps printing capacity/rate-limit errors, then no free A1 capacity is available in the selected region or availability domain yet.

## Files to keep local, not in Git

These should stay on your machine only:

- `~/.oci/config`
- `~/.oci/oci_api_key.pem`
- `~/.ssh/your_ssh_key`
- `~/.ssh/your_ssh_key.pub`
- local log files and success files

## License

This repository is a template for personal use. Add a license if you want to publish it with explicit reuse terms.

