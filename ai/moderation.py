import asyncio
import json

from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


async def check_message(message: str):

    prompt = f"""
You are an AI moderation system.

Analyze the following Discord message.

Return ONLY valid JSON.

Example:

{{
    "toxic": true,
    "score": 95
}}

Rules:

- toxic = true if the message contains:
  - insults
  - harassment
  - bullying
  - hate speech
  - racism
  - threats
  - discrimination
  - offensive language

- toxic = false otherwise.

- score must be from 0 to 100.

The AI must understand Arabic and English.

Message:

{message}
"""

    try:

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        data = json.loads(text)

        return data

    except Exception as e:

        print("Gemini Error:", e)

        return {
            "toxic": False,
            "score": 0
        }
