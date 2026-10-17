#!/usr/bin/env python3
"""
OCI Ampere A1 Auto-Catcher (sanitized template)
This version uses environment variables and placeholder values only; do not commit real keys or OCIDs.
"""
import os
import time
import sys
from pathlib import Path

try:
    import oci
except Exception:
    print("[ERROR] The 'oci' Python package is required. Install with: pip install oci")
    raise

# Configuration via environment variables (safe defaults are placeholders)
CONFIG_PATH = os.environ.get("OCI_CONFIG_PATH", str(Path.home() / ".oci" / "config"))
CONFIG_PROFILE = os.environ.get("OCI_CONFIG_PROFILE", "DEFAULT")
SSH_PUB_KEY_PATH = os.environ.get("SSH_PUB_KEY_PATH", str(Path.home() / ".ssh" / "your_ssh_key.pub"))
SUCCESS_FILE = os.environ.get("SUCCESS_FILE", str(Path.home() / "SERVER_CAUGHT_SUCCESS.txt"))
LOG_PATH = os.environ.get("CATCHER_LOG_PATH", str(Path.home() / "ampere_catcher_log.txt"))

# OCI resource placeholders (set these in environment or replace with real OCIDs locally)
COMPARTMENT_ID = os.environ.get("COMPARTMENT_ID", "<COMPARTMENT_OCID>")
AVAILABILITY_DOMAIN = os.environ.get("AVAILABILITY_DOMAIN", "<AVAILABILITY_DOMAIN>")
SUBNET_ID = os.environ.get("SUBNET_ID", "<SUBNET_OCID>")
IMAGE_ID = os.environ.get("IMAGE_ID", "<IMAGE_OCID>")

# Instance shape config (can be tuned). Use environment vars to override.
OCPUS = int(os.environ.get("OCPUS", "1"))
MEMORY_IN_GBS = int(os.environ.get("MEMORY_IN_GBS", "6"))
BOOT_VOLUME_GB = int(os.environ.get("BOOT_VOLUME_GB", "50"))

# Generic display name
DISPLAY_NAME = os.environ.get("DISPLAY_NAME", "your-server")
SHAPE = os.environ.get("SHAPE", "VM.Standard.A1.Flex")


def play_success_sound():
    """Play a short alert on Windows. Quietly no-op on other platforms."""
    if sys.platform.startswith("win"):
        try:
            import winsound
            for freq in [523, 659, 783, 1046]:
                winsound.Beep(freq, 200)
        except Exception:
            pass


def load_oci_config(path: str, profile: str = "DEFAULT"):
    """Load OCI config from file path and profile. Raises if missing.
    This function only reads config; it does not contain secrets.
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"OCI config file not found at: {path}")
    return oci.config.from_file(file_location=path, profile_name=profile)


def run_catcher():
    # Validate SSH public key file
    if not Path(SSH_PUB_KEY_PATH).exists():
        print(f"[ERROR] SSH public key not found at: {SSH_PUB_KEY_PATH}")
        return

    try:
        config = load_oci_config(CONFIG_PATH, CONFIG_PROFILE)
    except Exception as e:
        print(f"[ERROR] Failed to load OCI config: {e}")
        return

    # Use provided compartment ID or fall back to tenancy (only for templates)
    compartment_id = COMPARTMENT_ID
    if compartment_id.startswith("<"):
        # Fallback: use tenancy if user didn't set COMPARTMENT_ID (template behavior)
        compartment_id = config.get("tenancy")
        print("[WARN] COMPARTMENT_ID not set; falling back to tenancy OCID from config. For production use a compartment OCID.")

    compute_client = oci.core.ComputeClient(config)

    with open(SSH_PUB_KEY_PATH, "r", encoding="utf-8") as f:
        ssh_public_key = f.read().strip()

    # Construct launch details using placeholders. Replace environment variables with real values locally.
    launch_details = oci.core.models.LaunchInstanceDetails(
        compartment_id=compartment_id,
        availability_domain=AVAILABILITY_DOMAIN,
        display_name=DISPLAY_NAME,
        shape=SHAPE,
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=OCPUS,
            memory_in_gbs=MEMORY_IN_GBS,
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=IMAGE_ID,
            boot_volume_size_in_gbs=BOOT_VOLUME_GB,
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=SUBNET_ID,
            assign_public_ip=True,
        ),
        metadata={
            "ssh_authorized_keys": ssh_public_key,
        },
    )

    print("=" * 70)
    print(">>> OCI AMPERE CATCHER (sanitized template) <<<")
    print(f"Region (from config): {config.get('region', '<REGION_PLACEHOLDER>')}")
    print(f"Availability Domain: {AVAILABILITY_DOMAIN}")
    print(f"Instance Specs: {OCPUS} OCPU | {MEMORY_IN_GBS} GB RAM | {BOOT_VOLUME_GB} GB boot")
    print(f"Shape: {SHAPE}")
    print(f"SSH public key: {SSH_PUB_KEY_PATH}")
    print("=" * 70)

    attempt = 1
    # Conservative retry loop with fixed interval; user should customize for production.
    while True:
        timestamp = time.strftime("%Y-%m-%d %I:%M:%S %p")
        log_line = f"[{timestamp}] [Attempt #{attempt}] Sending launch request ({OCPUS} OCPU, {MEMORY_IN_GBS} GB RAM)..."
        print(log_line)

        try:
            Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        try:
            with open(LOG_PATH, "a", encoding="utf-8") as lf:
                lf.write(log_line + "\n")
        except Exception:
            pass

        try:
            response = compute_client.launch_instance(launch_details)
            instance = response.data

            success_msg = (
                "\n" + "=" * 70 + "\n"
                + "*** SUCCESS: Instance launched (template) ***\n"
                + f"Instance Name:    {instance.display_name}\n"
                + f"Instance ID:      {instance.id}\n"
                + f"Lifecycle State:  {instance.lifecycle_state}\n"
                + f"Availability:     {instance.availability_domain}\n"
                + f"Time Created:     {instance.time_created}\n"
                + "\nCheck the OCI Console for the public IP. Use your private SSH key to connect (not included in this repository).\n"
            )

            print(success_msg)
            try:
                with open(SUCCESS_FILE, "w", encoding="utf-8") as sf:
                    sf.write(success_msg)
            except Exception:
                pass

            try:
                with open(LOG_PATH, "a", encoding="utf-8") as lf:
                    lf.write(success_msg + "\n")
            except Exception:
                pass

            play_success_sound()
            break

        except oci.exceptions.ServiceError as e:
            # Basic handling: capacity and rate-limit are retried, others stop.
            wait_time = 60 if getattr(e, "status", None) == 429 else 35
            message = getattr(e, "message", "") or str(e)
            if "capacity" in message.lower() or getattr(e, "status", None) in [429, 500]:
                status_msg = f"  --> Status: capacity/rate limit. Retrying in {wait_time}s (Attempt #{attempt + 1})...\n"
                print(status_msg)
                try:
                    with open(LOG_PATH, "a", encoding="utf-8") as lf:
                        lf.write(status_msg)
                except Exception:
                    pass
                time.sleep(wait_time)
                attempt += 1
                continue
            else:
                err_msg = f"\n[API Error]: {getattr(e,'status', 'N/A')} - {message}\nStopping to avoid repeated invalid requests.\n"
                print(err_msg)
                try:
                    with open(LOG_PATH, "a", encoding="utf-8") as lf:
                        lf.write(err_msg)
                except Exception:
                    pass
                break

        except Exception as ex:
            err_msg = f"\n[Unexpected Error]: {ex}\nRetrying in 45 seconds...\n"
            print(err_msg)
            try:
                with open(LOG_PATH, "a", encoding="utf-8") as lf:
                    lf.write(err_msg)
            except Exception:
                pass
            time.sleep(45)
            attempt += 1


if __name__ == "__main__":
    run_catcher()
