import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import re
from google import genai
from google.genai import types
from prompts.prompt import default_prompt
from config.ai import client
from utils.utils import extract_json_block

def create_mindmap(content: str):
    prompt = f"""
Generate a hierarchical mind map from the following content.

CONTENT:
{content}

OUTPUT FORMAT (MANDATORY JSON):
{{
  "title": "Main topic",
  "nodes": [
    {{
      "name": "Subtopic 1",
      "children": [
        {{ "name": "Point A" }},
        {{ "name": "Point B" }}
      ]
    }},
    {{
      "name": "Subtopic 2",
      "children": [...]
    }}
  ]
}}

RULES:
- Do NOT add extra text outside JSON.
- Keep the hierarchy clean and 3 levels deep maximum.
- Summarize but do NOT omit important concepts.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt["mind_map"]),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    return json.loads(json_payload)
