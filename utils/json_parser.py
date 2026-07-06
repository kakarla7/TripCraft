from __future__ import annotations
import json
import re


def parse_claude_json(raw: str) -> any:
    """
    Robustly parse JSON from a Claude response.
    Handles markdown code fences, leading/trailing text,
    and truncated responses gracefully.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    if "```" in text:
        # Extract content between first ``` and last ```
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("[") or part.startswith("{"):
                text = part
                break

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON array or object in the text
    # Look for the first [ or { and try from there
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start = text.find(start_char)
        if start == -1:
            continue
        # Try progressively shorter substrings if full parse fails
        substring = text[start:]
        try:
            return json.loads(substring)
        except json.JSONDecodeError:
            # Try to find the last complete item if truncated
            last_end = substring.rfind(end_char)
            if last_end > 0:
                try:
                    return json.loads(substring[:last_end + 1])
                except json.JSONDecodeError:
                    pass

    # Last resort — raise with helpful message
    raise ValueError(
        f"Could not parse JSON from Claude response. "
        f"First 200 chars: {raw[:200]}"
    )