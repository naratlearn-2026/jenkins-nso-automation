import os
import sys
import requests

NSO_BASE_URL = os.getenv("NSO_BASE_URL")
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")

if not all([NSO_BASE_URL, USERNAME, PASSWORD]):
    print("ERROR: Missing NSO configuration")
    sys.exit(1)

AUTH = (USERNAME, PASSWORD)
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# -------------------------------------------------
# STEP 1: Inventory & operational state validation
# -------------------------------------------------

inventory_url = f"{NSO_BASE_URL}/tailf-ncs:devices/device"
print(f"\n[1/2] Querying NSO device inventory")
print(f"URL: {inventory_url}")

resp = requests.get(
    inventory_url,
    auth=AUTH,
    headers=HEADERS,
    timeout=15,
    verify=False
)

if resp.status_code != 200:
    print(f"ERROR: Failed to fetch device inventory (HTTP {resp.status_code})")
    print(resp.text)
    sys.exit(1)

data = resp.json()
devices = data.get("tailf-ncs:device", [])

if not devices:
    print("ERROR: No devices found in NSO inventory")
    sys.exit(1)

print(f"Found {len(devices)} device(s)\n")

inventory_failed = False

for dev in devices:
    name = dev.get("name")
    state = dev.get("state", {})
    admin = state.get("admin-state")
    oper = state.get("oper-state")

    print(f"Device: {name}")
    print(f"  Admin State : {admin}")
    print(f"  Oper State  : {oper}")

    if admin != "unlocked" or oper not in ("enabled", "up"):
        print("  ❌ Inventory validation FAILED\n")
        inventory_failed = True
    else:
        print("  ✅ Inventory validation OK\n")

if inventory_failed:
    print("Inventory validation failed — stopping pipeline")
    sys.exit(1)

print("Inventory validation passed\n")

# -------------------------------------------------
# STEP 2: Authoritative sync check (action)
# -------------------------------------------------

check_sync_url = f"{NSO_BASE_URL}/../operations/tailf-ncs:devices/check-sync"
print("[2/2] Running NSO check-sync operation")
print(f"URL: {check_sync_url}")

resp = requests.post(
    check_sync_url,
    auth=AUTH,
    headers=HEADERS,
    timeout=30,
    verify=False
)

if resp.status_code != 200:
    print(f"ERROR: check-sync failed (HTTP {resp.status_code})")
    print(resp.text)
    sys.exit(1)

data = resp.json()
results = data.get("tailf-ncs:output", {}).get("sync-result", [])

if not results:
    print("ERROR: No sync results returned")
    sys.exit(1)

sync_failed = False

print(f"\nReceived sync results for {len(results)} device(s)\n")

for r in results:
    device = r.get("device")
    result = r.get("result")

    print(f"Device: {device}")
    print(f"  Sync Result: {result}")

    if result != "in-sync":
        print("  ❌ Device out-of-sync\n")
        sync_failed = True
    else:
        print("  ✅ Device in-sync\n")

if sync_failed:
    print("One or more devices are out-of-sync")
    sys.exit(1)

print("All devices are in-sync")
print("\nNSO device validation completed successfully")

