import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

def analyze_document(raw_text: str, entities: dict) -> dict:
    prompt = f"""You are analyzing a business document (invoice/contract/PO).

Raw extracted text:
{raw_text}

Extracted entities: {json.dumps(entities)}

Respond ONLY with valid JSON (no markdown, no explanation) in this exact format:
{{
  "document_type": "invoice" | "contract" | "purchase_order" | "unknown",
  "summary": "2-3 sentence plain language summary",
  "anomalies": ["list of any red flags, or empty list if none"],
  "confidence": "high" | "medium" | "low"
}}
"""

    response = model.generate_content(prompt)
    result_text = response.text.strip()
    result_text = result_text.replace("```json", "").replace("```", "").strip()

    return json.loads(result_text)