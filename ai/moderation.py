import os
import traceback
from huggingface_hub import InferenceClient

client = InferenceClient(
    token=os.getenv("HF_TOKEN")
)

MODEL_NAME = "hossam87/bert-base-arabic-hate-speech"


async def check_message(text):
    try:
        result = client.text_classification(
            text,
            model=MODEL_NAME
        )

        if not result:
            return {
                "toxic": False,
                "level": "safe",
                "reason": "No Result",
                "score": 0
            }

        prediction = max(
            result,
            key=lambda x: x["score"]
        )

        label = prediction["label"].lower()
        score = float(prediction["score"])

        print("TEXT:", text)
        print("AI RESULT:", label, score)

        if score < 0.75:
            level = "safe"
            toxic = False

        elif score < 0.90:
            level = "delete"
            toxic = True

        else:
            level = "warn"
            toxic = True

        return {
            "toxic": toxic,
            "level": level,
            "reason": label,
            "score": round(score * 100, 2)
        }

    except Exception as e:
        print("========== AI ERROR ==========")
        print(repr(e))
        traceback.print_exc()
        print("==============================")

        return {
            "toxic": False,
            "level": "safe",
            "reason": "AI Error",
            "score": 0
        }
