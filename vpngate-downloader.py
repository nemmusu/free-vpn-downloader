import os
import csv
import base64
import requests
import argparse

def create_credentials_file(username, password, output_folder, auth_file_name):
    """
    Create a credentials file for OpenVPN with a custom name.
    """
    credentials_path = os.path.join(output_folder, auth_file_name)
    try:
        with open(credentials_path, 'w') as f:
            f.write(f"{username}\n{password}\n")
        os.chmod(credentials_path, 0o600)  # Set restrictive permissions
        print(f"Credentials file created at: {credentials_path}")
    except Exception as e:
        print(f"Error creating the credentials file: {e}")
    return os.path.abspath(credentials_path)


def download_vpngate_csv(url, output_folder, auth_file_name):
    """
    Download the CSV file from VPN Gate and create .ovpn configuration files.
    """
    # Default credentials
    username = "vpn"
    password = "vpn"

    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            print("Error downloading the VPN Gate CSV file.")
            return

        csv_content = response.text
        csv_lines = csv_content.splitlines()[1:]
        reader = csv.DictReader(csv_lines)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create the credentials file
        auth_file_path = create_credentials_file(username, password, output_folder, auth_file_name)

        total = sum(1 for _ in csv_lines)  # Count the total number of lines
        print(f"Total configurations found: {total}")

        created = 0
        for row in reader:
            hostname = row.get('#HostName')
            if not hostname:
                continue

            filename = os.path.join(output_folder, f"{hostname}.ovpn")
            if os.path.exists(filename):
                print(f"File {filename} already exists, skipping.")
                continue

            config_data_base64 = row.get('OpenVPN_ConfigData_Base64')
            if not config_data_base64:
                print(f"Host {hostname} does not contain base64 configuration, skipping.")
                continue

            try:
                ovpn_data = base64.b64decode(config_data_base64)
                with open(filename, 'wb') as ovpn_file:
                    ovpn_file.write(ovpn_data)

                # Add the auth-user-pass directive with the absolute path
                with open(filename, 'a') as ovpn_file:
                    ovpn_file.write(f"\nauth-user-pass {auth_file_path}\n")
                    ovpn_file.write("data-ciphers AES-256-GCM:AES-128-GCM:AES-128-CBC:CHACHA20-POLY1305\n")

                created += 1
                print(f"[{created}/{total}] File {filename} configured successfully.")
            except Exception as e:
                print(f"Error saving the file {filename}: {e}")
                continue

        print(f"Configuration creation complete. Files created: {created}/{total}")
    except Exception as e:
        print(f"Error during the process: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and configure VPN Gate .ovpn files")
    parser.add_argument("-o", "--output", required=True, help="Output folder to save .ovpn files")
    parser.add_argument("-af", "--auth-file", default="vpngate.txt", help="Custom name for the authentication file (default: auth.txt)")
    args = parser.parse_args()

    VPN_GATE_URL = "http://www.vpngate.net/api/iphone/"

    download_vpngate_csv(VPN_GATE_URL, args.output, args.auth_file)
