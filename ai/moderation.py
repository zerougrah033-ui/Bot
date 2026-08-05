import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    token=HF_TOKEN
)

MODEL = "aubmindlab/bert-base-arabertv02"

async def check_message(text):
    try:
        result = client.text_classification(
            text,
            model=MODEL
        )

        return result[0].label

    except Exception as e:
        print("AI Error:", e)
        return "safe"
