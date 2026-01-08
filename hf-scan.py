import argparse
import sys
from model_security_client.client import ModelSecurityClient  # adjust if SDK differs

def main():
    parser = argparse.ArgumentParser(description="Scan a Hugging Face model")
    parser.add_argument("--model", required=True)
    parser.add_argument("--fail-on", default="high", choices=["low", "medium", "high"])

    args = parser.parse_args()
    model_id = args.model

    print(f"🔍 Scanning Hugging Face model: {model_id}")

    client = ModelSecurityClient()
    result = client.scan_huggingface_model(model_id)

    summary = result.get("summary", {})
    high = summary.get("high", 0)
    medium = summary.get("medium", 0)
    low = summary.get("low", 0)

    print(f"Results → High:{high}, Medium:{medium}, Low:{low}")

    if args.fail_on == "high" and high > 0:
        sys.exit(1)
    if args.fail_on == "medium" and (high > 0 or medium > 0):
        sys.exit(1)
    if args.fail_on == "low" and (high > 0 or medium > 0 or low > 0):
        sys.exit(1)

    print("✅ Scan passed")

if __name__ == "__main__":
    main()