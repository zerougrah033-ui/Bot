import asyncio
from huggingface_hub import InferenceClient
from config import HF_TOKEN

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


async def check_message(message: str):
    prompt = f"""
You are a moderation AI.

Determine whether the following message is safe or unsafe.

Rules:
- Reply with ONLY one word.
- Reply "safe" if the message is acceptable.
- Reply "unsafe" if it contains insults, harassment, hate speech, threats, bullying, discrimination, or toxic behavior.

Message:
{message}
"""

    try:
        result = await asyncio.to_thread(
            client.text_generation,
            prompt,
            model="meta-llama/Llama-Guard-3-8B",
            max_new_tokens=5,
            temperature=0
        )

        result = result.strip().lower()

        if "unsafe" in result:
            return False

        return True

    except Exception as e:
        print(f"Hugging Face Error: {e}")
        return True
