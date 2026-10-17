import oci
import time
import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# DEMOODY ORACLE AMPERE A1 AUTO-CATCHER
# Automatically claims your Always Free 2-Core / 12 GB RAM Ampere A1 server
# as soon as a slot frees up in Oracle Hyderabad (ap-hyderabad-1).
# ==============================================================================

CONFIG_PATH = r"C:\YOUR_FOLDER_PATH\oci_config"
SSH_PUB_KEY_PATH = r"C:\YOUR_FOLDER_PATH\your_ssh_key.pub"
SUCCESS_FILE = r"C:\YOUR_FOLDER_PATH\\SERVER_CAUGHT_SUCCESS.txt"

def play_success_sound():
    try:
        import winsound
        # Play high-pitched victory chimes
        for freq in [523, 659, 783, 1046]:
            winsound.Beep(freq, 300)
    except Exception:
        pass

def run_catcher():
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Config not found at: {CONFIG_PATH}")
        return

    config = oci.config.from_file(CONFIG_PATH)
    compute_client = oci.core.ComputeClient(config)

    # Read SSH public key
    with open(SSH_PUB_KEY_PATH, "r", encoding="utf-8") as f:
        ssh_public_key = f.read().strip()

    compartment_id = config["tenancy"]
    availability_domain = "YOUR_DOMAIN"
    subnet_id = "YOUR_SUBNET_ID"
    image_id = "YOUR_IMAGE_ID" # Canonical Ubuntu 24.04 ARM64

    # Requested specs: 1 OCPU, 6 GB RAM, 50 GB Boot Volume (Always Free)
    # 1 Core / 6 GB has a significantly higher chance of catching a free slot in Hyderabad!
    ocpus = 1
    memory_in_gbs = 6
    boot_volume_gb = 50

    launch_details = oci.core.models.LaunchInstanceDetails(
        compartment_id=compartment_id,
        availability_domain=availability_domain,
        display_name="your-server",
        shape="VM.Standard.A1.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=ocpus,
            memory_in_gbs=memory_in_gbs
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=image_id,
            boot_volume_size_in_gbs=boot_volume_gb
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=subnet_id,
            assign_public_ip=True
        ),
        metadata={
            "ssh_authorized_keys": ssh_public_key
        }
    )

    log_path = r"D:\YOUR_FOLDER_PATH\catcher_log.txt"

    print("=" * 70)
    print(">>> DEMOODY ORACLE AMPERE A1 AUTO-CATCHER ACTIVE (2-CORE / 12GB OPTIMIZED) <<<")
    print(f"Datacenter:       {config.get('region', 'ap-hyderabad-1')} ({availability_domain})")
    print(f"Instance Specs:   {ocpus} OCPU (ARM Neoverse N1) | {memory_in_gbs} GB RAM | {boot_volume_gb} GB NVMe")
    print(f"Target Strategy:  High-frequency 1-Core snatch (35s interval)")
    print(f"SSH Key Attached: {SSH_PUB_KEY_PATH}")
    print("=" * 70)

    attempt = 1
    while True:
        timestamp = time.strftime("%Y-%m-%d %I:%M:%S %p")
        log_line = f"[{timestamp}] [Attempt #{attempt}] Sending launch request (2 OCPU, 12 GB RAM)..."
        print(log_line)
        
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(log_line + "\n")
        except Exception:
            pass

        try:
            response = compute_client.launch_instance(launch_details)
            instance = response.data
            
            success_msg = f"""
======================================================================
>>> SUCCESS! YOUR SERVER HAS BEEN LAUNCHED! <<<
======================================================================
Instance Name:    {instance.display_name}
Instance ID:      {instance.id}
Lifecycle State:  {instance.lifecycle_state}
Availability:     {instance.availability_domain}
Time Created:     {instance.time_created}
======================================================================
Server is now provisioning! Check your Oracle Console for Public IP.
SSH Private Key: C:\\YOUR_FOLDER_PATH\\your_ssh_key
"""
            print(success_msg)
            
            # Save success file
            with open(SUCCESS_FILE, "w", encoding="utf-8") as sf:
                sf.write(success_msg)
            
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write("\n" + success_msg + "\n")
            
            # Play alert sound
            play_success_sound()
            break
        except oci.exceptions.ServiceError as e:
            wait_time = 60 if e.status == 429 else 35
            if "Out of host capacity" in e.message or "capacity" in e.message.lower() or e.status in [500, 429]:
                status_msg = f"  --> Status: Capacity full in Hyderabad right now. Retrying in {wait_time}s (Attempt #{attempt + 1})...\n"
                print(status_msg)
                try:
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write(status_msg)
                except Exception:
                    pass
                time.sleep(wait_time)
                attempt += 1
            else:
                err_msg = f"\n[API Error]: {e.status} - {e.message}\nStopping catcher to avoid repeated invalid requests.\n"
                print(err_msg)
                try:
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write(err_msg)
                except Exception:
                    pass
                break
        except Exception as ex:
            err_msg = f"\n[Unexpected Error]: {ex}\nRetrying in 45 seconds...\n"
            print(err_msg)
            try:
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(err_msg)
            except Exception:
                pass
            time.sleep(45)
            attempt += 1

if __name__ == "__main__":
    run_catcher()
