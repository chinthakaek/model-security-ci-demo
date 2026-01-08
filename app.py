from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "MustEr/gpt2-elite"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained("facebook/opt-125m")