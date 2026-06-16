import json
import re


def repair_json(raw_text):

    # If already correct dict, return directly
    if isinstance(raw_text, dict):
        return raw_text

    text = str(raw_text)

    # -----------------------------
    # STEP 1: Remove markdown noise
    # -----------------------------
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # -----------------------------
    # STEP 2: Normalize bad LLM JSON patterns
    # -----------------------------
    text = text.replace("'", '"')              # single → double quotes
    text = re.sub(r",\s*}", "}", text)         # trailing comma fix
    text = re.sub(r",\s*]", "]", text)
    text = text.replace("None", "null")        # Python → JSON compatibility
    text = text.replace("True", "true")
    text = text.replace("False", "false")

    # -----------------------------
    # STEP 3: Extract best JSON block
    # -----------------------------
    matches = re.findall(r"\{.*?\}", text, re.DOTALL)

    if matches:
        text = matches[-1]   # safest assumption: last valid JSON block

    # -----------------------------
    # STEP 4: Try parsing
    # -----------------------------
    try:
        return json.loads(text)

    except Exception:

        # -----------------------------
        # FINAL SAFE FALLBACK
        # -----------------------------
        return {
            "product_id": "UNKNOWN",
            "standardized_category": "Unknown",
            "estimated_unit_price": 0.0,
            "confidence_score": 0.0,
            "repair_status": "failed_repair",
            "raw_input": text[:200]   # helps debugging (very important for audit)
        }