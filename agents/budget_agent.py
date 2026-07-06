from __future__ import annotations
import anthropic
import json
import streamlit as st
from typing import List
from utils.json_parser import parse_claude_json


async def run(
    origin_city: str,
    destinations: List[dict],
    days: int,
    booking_window: str
) -> dict:
    """
    Estimates travel costs for each destination.
    booking_window: '3_months', '4_8_weeks', 'last_minute'
    Returns a dict keyed by destination name.
    """
    client = anthropic.AsyncAnthropic(api_key=st.secrets["anthropic"]["api_key"])

    dest_list = [f"{d['name']}, {d['state_code']}" for d in destinations]
    dest_str = "\n".join(f"- {d}" for d in dest_list)

    booking_labels = {
        "3_months": "3+ months in advance",
        "4_8_weeks": "4-8 weeks in advance",
        "last_minute": "under 2 weeks (last minute)"
    }
    booking_label = booking_labels.get(booking_window, "3+ months in advance")

    prompt = f"""You are a US travel budget expert. Estimate realistic flight costs from {origin_city} 
to each destination, booking {booking_label}.

Destinations:
{dest_str}

Trip duration: {days} days

Return ONLY a JSON object keyed by city name. Each value must have:
{{
  "flight_low": 150,
  "flight_high": 220,
  "flight_note": "e.g. Via Charlotte on American",
  "daily_budget_low": 120,
  "daily_budget_high": 200,
  "total_est_low": 990,
  "total_est_high": 1620,
  "cost_tier": "$ or $$ or $$$",
  "booking_tip": "One practical tip for getting the best price"
}}

Prices in USD. Be realistic. Return only valid JSON, no extra text."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    return parse_claude_json(raw)