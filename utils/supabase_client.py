from __future__ import annotations
import streamlit as st
from supabase import create_client, Client


def get_supabase() -> Client:
    """
    Returns Supabase client — stored in session state to avoid
    cache issues with st.cache_resource after secrets updates.
    """
    if "supabase_client" not in st.session_state:
        url: str = st.secrets["supabase"]["url"]
        key: str = st.secrets["supabase"]["anon_key"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]


def save_search(
    user_id: str,
    name: str,
    search_params: dict,
    results: list,
    share_slug: str
) -> dict | None:
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
    sb = get_supabase()
    response = (
        sb.table("saved_trips")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []