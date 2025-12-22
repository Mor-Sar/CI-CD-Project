import os
import sys
import time
import requests

BASE_URL = os.getenv("BASE_URL", "http://flask_app:5000")
PATH = os.getenv("TEST_PATH", "/health")
URL = f"{BASE_URL}{PATH}"

TIMEOUT_SEC = int(os.getenv("TIMEOUT_SEC", "5"))
RETRIES = int(os.getenv("RETRIES", "40"))
SLEEP_SEC = float(os.getenv("SLEEP_SEC", "1"))

def main() -> int:
    last_err = None

    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(URL, timeout=TIMEOUT_SEC)
            if r.status_code == 200:
                try:
                    payload = r.json()
                except Exception:
                    print(f"FAILED: {URL} returned 200 but not JSON")
                    return 1

                if payload.get("status") == "ok":
                    print(f"PASSED: GET {URL} -> 200, {payload}")
                    return 0

                print(f"FAILED: unexpected JSON from {URL}: {payload}")
                return 1

            print(f"WAIT: GET {URL} -> {r.status_code} (attempt {attempt}/{RETRIES})")

        except Exception as e:
            last_err = e
            print(f"WAIT: {e} (attempt {attempt}/{RETRIES})")

        time.sleep(SLEEP_SEC)

    print(f"FAILED: server not ready at {URL}. Last error: {last_err}")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
