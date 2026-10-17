# Oracle Ampere Catcher

Short project summary

A minimal, opinionated Python template that repeatedly attempts to launch an Oracle Cloud Infrastructure (OCI) Ampere A1 (VM.Standard.A1.Flex) instance until capacity becomes available. Intended for experienced OCI users who want an automated "catcher" script; this repo is a sanitized template — it contains no live keys or OCIDs.

How it works

- Read configuration and credentials from your local OCI config (default: `~/.oci/config`) and optional environment variables.
- Read a local SSH public key and include it in the instance metadata so you can SSH in after launch.
- Build a LaunchInstanceDetails object using placeholder values (COMPARTMENT, SUBNET, IMAGE, shape/config).
- Repeatedly call the OCI Compute API to launch the instance.
  - On capacity or rate-limit errors the script retries after a short wait.
  - On successful launch the script writes a success file and prints instance details.

Setup

1. Prerequisites
   - Python 3.8+
   - An Oracle Cloud account and appropriate permissions
   - OCI Python SDK: `pip install -r requirements.txt`
   - An OCI API key pair (private key stored locally and referenced in your OCI config)
   - An SSH key pair (public key path available locally)

2. OCI config (local only)
   Create `~/.oci/config` or set `OCI_CONFIG_PATH` to point to your config file.

   Example `~/.oci/config`:
   ```ini
   [DEFAULT]
   user=<USER_OCID>
   fingerprint=<API_KEY_FINGERPRINT>
   tenancy=<TENANCY_OCID>
   region=<REGION>
   key_file=/home/your-user/.oci/oci_api_key.pem
   ```

   Important: keep this file out of the repository and never commit your private API key.

3. SSH key
   Generate an SSH key pair if needed and keep the private key local:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/your_ssh_key
   ```
   Use the public key path in the environment variable `SSH_PUB_KEY_PATH`.

4. Environment variables (example)

   Set the required environment variables (bash example):
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

Run

From the repository root run:

```bash
python oci_ampere_catcher.py
```

What to expect

- The script prints attempt logs to stdout and appends them to `CATCHER_LOG_PATH`.
- On capacity/rate-limit responses the script will wait and retry.
- On success the script writes instance details to `SUCCESS_FILE` and prints a success message.

Troubleshooting

- Authentication errors
  - Ensure `OCI_CONFIG_PATH` points to the correct config and that `key_file` points to a valid private API key.
  - Check `user`, `fingerprint`, `tenancy`, and `region` values in the config.

- Permission errors
  - Ensure the user associated with your API key has `compute.instance.launch` permissions for the target compartment.

- Missing/incorrect env vars
  - If `COMPARTMENT_ID`, `SUBNET_ID`, or `IMAGE_ID` are not set, the script will either fall back (compartment -> tenancy) or fail. Set the values explicitly.

- Capacity or rate-limit errors
  - These indicate no free A1 capacity in the chosen region/AD or temporary API rate limits. Try a different availability domain or region, and consider adding exponential backoff with jitter for production.

- OCI SDK errors
  - Upgrade your SDK: `pip install --upgrade oci` and ensure your Python version is supported.

Security

- Never commit private keys, API keys, or real OCIDs to source control.
- Use `.gitignore` to exclude `~/.oci/config`, any private key files, and local logs.
- Use the principle of least privilege for the API key user — create a dedicated user/compartment and assign minimal policies.
- Monitor your tenancy and billing; launching instances can incur charges.

License

This repository is provided as a personal-use template. If you want to publish it with an explicit license, add a `LICENSE` file (e.g. MIT). Example MIT header:

```
MIT License

Copyright (c) <year> <your name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

If you want, I can add a `LICENSE` file with MIT (or another) license and/or add an `.env.example` file to the repo.