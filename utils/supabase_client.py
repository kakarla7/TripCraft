from __future__ import annotations
import streamlit as st
from supabase import create_client, Client


# @st.cache_resource
def get_supabase() -> Client:
    """Cached Supabase client — one connection reused across sessions."""
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["anon_key"]
    return create_client(url, key)


def save_search(
    user_id: str,
    name: str,
    search_params: dict,
    results: list,
    share_slug: str
) -> dict | None:
    """Save a named search result to Supabase."""
    sb = get_supabase()
    data = {
        "user_id": user_id,
        "name": name,
        "search_params": search_params,
        "results": results,
        "share_slug": share_slug
    }
    response = sb.table("saved_searches").insert(data).execute()
    return response.data[0] if response.data else None


def get_search_by_slug(slug: str) -> dict | None:
    """Fetch a saved search by share slug."""
    sb = get_supabase()
    response = (
        sb.table("saved_searches")
        .select("*")
        .eq("share_slug", slug)
        .single()
        .execute()
    )
    return response.data


def get_user_searches(user_id: str) -> list:
    """Fetch all saved searches for a user, newest first."""
    sb = get_supabase()
    response = (
        sb.table("saved_searches")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def delete_search(search_id: str, user_id: str) -> bool:
    """Delete a saved search — only if owned by user."""
    sb = get_supabase()
    response = (
        sb.table("saved_searches")
        .delete()
        .eq("id", search_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(response.data)


def save_trip(
    user_id: str,
    destination: str,
    full_plan: dict,
    share_slug: str
) -> dict | None:
    """Save a full Phase 2 trip plan."""
    sb = get_supabase()
    data = {
        "user_id": user_id,
        "destination": destination,
        "full_plan": full_plan,
        "share_slug": share_slug
    }
    response = sb.table("saved_trips").insert(data).execute()
    return response.data[0] if response.data else None


def get_trip_by_slug(slug: str) -> dict | None:
    """Fetch a trip plan by share slug."""
    sb = get_supabase()
    response = (
        sb.table("saved_trips")
        .select("*")
        .eq("share_slug", slug)
        .single()
        .execute()
    )
    return response.data


def get_user_trips(user_id: str) -> list:
    """Fetch all saved trips for a user."""
    sb = get_supabase()
    response = (
        sb.table("saved_trips")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []