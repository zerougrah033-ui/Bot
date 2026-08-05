import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    token=os.getenv("HF_TOKEN")
)

MODEL_NAME = "akhooli/xlm-r-large-arabic-toxic"


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

        label = prediction["label"].lower()
        score = prediction["score"]

        print("TEXT:", text)
        print("AI RESULT:", label, score)

        toxic = False
        level = "safe"

        # أقل من 75% تجاهل
        if score < 0.75:
            toxic = False
            level = "safe"

        # من 75 إلى 90 حذف فقط
        elif score < 0.90:
            toxic = True
            level = "delete"

        # 90 وفوق حذف + تحذير
        elif score >= 0.90:
            toxic = True
            level = "warn"

        return {
            "toxic": toxic,
            "level": level,
            "reason": label,
            "score": round(score * 100, 2)
        }


    except Exception as e:
        print("AI Error:", e)

        return {
            "toxic": False,
            "level": "safe",
            "reason": "AI Error",
            "score": 0
        }
