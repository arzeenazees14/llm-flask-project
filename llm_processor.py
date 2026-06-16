import os
import json
import time
from google import genai

# ---------------- CONFIG ----------------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=API_KEY)


# ---------------- MODELS (FALLBACK LIST) ----------------
MODELS = [
    "models/gemini-2.0-flash",
    "models/gemini-2.5-flash",
    "models/gemini-3.5-flash"
]


# ---------------- MAIN FUNCTION ----------------
def generate_product_json(description: str):

    prompt = f"""
You are a strict JSON generator for procurement.

Return ONLY valid JSON:

{{
  "product_id": "string",
  "standardized_category": "string",
  "estimated_unit_price": number,
  "confidence_score": number
}}

Product: {description}
"""

    for model_name in MODELS:
        for i in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                text = response.text.strip()

                start = text.find("{")
                end = text.rfind("}") + 1

                return text[start:end]

            except Exception as e:
                print(f"LLM error with {model_name}:", e)

                if "429" in str(e):
                    time.sleep(5 * (i + 1))
                else:
                    break

    return json.dumps({
        "product_id": "ERROR",
        "standardized_category": "Unknown",
        "estimated_unit_price": 0,
        "confidence_score": 0,
        "error": "LLM_FAILED"
    })