import os
import sys
import argparse
import json
from pan_modelsecurity import Scanner, AiProfile

def parse_arguments():
    """Parses command-line arguments for model path and security group ID."""
    parser = argparse.ArgumentParser(description="Palo Alto Model Security Scan.")
    
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to the model artifact (local path) or URL (Hugging Face)."
    )
    
    parser.add_argument(
        "--security-group-id",
        required=True,
        help="The ID of the security group."
    )
    
    return parser.parse_args()

def run_model_scan(model_path: str, security_group_id: str):
    """
     Initializes the SDK, scans the model, and enforces the security policy.
    """
    try:
        # 1. Initialize the Scanner Client
        # Note: Ensure environment variables (like access keys) are set if required by your specific SDK version
        scanner = Scanner()
        ai_profile = AiProfile(profile_name=security_group_id)
        
        print(f"Initializing scan for: {model_path}")
        print(f"Using Security Profile ID: {security_group_id}")

        # 2. Determine URI Type (Local File vs. Hugging Face URL)
        if model_path.startswith("http://") or model_path.startswith("https://"):
            # It is a Hugging Face (or remote) URL
            final_model_uri = model_path
            print("Detected Remote URL. Scanning directly from source...")
        else:
            # It is a local file path
            # Ensure absolute path for safety
            abs_path = os.path.abspath(model_path)
            final_model_uri = f"file://{abs_path}"
            print(f"Detected Local File. Scanning artifact at: {abs_path}")

        # 3. Trigger the Scan
        # The SDK will upload the file hash/metadata or URL to Prisma AIRS for analysis
        scan_response = scanner.sync_scan(
            ai_profile=ai_profile,
            model_uri=final_model_uri
        )
        
        # 4. Save the full report for audit/debugging
        report_filename = 'model_scan_report.json'
        with open(report_filename, 'w') as f:
            json.dump(scan_response, f, indent=4)
        print(f"Scan complete. Report saved to {report_filename}")
        
        # 5. Policy Enforcement Check
        # Iterate through findings to determine if the build should FAIL
        policy_violated = False
        
        # The 'findings' list contains specific security issues detected
        findings = scan_response.get("findings", [])
        
        if findings:
            for finding in findings:
                # You can customize this logic (e.g., only fail on 'Critical' severity)
                # Here we fail on any error finding
                error = finding.get("error", "")
                if error:
                    policy_violated = True
                    print(f"❌ VIOLATION DETECTED: {error}")
                    # Optional: Print severity or description if available in payload
        
        if policy_violated:
            print("\n⛔ FAIL: Security violations found. Stopping pipeline.")
            sys.exit(1) # Exit code 1 signals failure to GitHub Actions/Jenkins
        else:
            print("\n✅ PASS: No security violations detected.")
            sys.exit(0) # Exit code 0 signals success

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Script failed execution. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_arguments()
    run_model_scan(args.model_path, args.security_group_id)