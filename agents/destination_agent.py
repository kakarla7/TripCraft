from __future__ import annotations
import anthropic
import json
import streamlit as st
from typing import List
from utils.json_parser import parse_claude_json


async def run(
    origin_city: str,
    month: str,
    days: int,
    interests: List[str],
    traveller_types: List[str]
) -> List[dict]:
    """
    Finds the 5 best US destinations matching the user's inputs.
    Returns a list of destination dicts.
    """
    client = anthropic.AsyncAnthropic(api_key=st.secrets["anthropic"]["api_key"])

    interests_str = ", ".join(interests) if interests else "general travel"
    traveller_str = ", ".join(traveller_types) if traveller_types else "adults"

    prompt = f"""You are a US travel expert. Find the 5 best US destinations for this traveller.

Trip details:
- Origin: {origin_city}
- Month: {month}
- Duration: {days} days
- Interests: {interests_str}
- Travelling with: {traveller_str}

Return ONLY a JSON array with exactly 5 destinations. Each object must have these exact keys:
{{
  "name": "City name",
  "state": "State name",
  "state_code": "XX",
  "why": "2 sentence explanation of why it matches their interests",
  "top_3": ["thing 1", "thing 2", "thing 3"],
  "matched_interests": ["interest1", "interest2"],
  "drive_hours": 12.5,
  "flight_hours": 2.5,
  "nearest_airport": "Airport code e.g. BNA",
  "cost_tier": "$ or $$ or $$$"
}}

Rank by best match to their interests. Return only valid JSON, no extra text."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    return parse_claude_json(raw)