import os
import argparse
import requests
import zipfile
import shutil
from bs4 import BeautifulSoup

def download_vpnbook_configs(output_folder, password, auth_file_name):
    """
    Downloads .zip files from VPNBook, extracts them, and configures the .ovpn files.
    """
    vpnbook_url = "https://www.vpnbook.com/freevpn"
    temp_dir = os.path.join(output_folder, "temp_vpnbook")

    # VPNBook credentials
    username = "vpnbook"

    # Create necessary folders
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Crawl the VPNBook page
        response = requests.get(vpnbook_url)
        if response.status_code != 200:
            print("Error accessing the VPNBook page.")
            return

        # Parse the HTML page to find .zip file links
        soup = BeautifulSoup(response.text, 'html.parser')
        zip_links = [
            f"https://www.vpnbook.com{link.get('href')}" for link in soup.find_all('a', href=True)
            if link.get('href').endswith(".zip") and "vpnbook-openvpn" in link.get('href')
        ]

        if not zip_links:
            print("No VPN files found on the page.")
            return

        print(f"Found {len(zip_links)} files to download.")

        # Download and process each .zip file
        for i, zip_link in enumerate(zip_links, start=1):
            zip_filename = os.path.basename(zip_link)
            zip_filepath = os.path.join(temp_dir, zip_filename)

            print(f"[{i}/{len(zip_links)}] Downloading {zip_filename}...")
            zip_response = requests.get(zip_link, stream=True)
            if zip_response.status_code == 200:
                with open(zip_filepath, 'wb') as zip_file:
                    shutil.copyfileobj(zip_response.raw, zip_file)
                print(f"{zip_filename} downloaded successfully.")
            else:
                print(f"Error downloading {zip_filename}.")
                continue

            # Extract the contents of the zip file
            print(f"Extracting {zip_filename}...")
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

        # Find and process all .ovpn files
        ovpn_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".ovpn"):
                    full_path = os.path.join(root, file)
                    ovpn_files.append(full_path)

        print(f"Total .ovpn files found: {len(ovpn_files)}")

        # Create the auth file with the specified name
        auth_file_path = os.path.abspath(os.path.join(output_folder, auth_file_name))
        with open(auth_file_path, 'w') as auth_file:
            auth_file.write(f"{username}\n{password}\n")
        os.chmod(auth_file_path, 0o600)
        print(f"Auth file created at: {auth_file_path}")

        # Move and update the .ovpn files
        for ovpn_file in ovpn_files:
            try:
                # Move the .ovpn file to the output folder
                dest_path = os.path.join(output_folder, os.path.basename(ovpn_file))
                shutil.move(ovpn_file, dest_path)

                # Update the .ovpn file with the absolute path of the auth file
                with open(dest_path, 'a') as file:
                    file.write(f"\nauth-user-pass {auth_file_path}\n")
                    file.write("data-ciphers AES-256-GCM:AES-128-GCM:AES-128-CBC:CHACHA20-POLY1305\n")

                print(f"Configured: {dest_path}")
            except Exception as e:
                print(f"Error configuring {ovpn_file}: {e}")

        print("Process completed. All .ovpn files have been configured.")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        # Clean up the temporary folder
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("Temporary folder removed.")

    print("\n[INFO] If the VPNs don't work, update the password by visiting: https://www.vpnbook.com/freevpn")
    print("[INFO] Use the --password option to specify a custom password if needed.")
    print(f"[INFO] Use the --auth-file option to specify a custom name for the authentication file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and configure VPNBook .ovpn files")
    parser.add_argument("-o", "--output", required=True, help="Output folder to save configured .ovpn files")
    parser.add_argument("-p", "--password", default="e83zu76", help="Password for the auth file (default: e83zu76)")
    parser.add_argument("-af", "--auth-file", default="vpnbook.txt", help="Custom name for the authentication file (default: auth.txt)")
    args = parser.parse_args()

    download_vpnbook_configs(args.output, args.password, args.auth_file)
