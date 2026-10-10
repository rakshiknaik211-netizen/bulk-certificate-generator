
import json
import time
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8000"
RECIPIENT_COUNT = 100


def api_request(url, method="GET", data=None):
    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=600) as response:
        response_body = response.read()
        return json.loads(response_body) if response_body else {}


def main():
    recipients = [
        {
            "name": f"Test Recipient {i:04d}",
            "email": f"recipient{i:04d}@example.com"
        }
        for i in range(1, RECIPIENT_COUNT + 1)
    ]

    print(f"Creating job for {RECIPIENT_COUNT} recipients...")

    start = time.perf_counter()

    job = api_request(
        f"{BASE_URL}/api/jobs/",
        method="POST",
        data={"recipients": recipients}
    )

    created = time.perf_counter()

    print(f"Job ID: {job['job_id']}")
    print("Generating actual PDF certificates...")

    result = api_request(
        f"{BASE_URL}/api/jobs/{job['job_id']}/generate",
        method="POST"
    )

    finished = time.perf_counter()

    print("\n--- BULK PROCESSING RESULTS ---")
    print(f"Recipients submitted: {RECIPIENT_COUNT}")
    print(f"Job creation time: {created - start:.2f} seconds")
    print(f"Generation time: {finished - created:.2f} seconds")
    print(f"Total time: {finished - start:.2f} seconds")
    print(f"Successful certificates: {result['successful_count']}")
    print(f"Failed certificates: {result['failed_count']}")
    print(f"Final status: {result['status']}")

    if result["successful_count"] + result["failed_count"] != RECIPIENT_COUNT:
        print("WARNING: Processed count does not match submitted count.")

    if result["failed_count"] > 0:
        print("Some certificates failed. Inspect the job records.")


if __name__ == "__main__":
    main()
