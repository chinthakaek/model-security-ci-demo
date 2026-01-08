import os
import re
import sys

MODEL_PATTERNS = [
    r'from_pretrained\(\s*["\']([^"\']+)["\']\s*\)',
]

def detect_models(root_dir="."):
    models = set()

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for pattern in MODEL_PATTERNS:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                models.add(match)
                except Exception:
                    continue

    return sorted(models)

if __name__ == "__main__":
    models = detect_models()

    if not models:
        print("ℹ️ No Hugging Face models detected")
        sys.exit(0)

    print("🔍 Detected Hugging Face models:")
    for model in models:
        print(model)