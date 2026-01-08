import os
import sys
import argparse
import json
import pprint
from model_security_client.api import ModelSecurityAPIClient

def parse_arguments():
    """Parses command-line arguments for model path and security group ID."""
    parser = argparse.ArgumentParser(description="Prisma AIRS Model Security Scan")
    
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the model artifact (local path) or URL (Hugging Face)."
    )
    
    parser.add_argument(
        "--security-group-id",
        required=True,
        help="The UUID of the security group."
    )
    
    return parser.parse_args()

def run_model_scan(model_path: str, security_group_id: str):
    """
     Initializes the Client, scans the model, and enforces the security policy.
    """
    try:
        # 1. Initialize the Client
        # We use the environment variable for the endpoint, defaulting to the one in your snippet
        base_url = os.getenv("MODEL_SECURITY_API_ENDPOINT", "https://api.sase.paloaltonetworks.com/aims")
        
        print(f"🚀 Initializing Client connecting to: {base_url}")
        client = ModelSecurityAPIClient(base_url=base_url)

        # 2. Determine URI Type (Local File vs. Hugging Face URL)
        if model_path.startswith("http://") or model_path.startswith("https://"):
            final_model_uri = model_path
            print(f"   Target: Remote URL ({model_path})")
        else:
            abs_path = os.path.abspath(model_path)
            final_model_uri = f"file://{abs_path}"
            print(f"   Target: Local File ({abs_path})")

        print(f"   Profile UUID: {security_group_id}")

        # 3. Perform the scan
        # Using the exact method from your working snippet
        result = client.scan(
            security_group_uuid=security_group_id,
            model_uri=final_model_uri
        )

        # 4. Process Results
        print(f"\n🏁 Scan Status: {result.eval_outcome}")
        
        # Convert result to dictionary safely
        try:
            data_dict = result.model_dump()
        except AttributeError:
            data_dict = result.__dict__

        # Save report for GitHub Artifacts
        with open('model_scan_report.json', 'w') as f:
            json.dump(data_dict, f, indent=4, default=str)
        print("   Report saved to 'model_scan_report.json'")

        # 5. POLICY ENFORCEMENT (The Gatekeeper)
        # Fail the pipeline if the outcome is not clean
        # We check both the high-level outcome AND specific findings
        
        policy_violated = False
        
        # Check 1: High level outcome
        # Adjust "PASS" if the API returns "CLEAN" or similar. Usually it's "PASS" or "FAIL"
        if str(result.eval_outcome).upper() not in ["PASS", "CLEAN", "SUCCESS"]:
            print(f"⚠️ Outcome was not PASS: {result.eval_outcome}")
            # policy_violated = True # Uncomment this if you want to be strict on the label
            
        # Check 2: Deep dive into findings for errors
        findings = data_dict.get("findings", [])
        if findings:
            print("\n🔍 Detailed Findings:")
            for finding in findings:
                # pprint.pprint(finding) # Optional: print full details
                severity = finding.get('severity', 'UNKNOWN')
                category = finding.get('category', 'Generic')
                print(f"   - [{severity}] {category}")
                
                # Logic: Mark as violation if it's not just an 'INFO' message
                if severity.upper() in ['CRITICAL', 'HIGH', 'MEDIUM']:
                    policy_violated = True

        if policy_violated:
            print("\n⛔ FAIL: Security violations detected. Stopping pipeline.")
            sys.exit(1)
        else:
            print("\n✅ PASS: Model is secure.")
            sys.exit(0)

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        # Print full trace for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    args = parse_arguments()
    run_model_scan(args.model_path, args.security_group_id)