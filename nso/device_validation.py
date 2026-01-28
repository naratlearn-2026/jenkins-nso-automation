import os
import sys
import requests

NSO_BASE_URL = os.getenv("NSO_BASE_URL")
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")

if not all([NSO_BASE_URL, USERNAME, PASSWORD]):
    print("ERROR: Missing NSO configuration")
    sys.exit(1)

url = f"{NSO_BASE_URL}/tailf-ncs:devices/device"

headers = {
    "Accept": "application/yang-data+json"
}

print(f"Querying NSO device inventory: {url}")

response = requests.get(
    url,
    auth=(USERNAME, PASSWORD),
    headers=headers,
    timeout=15,
    verify=False
)

if response.status_code != 200:
    print(f"ERROR: Failed to fetch devices (HTTP {response.status_code})")
    print(response.text)
    sys.exit(1)

data = response.json()

devices = data.get("tailf-ncs:device", [])

if not devices:
    print("ERROR: No devices found in NSO")
    sys.exit(1)

print(f"Found {len(devices)} device(s)\n")

failed = False

for dev in devices:
    name = dev.get("name")
    admin = dev.get("state", {}).get("admin-state")
    oper = dev.get("state", {}).get("oper-state")
    sync = dev.get("state", {}).get("sync-state")

    print(f"Device: {name}")
    print(f"  Admin State : {admin}")
    print(f"  Oper State  : {oper}")
    print(f"  Sync State  : {sync}")

    if admin != "unlocked" or oper != "up" or sync != "in-sync":
        print("  ❌ Device validation FAILED\n")
        failed = True
    else:
        print("  ✅ Device validation OK\n")

if failed:
    print("One or more devices failed validation")
    sys.exit(1)

print("All devices validated successfully")

