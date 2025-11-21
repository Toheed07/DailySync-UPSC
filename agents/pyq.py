from config.ai import client
from utils.utils import extract_json_block
from prompts.prompt import default_prompt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from google.genai import types


def create_pyq(content: str):
    prompt = f"""
Generate UPSC-style Previous Year Questions (PYQ) based on the following current affairs content.

CONTENT:
{content}

OUTPUT FORMAT (MANDATORY JSON):
{{
  "prelims": [
    {{
      "question": "Question text in UPSC Prelims MCQ style",
      "options": {{
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D"
      }},
      "correct_answer": "a",
      "explanation": "Brief explanation of why this answer is correct",
      "gs_paper": "GS1",
      "year": "2024"
    }}
  ],
  "mains": [
    {{
      "question": "Question text in UPSC Mains descriptive style",
      "type": "10 marks / 15 marks / 20 marks",
      "gs_paper": "GS2",
      "year": "2024",
      "key_points": [
        "Key point 1 for answer",
        "Key point 2 for answer",
        "Key point 3 for answer"
      ]
    }}
  ]
}}

RULES:
- Produce ONLY valid JSON - no markdown, no code fences, no explanations
- Generate 2-4 Prelims questions (MCQ format with 4 options)
- Generate 1-3 Mains questions (descriptive/essay style)
- Questions should test understanding, application, and analysis
- Follow actual UPSC question style and difficulty
- Include relevant GS paper tags (GS1, GS2, GS3, GS4)
- Provide clear explanations for Prelims questions
- Include key points/answer framework for Mains questions
- Questions should be based on the content provided
- Use realistic year values (2020-2025)

Example:
Prelims:
Q. Which of the following are the reasons for the occurrence of multi-drug resistance in microbial pathogens in India? (2019)

Genetic predisposition of some people
Taking incorrect doses of antibiotics to cure diseases
Using antibiotics in livestock farming
Multiple chronic diseases in some people
Select the correct answer using the code given below.

(a) 1 and 2

(b) 2 and 3 only

(c) 1, 3 and 4

(d) 2, 3 and 4

Mains:
Q. Can overuse and free availability of antibiotics without Doctor’s prescription, be contributors to the emergence of drug-resistant diseasesin India? What are the available mechanisms for monitoring and control? Critically discuss the various issues involved. (2014)
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt["pyq"]),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    return json.loads(json_payload)
