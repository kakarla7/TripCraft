from __future__ import annotations
import anthropic
import json
import streamlit as st
from typing import List
from utils.json_parser import parse_claude_json


async def run(destinations: List[dict], month: str) -> dict:
    """
    Gets weather info for each destination in the given month.
    Returns a dict keyed by destination name.
    """
    client = anthropic.AsyncAnthropic(api_key=st.secrets["anthropic"]["api_key"])

    dest_list = [f"{d['name']}, {d['state_code']}" for d in destinations]
    dest_str = "\n".join(f"- {d}" for d in dest_list)

    prompt = f"""You are a US weather expert. Provide typical weather for these destinations in {month}.

Destinations:
{dest_str}

Return ONLY a JSON object keyed by city name. Each value must have:
{{
  "avg_high_f": 72,
  "avg_low_f": 52,
  "conditions": "Crisp and sunny",
  "rain_days": 4,
  "summary": "One line weather summary e.g. Perfect hiking weather, cool evenings",
  "packing_hint": "Light layers, waterproof jacket"
}}

Return only valid JSON, no extra text."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    return parse_claude_json(raw)