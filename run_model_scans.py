import subprocess
import sys
from detect_models import detect_models

def main():
    models = detect_models()

    if not models:
        print("ℹ️ No models detected – skipping scans")
        return

    failed = False

    for model in models:
        print(f"\n▶ Running scan for {model}")
        result = subprocess.run(
            ["python", "hf-scan.py", "--model", model, "--fail-on", "high"]
        )

        if result.returncode != 0:
            print(f"❌ Scan failed for {model}")
            failed = True

    if failed:
        print("\n❌ One or more model scans failed")
        sys.exit(1)

    print("\n✅ All model scans passed")

if __name__ == "__main__":
    main()