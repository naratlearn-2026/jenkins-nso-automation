import requests

class NSORestconfClient:
    def __init__(self, base_url, username, password, verify_tls=False):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password)
        self.verify_tls = verify_tls
        self.headers = {
            "Accept": "application/yang-data+json",
            "Content-Type": "application/yang-data+json"
        }

    def dry_run(self, resource_path, payload):
        url = f"{self.base_url}{resource_path}?dry-run=true"
        response = requests.post(
            url,
            auth=self.auth,
            headers=self.headers,
            json=payload,
            timeout=20,
            verify=self.verify_tls
        )
        return response

