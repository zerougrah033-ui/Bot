import asyncio
from huggingface_hub import InferenceClient

from config import HF_TOKEN


client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


async def check_message(message: str):

    try:
        result = await asyncio.to_thread(
            client.text_classification,
            message,
            model="unitary/toxic-bert"
        )

        if not result:
            return {
                "toxic": False,
                "score": 0
            }

        data = result[0]

        label = data["label"].lower()
        score = data["score"]

        # إذا النموذج اعتبرها toxic
        if label == "toxic" and score >= 0.85:
            return {
                "toxic": True,
                "score": score
            }

        return {
            "toxic": False,
            "score": score
        }


    except Exception as e:
        print("Hugging Face Error:", e)

        # إذا تعطل الـ AI لا يعطل البوت
        return {
            "toxic": False,
            "score": 0
        }
