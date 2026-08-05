import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    token=HF_TOKEN
)

MODEL = "unitary/toxic-bert"


async def check_message(text):

    try:
        result = client.text_classification(
            text,
            model=MODEL
        )

        prediction = result[0]

        label = prediction.label.lower()
        score = round(prediction.score * 100, 2)

        if label in ["toxic", "insult", "hate"]:
            return {
                "toxic": True,
                "reason": label,
                "score": score
            }

        else:
            return {
                "toxic": False,
                "reason": "Safe",
                "score": score
            }


    except Exception as e:
        print("AI Error:", e)

        return {
            "toxic": False,
            "reason": "AI Error",
            "score": 0
        }
