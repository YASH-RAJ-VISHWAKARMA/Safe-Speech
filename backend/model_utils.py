import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Global models
clf_model = None
rewrite_model = None


# -----------------------------------------------
# INIT MODELS
# -----------------------------------------------
def init_models():
    global clf_model, rewrite_model

    # Load .env file
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing in .env file!")

    # Configure Gemini API
    genai.configure(api_key=api_key)

    # Load Gemini 2.5 Flash
    clf_model = genai.GenerativeModel("gemini-2.5-flash")
    rewrite_model = genai.GenerativeModel("gemini-2.5-flash")

    print("✅ Models Loaded Successfully (Gemini 2.5 Flash)")


# -----------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------
def evaluate_text_pipeline(text: str):
    try:
        # ------------------------------
        # 1. CLASSIFICATION PROMPT
        # ------------------------------
        clf_prompt = f"""
You are a socio-cultural sensitivity classifier.

Analyze the following text and classify it for:
- hate speech
- racism
- sexism
- abusive content
- discrimination
- violence
- or safe content

TEXT:
\"{text}\"

Return STRICT JSON ONLY:
{{
 "score": number between 0-100,
 "category": "hate" | "racism" | "sexism" | "abusive" | "violence" | "safe" | "other",
 "explanation": "short explanation"
}}
"""

        clf_response = clf_model.generate_content(clf_prompt)

        # Extract clean JSON
        clf_json = extract_json(clf_response.text)

        # ------------------------------
        # 2. REWRITE PROMPT
        # ------------------------------
        rewrite_prompt = f"""
Rewrite the following text into 3 culturally safe, neutral, respectful versions:

TEXT:
\"{text}\"

Return STRICT JSON ONLY:
{{
  "rewrites": ["rewrite1", "rewrite2", "rewrite3"]
}}
"""

        rewrite_response = rewrite_model.generate_content(rewrite_prompt)

        rewrite_json = extract_json(rewrite_response.text)

        # ------------------------------
        # FINAL OUTPUT STRUCTURE
        # ------------------------------
        return {
            "risk": clf_json.get("score", 0),
            "highlights": [{
                "category": clf_json.get("category", "unknown"),
                "score": clf_json.get("score", 0)
            }],
            "explanation": clf_json.get("explanation", ""),
            "rewrites": rewrite_json.get("rewrites", []),
            "rule_hits": []
        }

    except Exception as e:
        return {
            "risk": 0,
            "highlights": [{"category": "error", "score": 0}],
            "explanation": f"Error evaluating text: {e}",
            "rewrites": [],
            "rule_hits": []
        }


# -----------------------------------------------
# JSON EXTRACTOR — FIXES BAD GEMINI OUTPUT
# -----------------------------------------------
def extract_json(text: str):
    """
    Gemini sometimes adds extra text. This function safely extracts JSON.
    """
    try:
        # If the response is clean JSON
        return json.loads(text)
    except:
        pass

    # Try to find JSON between { ... }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except:
        return {}
