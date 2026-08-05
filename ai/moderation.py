import os
import google.generativeai as genai


# ==========================
# GEMINI SETUP
# ==========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=GEMINI_API_KEY
)


model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


# ==========================
# MESSAGE MODERATION
# ==========================

async def check_message(content: str):

    prompt = f"""
You are a Discord moderation AI.

Analyze this message:

"{content}"

Decide if the message contains:
- insults
- harassment
- hate speech
- threats
- toxic behavior
- excessive profanity

Return ONLY valid JSON.

Format:

{{
    "toxic": true or false,
    "score": number between 0 and 100,
    "reason": "short reason"
}}

If the message is safe:

{{
    "toxic": false,
    "score": 0,
    "reason": "safe"
}}
"""

    try:

        response = await model.generate_content_async(
            prompt
        )

        text = response.text.strip()


        # تنظيف لو رجع Markdown
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")

        import json

        data = json.loads(text)


        return {
            "toxic": data.get("toxic", False),
            "score": data.get("score", 0),
            "reason": data.get("reason", "Unknown")
        }


    except Exception as e:

        print(
            "Gemini Moderation Error:",
            e
        )

        # إذا صار خطأ لا يعاقب أحد
        return {
            "toxic": False,
            "score": 0,
            "reason": "AI Error"
        }
