import os
import sys
import time

import requests


def main() -> int:
    base_url = os.environ.get("CI_API_URL", "http://127.0.0.1:8000")
    url = f"{base_url.rstrip('/')}/"

    for _ in range(60):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print("API is healthy")
                return 0
        except Exception:
            pass

        time.sleep(1)

    print("API did not become healthy in time")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())