import re

def extract_json_block(text: str) -> str:
    """Extracts the first JSON block from the text."""
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    return None