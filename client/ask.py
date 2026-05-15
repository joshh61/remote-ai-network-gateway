"""Command-line client for the AI gateway.

Example:
    python client/ask.py --url http://127.0.0.1:8080 --message "Explain NAT"
"""

import argparse
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a message to the AI gateway.")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="Base URL of the gateway")
    parser.add_argument("--message", required=True, help="Message to send")
    parser.add_argument("--token", default=os.getenv("AI_GATEWAY_TOKEN", "class-demo-token"))
    args = parser.parse_args()

    response = requests.post(
        f"{args.url.rstrip('/')}/ask",
        headers={"Authorization": f"Bearer {args.token}"},
        json={"message": args.message},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    print("AI Gateway Response")
    print("=" * 40)
    print(data["response"])
    print("\nNetwork metadata")
    print("- client_ip:", data["client_ip"])
    print("- timestamp_utc:", data["timestamp_utc"])
    print("- network_path:", data["network_path"])


if __name__ == "__main__":
    main()
