import asyncio
import json

from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


async def check_message(message: str):

    prompt = f"""
You are a Discord moderation AI.

Analyze the message.

Reply ONLY with valid JSON.

Example:

{{
  "toxic": true,
  "score": 95,
  "reason": "Harassment"
}}

Rules:

- Detect Arabic and English.
- toxic must be true or false.
- score must be from 0 to 100.
- reason must be one of:
  Harassment
  Hate Speech
  Threat
  Bullying
  Racism
  Offensive Language
  Safe

Message:

{message}
"""

    try:

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        elif text.startswith("```"):
            text = text.replace("```", "").strip()

        data = json.loads(text)

        if "toxic" not in data:
            data["toxic"] = False

        if "score" not in data:
            data["score"] = 0

        if "reason" not in data:
            data["reason"] = "Safe"

        return data

    except Exception as e:

        print("Gemini Error:", e)

        return {
            "toxic": False,
            "score": 0,
            "reason": "Error"
        }
