import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    token=os.getenv("HF_TOKEN")
)

MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment"


async def check_message(text):
    try:
        result = client.text_classification(
            text,
            model=MODEL_NAME
        )

        prediction = max(
            result,
            key=lambda x: x["score"]
        )

        label = prediction["label"]
        score = prediction["score"]

        print("TEXT:", text)
        print("AI RESULT:", label, score)

        toxic_labels = [
            "toxic",
            "negative",
            "hate",
            "insult"
        ]

        is_toxic = label.lower() in toxic_labels and score > 0.80

        return {
            "toxic": is_toxic,
            "reason": label,
            "score": round(score * 100, 2)
        }

    except Exception as e:
        print("AI Error:", e)

        return {
            "toxic": False,
            "reason": "AI Error",
            "score": 0
        }
