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

        prediction = max(result, key=lambda x: x["score"])

        label = prediction["label"].lower()
        score = prediction["score"]

        print("TEXT:", text)
        print("AI RESULT:", label, score)

        # أقل من 75% = تجاهل
        if score < 0.75:
            return {
                "toxic": False,
                "reason": label,
                "score": round(score * 100, 2)
            }

        # 75% وفوق = اعتبرها مسيئة
        return {
            "toxic": label == "negative",
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
