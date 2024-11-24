import os
import csv
import base64
import requests
import argparse
import zipfile
import shutil
from bs4 import BeautifulSoup

VPN_GATE_URL = "http://www.vpngate.net/api/iphone/"
VPNBOOK_URL = "https://www.vpnbook.com/freevpn"


def create_credentials_file(output_folder, filename, username, password):
    """
    Create a credentials file for OpenVPN.
    """
    credentials_path = os.path.join(output_folder, filename)
    with open(credentials_path, 'w') as f:
        f.write(f"{username}\n{password}\n")
    os.chmod(credentials_path, 0o600)
    print(f"[INFO] Credentials file created: {credentials_path}")
    return os.path.abspath(credentials_path)


def download_vpngate_csv(output_folder, auth_file_name):
    """
    Download and process the VPNGate CSV file.
    """
    print("[VPNGate] Starting configuration process...")
    response = requests.get(VPN_GATE_URL)
    if response.status_code != 200:
        print("[VPNGate] Failed to download the CSV file.")
        return 0

    csv_content = response.text
    csv_lines = csv_content.splitlines()[1:]
    reader = csv.DictReader(csv_lines)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    auth_file_path = create_credentials_file(output_folder, auth_file_name, "vpn", "vpn")

    total_configs = sum(1 for _ in csv_lines if '#' in _)
    valid_configs = []
    for row in reader:
        hostname = row.get('#HostName')
        config_data = row.get('OpenVPN_ConfigData_Base64')
        if hostname and config_data and '*' not in hostname:
            valid_configs.append((hostname, config_data))

    print(f"[VPNGate] Found {len(valid_configs)} valid configurations.")

    created = 0
    for hostname, config_data in valid_configs:
        filename = os.path.join(output_folder, f"{hostname}.ovpn")
        if os.path.exists(filename):
            continue

        ovpn_data = base64.b64decode(config_data)
        with open(filename, 'wb') as ovpn_file:
            ovpn_file.write(ovpn_data)
        with open(filename, 'a') as ovpn_file:
            ovpn_file.write(f"\nauth-user-pass {auth_file_path}\n")
            ovpn_file.write("data-ciphers AES-256-GCM:AES-128-GCM:AES-128-CBC:CHACHA20-POLY1305\n")
        created += 1

    print("[VPNGate] Progress: 100% completed")
    print(f"[VPNGate] Configuration process completed. Created {created} new files ({len(valid_configs) - created} existents).")
    return len(valid_configs)


def download_vpnbook_configs(output_folder, password):
    """
    Download and process VPNBook .zip files.
    """
    print("[VPNBook] Starting configuration process...")
    temp_dir = os.path.join(output_folder, "temp_vpnbook")

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    response = requests.get(VPNBOOK_URL)
    if response.status_code != 200:
        print("[VPNBook] Failed to access the VPNBook page.")
        return 0

    soup = BeautifulSoup(response.text, 'html.parser')
    zip_links = [
        f"https://www.vpnbook.com{link.get('href')}" for link in soup.find_all('a', href=True)
        if link.get('href').startswith("/free-openvpn-account/") and link.get('href').endswith(".zip")
    ]

    print("[VPNBook] Found .zip files to download.")
    for zip_link in zip_links:
        zip_filename = os.path.basename(zip_link)
        zip_filepath = os.path.join(temp_dir, zip_filename)

        response = requests.get(zip_link, stream=True)
        if response.status_code == 200:
            with open(zip_filepath, 'wb') as zip_file:
                shutil.copyfileobj(response.raw, zip_file)

            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

    ovpn_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(temp_dir)
        for file in files if file.endswith(".ovpn")
    ]
    print(f"[VPNBook] Found {len(ovpn_files)} .ovpn files.")

    auth_file_path = create_credentials_file(output_folder, "vpnbook.txt", "vpnbook", password)

    created = 0
    for ovpn_file in ovpn_files:
        dest_path = os.path.join(output_folder, os.path.basename(ovpn_file))
        if os.path.exists(dest_path):
            continue

        shutil.move(ovpn_file, dest_path)
        with open(dest_path, 'a') as file:
            file.write(f"\nauth-user-pass {auth_file_path}\n")
            file.write("data-ciphers AES-256-GCM:AES-128-GCM:AES-128-CBC:CHACHA20-POLY1305\n")
        created += 1

    print("[VPNBook] Progress: 100% completed")
    if created == 0:
        print("[VPNBook] All configuration files already exist. No new files were created.")
    else:
        print(f"[VPNBook] Configuration process completed. Created {created}/{len(ovpn_files)} new files.")
    shutil.rmtree(temp_dir)
    print("[VPNBook] Temporary folder cleaned up.")
    return len(ovpn_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and configure VPN configurations from VPNGate and VPNBook")
    parser.add_argument("-o", "--output", required=True, help="Output folder to save configurations")
    parser.add_argument("-p", "--password", default="e83zu76", help="Custom password for VPNBook (default: e83zu76)")
    args = parser.parse_args()

    vpngate_total = download_vpngate_csv(args.output, "vpngate.txt")
    vpnbook_total = download_vpnbook_configs(args.output, args.password)

    total_configs = vpngate_total + vpnbook_total
    print(f"\n[INFO] Stored {total_configs} configured .ovpn files")
    print("[INFO] If the VPNBook VPNs don't work, update the password by visiting: https://www.vpnbook.com/freevpn")
    print("[INFO] Use the --password option to specify a new password for VPNBook if needed.")
