import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from google import genai
from google.genai import types
from prompts.prompt import default_prompt
from utils.utils import extract_json_block
from config.ai import client


def extract_sections(article_text: str):
    """
    Analyzes raw current-affairs content and extracts only UPSC-relevant sections.
    
    Filters and prioritizes sections based on UPSC importance:
    - Returns 4-8 sections (prioritizing absolutely important ones)
    - Filters out non-UPSC relevant content (local news, minor updates, etc.)
    - Cleans content (removes ads, author bios, unrelated text)
    
    Returns:
        List of dicts with keys: title, content, importance
        - content: Array of strings, each string is a bullet point
        Importance levels: "absolutely_important", "important", "moderately_important"
    """

    prompt = f"""
Analyze the following current affairs article and extract ONLY the sections that are IMPORTANT for UPSC preparation.

INPUT ARTICLE:
{article_text}

YOUR TASK:
1. CRITICALLY ANALYZE each section for UPSC relevance
2. FILTER OUT sections that are NOT important for UPSC:
   - Local/regional news without national significance
   - Minor updates without policy implications
   - Non-exam relevant content (ads, author bios, navigation text)
   - Repetitive or redundant information
3. PRIORITIZE sections by importance:
   - ABSOLUTELY IMPORTANT: Government policies, major agreements, constitutional matters, international relations, economic reforms, environmental policies, social issues
   - IMPORTANT: Significant developments, new schemes, important reports, key judgments
4. SELECT ONLY 4-8 sections (prioritize absolutely important ones)
5. FORMAT content as an array of bullet points:
   - Break down each section into clear, concise bullet points
   - Each bullet should cover a distinct aspect (what, why, how, when, where, who)
   - Include key facts, figures, dates, names, and important details
   - Content must be an ARRAY of strings, not a single string with newlines
6. CLEAN content: remove ads, formatting issues, unrelated text

OUTPUT FORMAT (JSON ARRAY):
[
  {{
    "title": "India-Nepal Power Trade Agreement",
    "content": [
      "Point 1 explaining key aspect",
      "Point 2 with important details",
      "Point 3 covering another aspect",
      "Point 4 with facts/figures"
    ],
    "importance": "absolutely_important"
  }},
  {{
    "title": "MSP Reform Proposal",
    "content": [
      "Point 1",
      "Point 2",
      "Point 3"
    ],
    "importance": "important"
  }}
]

CRITICAL RULES:
- Produce ONLY valid JSON array - no markdown, no code fences, no explanations
- Return EXACTLY 4-8 sections (prioritize absolutely important ones)
- Each section MUST have: title, content (as ARRAY of strings), and importance level
- Content MUST be an ARRAY of strings, where each string is a bullet point
- DO NOT use newline characters (\n) or special bullet characters (•, \u2022)
- Each array element should be a clear, concise bullet point covering a distinct aspect
- Include key facts, figures, dates, names, and important details in bullet points
- Importance levels: "absolutely_important", "important", or "moderately_important"
- Filter out non-UPSC relevant content aggressively
- Clean content thoroughly (remove ads, author info, navigation, etc.)
- If article has fewer than 4 relevant sections, return only those
- If article has more than 8 relevant sections, return only the top 8 most important
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt["analyse"]),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)

    try:
        return json.loads(json_payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc
