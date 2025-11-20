import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import re
from google import genai
from google.genai import types
from prompts.prompt import default_prompt
from utils.utils import extract_json_block

from config.ai import client



def create_cards(content: str):
    prompt = f"""
Generate high-quality recall cards from the following daily current-affairs content.

CONTENT:
{content}

OUTPUT FORMAT (JSON ARRAY):
[
  {{
    "title": "India–Nepal Power Trade Agreement",
    "gs": "GS2 (IR), GS3 (Energy)",
    "tags": ["Hydropower", "Bilateral Relations", "Connectivity"],
    "summary": "3-4 line summary covering key points, facts, and significance.",
    "cta_buttons": "View Mind Map | View PYQs"
  }},
  {{
    "title": "Another Topic Title",
    "gs": "GS2, GS3",
    "tags": ["Tag1", "Tag2", "Tag3"],
    "summary": "Another 3-4 line summary...",
    "cta_buttons": "View Mind Map | View PYQs"
  }}
]

RULES:
- Produce ONLY valid JSON array - no markdown, no code fences, no explanations.
- Create separate cards for each distinct topic/concept in the content.
- Title should be clear and descriptive (max 100 characters).
- GS field should list relevant GS papers (e.g., "GS2 (IR), GS3 (Energy)" or "GS2, GS3").
- Tags should be an array of 3-5 relevant keywords.
- Summary must be exactly 3-4 lines covering key points, facts, dates, numbers, and significance.
- CTA buttons should always be exactly: "View Mind Map | View PYQs"
- Cover all major topics, concepts, agreements, policies, and important facts from the content.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt["recall_card"]),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    return json.loads(json_payload)
