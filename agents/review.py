import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from google import genai
from google.genai import types
from prompts.prompt import default_prompt
from utils.utils import extract_json_block
from config.ai import client


def review_and_correct_content(content_type: str, content: dict, original_text: str = None):
    """
    Review and correct content for accuracy, completeness, and UPSC relevance.
    
    Args:
        content_type: Type of content - "sections", "cards", "mindmap", "pyq"
        content: The content dictionary to review
        original_text: Optional original text for reference
        
    Returns:
        Corrected content dictionary with review notes
    """
    
    if content_type == "sections":
        return review_sections(content, original_text)
    elif content_type == "cards":
        return review_cards(content, original_text)
    elif content_type == "mindmap":
        return review_mindmap(content, original_text)
    elif content_type == "pyq":
        return review_pyq(content, original_text)
    else:
        raise ValueError(f"Unknown content type: {content_type}")


def review_sections(sections: list, original_text: str = None):
    """
    Review and correct sections for accuracy and UPSC relevance.
    
    Args:
        sections: List of section dictionaries
        original_text: Original article text for reference
        
    Returns:
        Dict with corrected sections and review notes
    """
    prompt = f"""
You are an expert UPSC content reviewer. Review the following sections for accuracy, completeness, and UPSC relevance.

ORIGINAL TEXT (for reference):
{original_text[:2000] if original_text else "Not provided"}

SECTIONS TO REVIEW (JSON):
{json.dumps(sections, indent=2)}

YOUR TASK:
1. Check for factual accuracy (dates, names, numbers, events)
2. Verify UPSC relevance (filter out non-exam relevant content)
3. Ensure completeness (all sections have title, content, importance)
4. Validate content format (content should be array of strings)
5. Check for consistency and coherence
6. Correct any errors, inaccuracies, or missing information
7. Improve clarity and structure where needed

OUTPUT FORMAT (MANDATORY JSON):
{{
  "corrected_sections": [
    {{
      "title": "Corrected section title",
      "content": ["Point 1", "Point 2", ...],
      "importance": "absolutely_important"
    }}
  ],
  "review_notes": {{
    "issues_found": ["Issue 1", "Issue 2"],
    "corrections_made": ["Correction 1", "Correction 2"],
    "accuracy_score": 0.95,
    "completeness_score": 1.0
  }}
}}

RULES:
- Produce ONLY valid JSON - no markdown, no code fences, no explanations
- Maintain the same number of sections unless content is irrelevant
- Preserve section_index if present
- Ensure all facts are accurate and verifiable
- Remove any non-UPSC relevant content
- Improve clarity without changing meaning
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt.get("review", "")),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    
    if not json_payload:
        # Fallback: return original content with error note
        return {
            "corrected_sections": sections,
            "review_notes": {
                "issues_found": ["Failed to parse review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "completeness_score": 0.0
            }
        }
    
    try:
        result = json.loads(json_payload)
        return result
    except json.JSONDecodeError:
        return {
            "corrected_sections": sections,
            "review_notes": {
                "issues_found": ["Invalid JSON in review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "completeness_score": 0.0
            }
        }


def review_cards(cards: list, original_text: str = None):
    """
    Review and correct cards for accuracy and quality.
    
    Args:
        cards: List of card dictionaries
        original_text: Original article text for reference
        
    Returns:
        Dict with corrected cards and review notes
    """
    prompt = f"""
You are an expert UPSC content reviewer. Review the following recall cards for accuracy, completeness, and quality.

ORIGINAL TEXT (for reference):
{original_text[:2000] if original_text else "Not provided"}

CARDS TO REVIEW (JSON):
{json.dumps(cards, indent=2)}

YOUR TASK:
1. Verify factual accuracy (dates, names, numbers, events)
2. Check GS paper tags are appropriate
3. Ensure tags are relevant and accurate
4. Validate summary is 3-4 lines and covers key points
5. Verify CTA buttons format is correct
6. Check title clarity and accuracy
7. Ensure all required fields are present
8. Correct any errors or improve quality

OUTPUT FORMAT (MANDATORY JSON):
{{
  "corrected_cards": [
    {{
      "title": "Corrected title",
      "gs": "GS2 (IR), GS3 (Energy)",
      "tags": ["Tag1", "Tag2", "Tag3"],
      "summary": "3-4 line corrected summary...",
      "cta_buttons": "View Mind Map | View PYQs",
      "section_index": 0,
      "section_title": "..."
    }}
  ],
  "review_notes": {{
    "issues_found": ["Issue 1", "Issue 2"],
    "corrections_made": ["Correction 1", "Correction 2"],
    "accuracy_score": 0.95,
    "quality_score": 0.9
  }}
}}

RULES:
- Produce ONLY valid JSON - no markdown, no code fences, no explanations
- Maintain section_index and section_title if present
- Ensure all facts are accurate
- Keep summary exactly 3-4 lines
- Preserve CTA buttons format
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt.get("review", "")),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    
    if not json_payload:
        return {
            "corrected_cards": cards,
            "review_notes": {
                "issues_found": ["Failed to parse review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "quality_score": 0.0
            }
        }
    
    try:
        result = json.loads(json_payload)
        return result
    except json.JSONDecodeError:
        return {
            "corrected_cards": cards,
            "review_notes": {
                "issues_found": ["Invalid JSON in review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "quality_score": 0.0
            }
        }


def review_mindmap(mindmap: dict, original_text: str = None):
    """
    Review and correct mindmap for accuracy and structure.
    
    Args:
        mindmap: Mindmap dictionary
        original_text: Original article text for reference
        
    Returns:
        Dict with corrected mindmap and review notes
    """
    prompt = f"""
You are an expert UPSC content reviewer. Review the following mindmap for accuracy, completeness, and structure.

ORIGINAL TEXT (for reference):
{original_text[:2000] if original_text else "Not provided"}

MINDMAP TO REVIEW (JSON):
{json.dumps(mindmap, indent=2)}

YOUR TASK:
1. Verify factual accuracy of all nodes
2. Check hierarchical structure (max 3 levels)
3. Ensure all important concepts are included
4. Verify node names are clear and accurate
5. Check for logical organization
6. Correct any errors or improve structure

OUTPUT FORMAT (MANDATORY JSON):
{{
  "corrected_mindmap": {{
    "title": "Corrected main topic",
    "nodes": [
      {{
        "name": "Subtopic 1",
        "children": [
          {{ "name": "Point A" }},
          {{ "name": "Point B" }}
        ]
      }}
    ],
    "section_index": 0,
    "section_title": "..."
  }},
  "review_notes": {{
    "issues_found": ["Issue 1", "Issue 2"],
    "corrections_made": ["Correction 1", "Correction 2"],
    "accuracy_score": 0.95,
    "structure_score": 0.9
  }}
}}

RULES:
- Produce ONLY valid JSON - no markdown, no code fences, no explanations
- Maintain section_index and section_title if present
- Keep hierarchy to 3 levels maximum
- Ensure all facts are accurate
- Improve clarity without changing meaning
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt.get("review", "")),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    
    if not json_payload:
        return {
            "corrected_mindmap": mindmap,
            "review_notes": {
                "issues_found": ["Failed to parse review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "structure_score": 0.0
            }
        }
    
    try:
        result = json.loads(json_payload)
        return result
    except json.JSONDecodeError:
        return {
            "corrected_mindmap": mindmap,
            "review_notes": {
                "issues_found": ["Invalid JSON in review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "structure_score": 0.0
            }
        }


def review_pyq(pyq: dict, original_text: str = None):
    """
    Review and correct PYQ questions for accuracy and UPSC style.
    
    Args:
        pyq: PYQ dictionary with prelims and mains
        original_text: Original article text for reference
        
    Returns:
        Dict with corrected PYQ and review notes
    """
    prompt = f"""
You are an expert UPSC content reviewer. Review the following PYQ questions for accuracy, UPSC style compliance, and quality.

ORIGINAL TEXT (for reference):
{original_text[:2000] if original_text else "Not provided"}

PYQ TO REVIEW (JSON):
{json.dumps(pyq, indent=2)}

YOUR TASK:
1. Verify factual accuracy of all questions
2. Check UPSC question style and format
3. Validate correct answers for prelims
4. Ensure explanations are accurate and clear
5. Verify GS paper tags are appropriate
6. Check key points for mains questions are comprehensive
7. Ensure questions test understanding, not just recall
8. Correct any errors or improve quality

OUTPUT FORMAT (MANDATORY JSON):
{{
  "corrected_pyq": {{
    "prelims": [
      {{
        "question": "Corrected question text",
        "options": {{
          "a": "Option A",
          "b": "Option B",
          "c": "Option C",
          "d": "Option D"
        }},
        "correct_answer": "a",
        "explanation": "Corrected explanation",
        "gs_paper": "GS1",
        "year": "2024",
        "section_index": 0,
        "section_title": "..."
      }}
    ],
    "mains": [
      {{
        "question": "Corrected question text",
        "type": "10 marks",
        "gs_paper": "GS2",
        "year": "2024",
        "key_points": ["Point 1", "Point 2", ...],
        "section_index": 0,
        "section_title": "..."
      }}
    ]
  }},
  "review_notes": {{
    "issues_found": ["Issue 1", "Issue 2"],
    "corrections_made": ["Correction 1", "Correction 2"],
    "accuracy_score": 0.95,
    "quality_score": 0.9
  }}
}}

RULES:
- Produce ONLY valid JSON - no markdown, no code fences, no explanations
- Maintain section_index and section_title if present
- Ensure all facts are accurate
- Follow UPSC question style exactly
- Verify correct answers are actually correct
- Improve clarity without changing meaning
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=default_prompt.get("review", "")),
        contents=prompt,
    )

    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    
    if not json_payload:
        return {
            "corrected_pyq": pyq,
            "review_notes": {
                "issues_found": ["Failed to parse review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "quality_score": 0.0
            }
        }
    
    try:
        result = json.loads(json_payload)
        return result
    except json.JSONDecodeError:
        return {
            "corrected_pyq": pyq,
            "review_notes": {
                "issues_found": ["Invalid JSON in review response"],
                "corrections_made": [],
                "accuracy_score": 0.0,
                "quality_score": 0.0
            }
        }


def review_all_content(sections: list, cards: list, mindmaps: list, pyq: dict, original_text: str = None):
    """
    Review and correct all content types at once.
    
    Args:
        sections: List of sections
        cards: List of cards
        mindmaps: List of mindmaps
        pyq: PYQ dictionary
        original_text: Original article text
        
    Returns:
        Dict with all corrected content and review summary
    """
    results = {
        "sections": review_sections(sections, original_text),
        "cards": review_cards(cards, original_text),
        "mindmaps": [],
        "pyq": review_pyq(pyq, original_text),
        "overall_review": {
            "total_issues": 0,
            "total_corrections": 0,
            "average_accuracy": 0.0
        }
    }
    
    # Review each mindmap
    for mindmap in mindmaps:
        mindmap_result = review_mindmap(mindmap, original_text)
        results["mindmaps"].append(mindmap_result)
    
    # Calculate overall metrics
    all_notes = [
        results["sections"]["review_notes"],
        results["cards"]["review_notes"],
        results["pyq"]["review_notes"]
    ]
    
    for mindmap_result in results["mindmaps"]:
        all_notes.append(mindmap_result["review_notes"])
    
    results["overall_review"]["total_issues"] = sum(
        len(notes.get("issues_found", [])) for notes in all_notes
    )
    results["overall_review"]["total_corrections"] = sum(
        len(notes.get("corrections_made", [])) for notes in all_notes
    )
    
    accuracy_scores = [
        notes.get("accuracy_score", 0.0) for notes in all_notes
    ]
    if accuracy_scores:
        results["overall_review"]["average_accuracy"] = sum(accuracy_scores) / len(accuracy_scores)
    
    return results

