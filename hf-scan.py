import argparse
import sys
from model_security_client import ModelSecurityClient


def main():
    parser = argparse.ArgumentParser(
        description="Scan a Hugging Face model using Model Security"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Hugging Face model ID (e.g. facebook/opt-125m)"
    )
    parser.add_argument(
        "--fail-on",
        default="high",
        choices=["low", "medium", "high"],
        help="Fail pipeline if findings >= this severity"
    )

    args = parser.parse_args()
    model_id = args.model
    fail_on = args.fail_on

    print(f"🔍 Starting real security scan for HF model: {model_id}")

    # Initialize client (auth comes from env vars)
    client = ModelSecurityClient()

    # ---- REAL SCAN ----
    result = client.scan_huggingface_model(model_id)

    # Example normalized result structure
    findings = result.get("summary", {})
    high = findings.get("high", 0)
    medium = findings.get("medium", 0)
    low = findings.get("low", 0)

    print("📊 Scan results:")
    print(f"  High   : {high}")
    print(f"  Medium : {medium}")
    print(f"  Low    : {low}")

    # ---- CI POLICY ----
    if fail_on == "high" and high > 0:
        print("❌ Failing due to HIGH severity findings")
        sys.exit(1)

    if fail_on == "medium" and (high > 0 or medium > 0):
        print("❌ Failing due to MEDIUM+ severity findings")
        sys.exit(1)

    if fail_on == "low" and (high > 0 or medium > 0 or low > 0):
        print("❌ Failing due to LOW+ severity findings")
        sys.exit(1)

    print("✅ Model passed security policy")
    sys.exit(0)


if __name__ == "__main__":
    main()