from __future__ import annotations
import anthropic
import json
import streamlit as st
from typing import List
from utils.json_parser import parse_claude_json


async def run(
    destinations: List[dict],
    weather: dict,
    budget: dict,
    interests: List[str],
    traveller_types: List[str]
) -> List[dict]:
    """
    Merges destination + weather + budget data.
    Scores and ranks final destination cards.
    Returns top 3-5 enriched cards ready for display.
    """
    client = anthropic.AsyncAnthropic(api_key=st.secrets["anthropic"]["api_key"])

    merged = []
    for dest in destinations:
        name = dest["name"]
        merged.append({
            "destination": dest,
            "weather": weather.get(name, {}),
            "budget": budget.get(name, {})
        })

    interests_str = ", ".join(interests)
    traveller_str = ", ".join(traveller_types)

    prompt = f"""You are a travel recommendation engine. Score and rank these 5 destinations for:
- Interests: {interests_str}
- Travelling with: {traveller_str}

Data:
{json.dumps(merged, indent=2)}

Return ONLY a JSON array of the top 3-5 destinations, each object must have:
{{
  "name": "City",
  "state": "State",
  "state_code": "XX",
  "why": "Why this matches their specific interests",
  "top_3": ["activity 1", "activity 2", "activity 3"],
  "matched_interests": ["interest1", "interest2"],
  "match_score": 5,
  "match_label": "5/5 interests matched",
  "is_best_match": true,
  "drive_hours": 12.5,
  "flight_hours": 2.5,
  "nearest_airport": "BNA",
  "weather_summary": "60F, crisp and sunny",
  "weather_packing": "Light layers, waterproof jacket",
  "flight_low": 150,
  "flight_high": 220,
  "daily_low": 120,
  "daily_high": 200,
  "total_low": 990,
  "total_high": 1620,
  "cost_tier": "$$",
  "booking_tip": "Book now - prices rise 8 weeks out"
}}

Only set is_best_match: true for the single top destination.
Return only valid JSON, no extra text."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    return parse_claude_json(raw)