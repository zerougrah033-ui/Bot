from huggingface_hub import InferenceClient

client = InferenceClient(
    token=os.getenv("HF_TOKEN")
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
        score = prediction.score

        print("TEXT:", text)
        print("AI RESULT:", label, score)

        if label == "toxic" and score >= 0.80:
            return {
                "toxic": True,
                "reason": "Toxic Message",
                "score": round(score * 100, 2)
            }

        return {
            "toxic": False,
            "reason": "Safe",
            "score": round(score * 100, 2)
        }

    except Exception as e:
        print("AI Error:", e)

        return {
            "toxic": False,
            "reason": "AI Error",
            "score": 0
        }
