# Oracle Ampere Catcher (Ampere A1 Auto-Catcher)

WARNING: This repository previously contained example SSH key files and a sample OCI config. NEVER commit private keys, credentials, or other secrets into source control. Remove any real keys from this repository and add them to your .gitignore.

This repository contains a small Python script (oci_ampere_catcher.py) that repeatedly attempts to launch an Oracle Cloud Infrastructure (OCI) Ampere A1 instance (VM.Standard.A1.Flex) as soon as capacity is available in a chosen region/availability domain. It is intended as a convenience tool for people trying to automatically claim Always Free or spot Ampere A1 slots when capacity opens up.

This README is a step-by-step, beginner-friendly guide to configure and run the catcher safely, plus an audit of the code and suggested fixes/improvements.

---

## Quick summary of what's inside

Top-level files you should care about:
- `oci_ampere_catcher.py` — main script that polls the OCI API and attempts to launch an instance.
- `oci_config` — example OCI config file (contains placeholders). Do not use in production as-is.
- `bitefast_ssh_key` / `bitefast_ssh_key.pub` — placeholder files; do NOT commit private keys.

---

## Repository audit (what I checked and issues found)

1. Paths and platform assumptions
   - The script uses hard-coded Windows-style paths (e.g. `C:\YOUR_FOLDER_PATH\...`, `D:\YOUR_FOLDER_PATH\catcher_log.txt`). This will break on Linux/macOS.
   - The script attempts to reconfigure sys.stdout encoding on Windows only. Good intent, but make paths OS-agnostic.

2. Secrets present / accidental commit risk
   - Repository includes placeholder files for SSH keys and an `oci_config` sample. Make sure no real private keys or real OCIDs are committed. Add a `.gitignore` that excludes keys and any files with secrets.

3. OCI usage correctness
   - `oci.config.from_file(CONFIG_PATH)` is used; this is valid if `CONFIG_PATH` points to the full file path of the config file. Confirm the format matches OCI SDK expectations (profile sections, key_file path, etc.).
   - The script uses `config['tenancy']` as `compartment_id`. That will usually be the root tenancy OCID — which works only if you intend to use the tenancy as the compartment. Most users should use a proper compartment OCID instead.
   - `availability_domain`, `subnet_id`, and `image_id` are hard-coded placeholder strings and must be replaced with valid values.

4. Messaging / spec inconsistencies
   - The script prints "Sending launch request (2 OCPU, 12 GB RAM)..." but the configured `ocpus` and `memory_in_gbs` are set to 1 and 6 respectively. Update text to reflect actual launch_details.

5. Error handling and rate-limiting
   - The script catches `oci.exceptions.ServiceError` and retries on capacity errors or 429 rate limit responses. That's reasonable, but be careful: excessive automated retries can be flagged by rate limiting or usage policies. Consider exponential backoff + jitter.

6. Missing dependency declaration
   - There is no `requirements.txt` or `pyproject.toml`. The code depends on the `oci` SDK (Oracle Cloud Infrastructure SDK for Python). Add a `requirements.txt` with `oci` and a tested Python version.

7. Logging and monitoring
   - The script writes to a log path (`D:\YOUR_FOLDER_PATH\catcher_log.txt`) and creates a success file when an instance is launched. Consider using a configurable path or environment variable.

8. Security & Cost
   - Launching instances in OCI may incur charges if you exceed free-tier limits or use non-free shapes/resources. This script will create instances and may use boot volumes — monitor your tenancy to avoid unexpected bills.

---

## What I changed / added

I added this `README.md` with detailed instructions and security notes. If you'd like, I can also:
- Add a `requirements.txt` (recommended).
- Add a `.gitignore` to exclude keys and sensitive files.
- Update the script to be cross-platform, configurable via environment variables/CLI args, and to use exponential backoff with jitter.

I can commit these changes if you want me to — tell me which changes you want me to add automatically.

---

## Step-by-step guide (beginner-friendly)

Prerequisites
- A computer with Python 3.8+ installed. Confirm by running:

  python --version

- An OCI account with API keys configured and a compartment where you can launch instances.
- The OCI Python SDK installed:

  python -m pip install oci

(If you plan to run on low-end machines, ensure Python is up-to-date and pip is installed.)

1) Create an SSH key pair (if you don't already have one)

- On macOS / Linux:

  ssh-keygen -t rsa -b 4096 -f ~/.ssh/your_ssh_key

  This produces `~/.ssh/your_ssh_key` (private) and `~/.ssh/your_ssh_key.pub` (public).

- On Windows (PowerShell):

  ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\\.ssh\\your_ssh_key

  Copy the `.pub` file contents for the next steps.

2) Configure OCI CLI / API credentials

- Create an API key via the OCI console (Identity → Users → Your user → API Keys), or follow the official docs to create an API key, download the private key, and note the OCID, fingerprint, etc.
- Create an `oci_config` file (or reuse the example `oci_config` in this repo) with a `[DEFAULT]` profile block. Example `oci_config` (replace placeholders):

  [DEFAULT]
  user=ocid1.user.oc1..example...
  fingerprint=aa:bb:cc:...
  tenancy=ocid1.tenancy.oc1..example...
  region=ap-hyderabad-1
  key_file=/home/you/.oci/oci_api_key.pem

  - Ensure the `key_file` path points to your private API key file (not your SSH key).
  - Save this file somewhere safe, e.g. `~/.oci/config`.

3) Find required OCI values

- Compartment OCID: in OCI console, navigate to the compartment you want and copy the OCID. Using the tenancy OCID as compartment will work only if you intend to use the root compartment — most users should use a compartment OCID.
- Availability Domain: list Availability Domains for your region in the console or using OCI CLI `oci iam availability-domain list`.
- Subnet OCID: find or create a subnet in the VCN that allows public IP (if you want a public IP) and copy its OCID.
- Image OCID: find a public image you want to boot from (for example Canonical Ubuntu 24.04 ARM64). You can find image OCIDs via the console or using OCI CLI search commands. Example (OCI CLI):

  oci compute image list --compartment-id <tenancy-or-compartment> --operating-system 'Canonical' --operating-system-version '24.04' --architecture 'ARM64'

  Pick the `id` field of the image you want.

4) Update the script configuration

- Edit `oci_ampere_catcher.py` and replace the placeholder constants near the top with paths and OCIDs you gathered:

  CONFIG_PATH = r"C:\path\to\oci_config"  # or "/home/you/.oci/config"
  SSH_PUB_KEY_PATH = r"C:\path\to\your_ssh_key.pub"
  SUCCESS_FILE = r"C:\path\to\SERVER_CAUGHT_SUCCESS.txt"

  Then inside run_catcher(), replace:

  compartment_id = config['tenancy']  # Replace with a compartment OCID if you want a non-root compartment
  availability_domain = "YOUR_DOMAIN"
  subnet_id = "YOUR_SUBNET_ID"
  image_id = "YOUR_IMAGE_ID"

  with real values.

5) Optional: make the script configuration cross-platform and safer

- Instead of editing constants, export environment variables and read them in the script. Example (bash):

  export OCI_CONFIG_PATH=/home/you/.oci/config
  export SSH_PUB_KEY_PATH=/home/you/.ssh/your_ssh_key.pub
  export COMPARTMENT_ID=ocid1.compartment.oc1..example...
  export SUBNET_ID=ocid1.subnet.oc1..example...
  export IMAGE_ID=ocid1.image.oc1..example...

  Then modify the script to read os.environ values (I can provide a patch for this).

6) Run the script

- From the folder containing `oci_ampere_catcher.py` run:

  python oci_ampere_catcher.py

- The script will print status lines and append to the log file configured inside the script. It will create the success file when a server is launched.

7) After a successful launch

- The script prints instance details and writes them to the success file. Use the SSH private key (the one corresponding to the public key you supplied) to connect:

  ssh -i /path/to/your_ssh_key opc@<public_ip>

  (Replace `opc` with the appropriate default username for the chosen image: `ubuntu` for Canonical Ubuntu images, `opc` for Oracle Linux images, etc.)

8) Stop the script when done

- If you successfully launched and want to avoid further instances, stop the script (Ctrl+C) or delete/modify the success file logic.

---

## Recommended immediate fixes and improvements

1. Make the script configurable via CLI args or environment variables instead of editing constants. Example: use argparse for `--config`, `--ssh-pub`, `--compartment`, etc.
2. Replace hard-coded Windows paths with os.path.join and allow POSIX paths. Use pathlib.
3. Add a `requirements.txt` with `oci` and optionally `python-dotenv`.
4. Add `.gitignore` to exclude any private key files and local config files.
5. Improve retry policy: use exponential backoff with jitter instead of a fixed 35s interval. Example strategy: base=5s, backoff *= 2 up to max 300s, add random jitter ±25%.
6. Validate OCI response fields before using them (defensive checks) and add more informative error logging.
7. Add a safety mechanism so the script stops after a configurable number of attempts or when charges would be incurred.
8. Replace `config['tenancy']` with a separate `compartment_id` config value; do not assume tenancy == compartment.

---

## Troubleshooting

- If the script prints capacity errors: this means there is no free Ampere A1 capacity in that AD/region. The script will retry; check logs and consider trying a different AD or wait.
- If you get `OCI` authentication errors: verify the `oci_config` file path, that the `key_file` points to a valid private key, and that the API key fingerprint matches the console.
- If you get permission errors: ensure the user whose API key you use has `compute.instance.launch` permissions for the chosen compartment.
- If the script fails with a `TypeError` constructing launch details: ensure your OCI Python SDK is up to date (pip install --upgrade oci) and that you are using supported shapes.

---

## Example minimal `requirements.txt`

oci

---

## Security & Cost reminder

- This script will create instances in your tenancy. Always monitor usage and delete unwanted instances and boot volumes to avoid charges.
- Never commit private keys or credentials. Use IAM policies and compartment restrictions to limit damage if credentials are compromised.

---

## License & Contribution

If this is your personal project, add a license file (e.g. MIT) if you want permissive reuse. If you'd like, I can add one.

Contributions welcome: issues, PRs. If you'd like, I can submit a PR that:
- Adds `requirements.txt` and `.gitignore`
- Makes the script configurable and cross-platform
- Improves retry/backoff logic

