import os
import sys
import time
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

# Retry parameters
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def get_with_retry(url, description):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"{description} (attempt {attempt}/{MAX_RETRIES})")
            resp = requests.get(
                url,
                auth=AUTH,
                headers=HEADERS,
                timeout=(10, 60),  # connect, read
                stream=True,
                verify=False
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"WARNING: {description} failed: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY}s...\n")
                time.sleep(RETRY_DELAY)
            else:
                print("ERROR: Exhausted retries")
                raise

# -------------------------------------------------
# STEP 1: Inventory validation
# -------------------------------------------------

inventory_url = f"{NSO_BASE_URL}/tailf-ncs:devices/device"
print(f"\n[1/2] Querying NSO device inventory")
print(f"URL: {inventory_url}")

try:
    data = get_with_retry(inventory_url, "Fetching device inventory")
except Exception:
    sys.exit(1)

devices = data.get("tailf-ncs:device", [])

if not devices:
    print("ERROR: No devices found in NSO inventory")
    sys.exit(1)

print(f"Found {len(devices)} device(s)\n")

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
        sys.exit(1)
    else:
        print("  ✅ Inventory validation OK\n")

print("Inventory validation passed\n")

# -------------------------------------------------
# STEP 2: check-sync (authoritative)
# -------------------------------------------------

check_sync_url = f"{NSO_BASE_URL}/../operations/tailf-ncs:devices/check-sync"
print("[2/2] Running NSO check-sync operation")
print(f"URL: {check_sync_url}")

for attempt in range(1, MAX_RETRIES + 1):
    try:
        resp = requests.post(
            check_sync_url,
            auth=AUTH,
            headers=HEADERS,
            timeout=(10, 90),
            verify=False
        )
        resp.raise_for_status()
        data = resp.json()
        break
    except requests.exceptions.RequestException as e:
        print(f"WARNING: check-sync failed: {e}")
        if attempt < MAX_RETRIES:
            print(f"Retrying in {RETRY_DELAY}s...\n")
            time.sleep(RETRY_DELAY)
        else:
            print("ERROR: check-sync failed after retries")
            sys.exit(1)

results = data.get("tailf-ncs:output", {}).get("sync-result", [])

if not results:
    print("ERROR: No sync results returned")
    sys.exit(1)

print(f"\nReceived sync results for {len(results)} device(s)\n")

for r in results:
    device = r.get("device")
    result = r.get("result")

    print(f"Device: {device}")
    print(f"  Sync Result: {result}")

    if result != "in-sync":
        print("  ❌ Device out-of-sync\n")
        sys.exit(1)
    else:
        print("  ✅ Device in-sync\n")

print("\nNSO health validation completed successfully")

