"""
utils/gemini_client.py
------------------------
This file handles everything related to talking to Google's Gemini API.

Why a separate file? Keeping API logic out of app.py means:
- app.py only worries about the UI
- this file only worries about "given product details, return a PRD"
- it's easier to test/debug/replace later

We use the NEW "google-genai" SDK (NOT the old, deprecated "google-generativeai").
Docs: https://ai.google.dev/gemini-api/docs/sdks
"""

import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load variables from the .env file (like GEMINI_API_KEY) into the environment.
load_dotenv()

# The exact model name we want to use, as required by the project spec.
MODEL_NAME = "gemini-2.5-flash"

# Low temperature = more consistent, predictable, less "creative" output.
# A PRD should be structured and repeatable, not flowery, so we keep this low.
TEMPERATURE = 0.1


class PRDGenerationError(Exception):
    """
    Custom exception so app.py can catch *this specific* error type
    and show a friendly message, instead of a raw Python traceback.
    """
    pass


def _get_client() -> genai.Client:
    """
    Creates and returns a Gemini API client using the key stored in .env.
    Raises a clear error if the key is missing, instead of a confusing
    error from deep inside the SDK.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise PRDGenerationError(
            "GEMINI_API_KEY is missing. Add it to your .env file "
            "(see .env.example for the format)."
        )
    return genai.Client(api_key=api_key)


def _build_prompt(product_data: dict) -> str:
    """
    Builds the instruction text we send to Gemini.

    We ask Gemini to act like a senior Product Manager and to return
    ONLY raw JSON (no markdown, no extra commentary) that matches an
    exact schema. This makes the response predictable and easy to parse.
    """
    return f"""
You are a senior Product Manager at a top tech company with 10+ years of
experience writing Product Requirements Documents (PRDs).

Using the product details below, write a complete, professional PRD.

PRODUCT DETAILS:
- Product Name: {product_data['product_name']}
- Category: {product_data['category']}
- Problem Statement (from founder): {product_data['problem_statement']}
- Target Users: {product_data['target_users']}
- Core Features (from founder): {product_data['core_features']}
- Out of Scope (from founder): {product_data['out_of_scope']}
- Success Metrics (from founder): {product_data['success_metrics']}

INSTRUCTIONS:
1. Expand and professionalize the founder's raw notes above into proper PRD language.
2. Return ONLY valid JSON. No markdown code fences, no explanations, no extra text.
3. The JSON MUST follow this EXACT schema and key names:

{{
  "executive_summary": "string, 3-5 sentences summarizing the product and its purpose",
  "problem_statement": "string, a clear, expanded version of the problem statement",
  "goals": ["string", "string", "string"],
  "personas": [
    {{
      "name": "string, a realistic persona name",
      "role": "string, their job title or role",
      "description": "string, 1-2 sentences about who they are",
      "needs": "string, what they need from this product",
      "pain_points": "string, their current frustrations"
    }},
    {{ "...": "a second persona with the same fields" }}
  ],
  "user_stories": [
    {{ "as_a": "string", "i_want": "string", "so_that": "string" }}
  ],
  "features": [
    {{ "name": "string", "description": "string", "priority": "High" }}
  ],
  "out_of_scope": ["string", "string"],
  "success_metrics": ["string", "string"],
  "timeline_estimate": "string, e.g. '8-10 weeks across 3 phases', with a brief phase breakdown",
  "risks": [
    {{ "risk": "string", "mitigation": "string" }}
  ]
}}

RULES:
- "goals" must contain EXACTLY 3 measurable goals.
- "personas" must contain EXACTLY 2 personas.
- "user_stories" must contain EXACTLY 5 stories in "As a / I want / So that" format.
- "features" must each have a "priority" of exactly "High", "Medium", or "Low".
- "risks" must contain 3-5 realistic risks with mitigations.
- Keep language clear and professional. Do not include placeholder text like "TBD".
- Output raw JSON only. Do not wrap it in ```json or any other formatting.
""".strip()


def _extract_json(raw_text: str) -> dict:
    """
    Gemini is instructed to return raw JSON, but models sometimes still wrap
    their answer in ```json ... ``` fences. This function strips any such
    fences and safely parses the JSON so the rest of the app never has to
    worry about it.
    """
    cleaned = raw_text.strip()

    # Remove ```json ... ``` or ``` ... ``` wrappers if present.
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise PRDGenerationError(
            "Gemini returned a response that wasn't valid JSON. "
            "Please try generating again."
        ) from exc


def generate_prd(product_data: dict) -> dict:
    """
    The main function the rest of the app calls.

    Input:  product_data (dict) - the raw form values from the Streamlit form.
    Output: dict - a parsed PRD matching the schema described in _build_prompt().

    Raises: PRDGenerationError on any failure (missing key, network issue,
            bad JSON, etc.) so app.py can show one clean error message.
    """
    try:
        client = _get_client()
        prompt = _build_prompt(product_data)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=TEMPERATURE,
                response_mime_type="application/json",
            ),
        )

        if not response.text:
            raise PRDGenerationError("Gemini returned an empty response. Please try again.")

        return _extract_json(response.text)

    except PRDGenerationError:
        # Re-raise our own clean errors as-is.
        raise
    except Exception as exc:
        # Catch anything else (network errors, SDK errors, etc.) and wrap it
        # in our custom error so app.py only ever needs to catch one type.
        raise PRDGenerationError(f"Failed to generate PRD: {exc}") from exc
