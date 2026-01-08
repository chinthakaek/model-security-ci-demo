import sys
import os
import pprint
from dotenv import load_dotenv
from model_security_client.api import ModelSecurityAPIClient

# 1. Load the environment variables
load_dotenv()
local_uuid = os.getenv("SECURITY_GROUP_UUID_LOCAL")

if __name__ == "__main__":
    
    # 2. Check for Command Line Argument
    if len(sys.argv) < 2:
        print("❌ Error: Missing model path.")
        print("Usage: python3 local-scan.py <path_to_model>")
        print("Example: python3 local-scan.py /Users/name/models/my-model")
        sys.exit(1)

    # 3. Get the path from the argument
    user_model_path = sys.argv[1]

    # Verify path exists before trying to scan
    if not os.path.exists(user_model_path):
        print(f"❌ Error: The path '{user_model_path}' does not exist.")
        sys.exit(1)

    print(f"✅ Scanning model at: {user_model_path}")

    # 4. Initialize the client
    client = ModelSecurityAPIClient(
        base_url="https://api.sase.paloaltonetworks.com/aims"
    )

    try:
        # 5. Perform the scan using the argument input
        result = client.scan(
            security_group_uuid=local_uuid,
            model_path=user_model_path
        )
        print(f"Scan completed: {result.eval_outcome}\n")
        
        # 6. Print Results
        try:
            data_dict = result.model_dump()
        except AttributeError:
            data_dict = result.__dict__  # Fallback if model_dump doesn't exist
            
        pprint.pprint(data_dict, indent=4)

    except Exception as e:
        print(f"An error occurred during scanning: {e}")