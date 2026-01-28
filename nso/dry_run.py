import os
import sys
import json
from nso.client import NSORestconfClient

NSO_BASE_URL = os.getenv("NSO_BASE_URL")
NSO_RESOURCE = os.getenv("NSO_RESOURCE")
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")

if not all([NSO_BASE_URL, NSO_RESOURCE, USERNAME, PASSWORD]):
    print("ERROR: Missing NSO configuration")
    sys.exit(1)

with open("nso/payloads/example_service.json") as f:
    payload = json.load(f)

client = NSORestconfClient(
    base_url=NSO_BASE_URL,
    username=USERNAME,
    password=PASSWORD,
    verify_tls=False
)

print(f"Running NSO dry-run against: {NSO_RESOURCE}")

response = client.dry_run(NSO_RESOURCE, payload)

print(f"HTTP Status Code: {response.status_code}")

if response.status_code not in (200, 201):
    print("ERROR: NSO dry-run failed")
    print(response.text)
    sys.exit(1)

data = response.json()

diff = (
    data.get("ncs:dry-run", {})
        .get("cli", "")
)

if diff:
    print("\nNSO DRY-RUN DIFF")
    print("=" * 50)
    print(diff)
    print("=" * 50)
else:
    print("No configuration changes detected")

print("NSO dry-run completed successfully")

