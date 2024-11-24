
# Free VPN Downloader Scripts

This repository contains three Python scripts designed to download and configure free VPN `.ovpn` files for use with OpenVPN. The main script, `vpn-downloader.py`, downloads VPN files from multiple sources, while the other two scripts focus on single sources for more specific needs.

## Scripts Overview

1. **`vpn-downloader.py`** 
   - Downloads VPN configurations from both [VPNGate](http://www.vpngate.net/) and [VPNBook](https://www.vpnbook.com/freevpn).
   - Processes, configures, and prepares `.ovpn` files automatically.

2. **`vpngate-downloader.py`**
   - Downloads and configures `.ovpn` files exclusively from VPNGate's official API.

3. **`vpnbook-downloader.py`**
   - Downloads and configures `.ovpn` files exclusively from the VPNBook website.

## Requirements

- Python 3.x
- Required Python libraries:
  - `requests`
  - `bs4` (BeautifulSoup)


Install the required libraries using:

```bash
pip install -r requirements.txt
```

## Usage

### `vpn-downloader.py`

Downloads VPN configurations from both VPNGate and VPNBook.

```bash
python3 vpn-downloader.py -o <output_folder> [-p <vpnbook_password>]
```

- **`-o`**: Specifies the output folder to save the `.ovpn` files.
- **`-p`**: (Optional) Sets a custom password for VPNBook.

Example:

```bash
python3 vpn-downloader.py -o vpn-configs
```


#### Output Example

```bash
[VPNGate] Starting configuration process...
[INFO] Credentials file created: vpn-dir/vpngate.txt
[VPNGate] Found 99 valid configurations.
[VPNGate] Progress: 100% completed
[VPNGate] Configuration process completed. Created 0 new files (99 existents).
[VPNBook] Starting configuration process...
[VPNBook] Found .zip files to download.
[VPNBook] Found 48 .ovpn files.
[INFO] Credentials file created: vpn-dir/vpnbook.txt
[VPNBook] Progress: 100% completed
[VPNBook] All configuration files already exist. No new files were created.
[VPNBook] Temporary folder cleaned up.

[INFO] Stored 147 configured .ovpn files
[INFO] If the VPNBook VPNs don't work, update the password by visiting: https://www.vpnbook.com/freevpn
[INFO] Use the --password option to specify a new password for VPNBook if needed.
```

### `vpngate-downloader.py`

Downloads VPN configurations exclusively from VPNGate.

```bash
python3 vpngate-downloader.py -o <output_folder> [-af <auth_file_name>]
```

- **`-o`**: Specifies the output folder to save the `.ovpn` files.
- **`-af`**: (Optional) Sets a custom name for the authentication file (default: `vpngate.txt`).

Example:

```bash
python3 vpngate-downloader.py -o vpn-configs -af my_auth.txt
```

### `vpnbook-downloader.py`

Downloads VPN configurations exclusively from VPNBook.

```bash
python3 vpnbook-downloader.py -o <output_folder> [-p <vpnbook_password>] [-af <auth_file_name>]
```

- **`-o`**: Specifies the output folder to save the `.ovpn` files.
- **`-p`**: (Optional) Sets a custom password for VPNBook.
- **`-af`**: (Optional) Sets a custom name for the authentication file (default: `vpnbook.txt`).

Example:

```bash
python3 vpnbook-downloader.py -o vpn-configs -p newpassword -af custom_auth.txt
```

