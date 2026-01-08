import sys
import os
import pprint
from dotenv import load_dotenv
from model_security_client.api import ModelSecurityAPIClient

# 1. Load the environment variables
load_dotenv()
hf_uuid = os.getenv("SECURITY_GROUP_UUID_HF")

if __name__ == "__main__":

    # 2. Check for Command Line Argument
    if len(sys.argv) < 2:
        print("❌ Error: Missing Hugging Face model URL.")
        print("Usage: python3 hf-scan.py <model_url>")
        print("Example: python3 hf-scan.py https://huggingface.co/username/modelname")
        sys.exit(1)

    # 3. Get the URL from the argument
    target_model_uri = sys.argv[1]

    # Initialize the client
    client = ModelSecurityAPIClient(
        base_url="https://api.sase.paloaltonetworks.com/aims"
    )

    print(f"🚀 Initiating scan for: {target_model_uri}")

    try:
        # 4. Perform the scan using the argument
        result = client.scan(
            security_group_uuid=hf_uuid,
            model_uri=target_model_uri  # <--- Input from command line
        )
        print(f"Scan completed: {result.eval_outcome}\n")

        # 5. Print Results
        try:
            data_dict = result.model_dump()
        except AttributeError:
            # Fallback if model_dump() is unavailable
            data_dict = result.__dict__
            
        pprint.pprint(data_dict, indent=4)

    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
