from __future__ import annotations

# Supabase stub — replace with real implementation once supabase package is confirmed working
# All functions return None or empty list safely so the app runs without a DB connection

def get_supabase():
    return None

def save_search(user_id: str, search_params: dict, results: list, share_slug: str):
    return None

def get_search_by_slug(slug: str):
    return None

def get_user_searches(user_id: str) -> list:
    return []

def save_trip(user_id: str, destination: str, full_plan: dict, share_slug: str):
    return None

def get_trip_by_slug(slug: str):
    return None

def get_user_trips(user_id: str) -> list:
    return []