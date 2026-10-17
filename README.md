# Oracle Ampere Catcher (Ampere A1 Auto-Catcher)

WARNING: This repository previously contained example SSH key files and a sample OCI config. NEVER commit private keys, credentials, or other secrets into source control. Remove any real keys from this repository and add them to your .gitignore.

This repository contains a small Python script (`oci_ampere_catcher.py`) that repeatedly attempts to launch an Oracle Cloud Infrastructure (OCI) Ampere A1 instance (VM.Standard.A1.Flex) as soon as capacity is available in a chosen region/availability domain. It is intended as a convenience tool for people trying to automatically claim Always Free or spot Ampere A1 slots when capacity opens up.

This README is a step-by-step, beginner-friendly guide to configure and run the catcher safely, plus an audit of the code and suggested fixes/improvements.

---

## Quick summary of what's inside

Top-level files you should care about:
- `oci_ampere_catcher.py` — main script that polls the OCI API and attempts to launch an instance (sanitized template).
- `oci_config` — example OCI config file (contains placeholders). Replace with your local config and do not commit real credentials.
- `your_ssh_key` / `your_ssh_key.pub` — placeholder files. Do NOT commit private keys. Keep only template/public examples.
- `.gitignore` — added to help prevent accidental commits of keys and local files.
- `requirements.txt` — Python dependencies.

---

## What I changed and why

- Replaced hard-coded Windows/absolute paths with environment-variable-driven configuration in `oci_ampere_catcher.py`.
- Replaced any example/placeholder OCIDs and sensitive paths with clear template placeholders like `<COMPARTMENT_OCID>`, `<IMAGE_OCID>`, and `<REGION>`.
- Renamed example SSH files to `your_ssh_key` / `your_ssh_key.pub` (placeholders) and cleared any content to avoid accidental leakage.
- Added `.gitignore` to exclude private keys, local config files, and logs.
- Added `requirements.txt` listing the `oci` SDK.

---

## How to use (short)

1. Install dependencies:

   python -m pip install -r requirements.txt

2. Prepare your OCI environment and keys locally (do NOT commit them):
   - Create an OCI config file (default `~/.oci/config`) or set `OCI_CONFIG_PATH` to point to it.
   - Set environment variables or edit the top of `oci_ampere_catcher.py` locally to provide real values for:
     - COMPARTMENT_ID, AVAILABILITY_DOMAIN, SUBNET_ID, IMAGE_ID
     - SSH_PUB_KEY_PATH (path to your public SSH key)

   Example (bash):

     export OCI_CONFIG_PATH=~/.oci/config
     export COMPARTMENT_ID=ocid1.compartment.oc1..<your-compartment>
     export SUBNET_ID=ocid1.subnet.oc1..<your-subnet>
     export IMAGE_ID=ocid1.image.oc1..<your-image>
     export SSH_PUB_KEY_PATH=~/.ssh/your_ssh_key.pub

3. Run the script:

   python oci_ampere_catcher.py

The script will log attempts to the log path (see CATCHER_LOG_PATH env var) and write a success file when a server is created.

---

## Next steps I can take for you (optional)

- Add argparse support so configuration can be passed via CLI rather than environment variables.
- Implement exponential backoff with jitter for retries.
- Add a GitHub Actions workflow to run static checks or tests.

If you want any of these changes, tell me which ones and I will implement them.
