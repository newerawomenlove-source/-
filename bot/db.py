from typing import Any

from supabase import AsyncClient, acreate_client

from bot.config import SUPABASE_KEY, SUPABASE_URL

_client: AsyncClient | None = None


async def init_client() -> None:
    global _client
    _client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)


def _require_client() -> AsyncClient:
    if _client is None:
        raise RuntimeError("Supabase client is not initialized, call init_client() first")
    return _client


async def upsert_user(tg_user_id: int, username: str | None, first_name: str | None, status: str) -> None:
    client = _require_client()
    await client.table("users").upsert(
        {
            "tg_user_id": tg_user_id,
            "username": username,
            "first_name": first_name,
            "status": status,
        },
        on_conflict="tg_user_id",
    ).execute()


async def update_user_status(tg_user_id: int, status: str) -> None:
    client = _require_client()
    await client.table("users").update({"status": status}).eq("tg_user_id", tg_user_id).execute()


async def save_survey_answer(tg_user_id: int, selected_options: list[str], custom_text: str | None) -> None:
    client = _require_client()
    await client.table("funnel_answers").insert(
        {
            "tg_user_id": tg_user_id,
            "selected_options": selected_options,
            "custom_text": custom_text,
        }
    ).execute()


async def count_occupied_spots() -> int:
    client = _require_client()
    result = (
        await client.table("users")
        .select("tg_user_id", count="exact")
        .in_("status", ["joined", "paid"])
        .execute()
    )
    return result.count or 0


async def log_event(tg_user_id: int, event_type: str, payload: dict[str, Any] | None = None) -> None:
    client = _require_client()
    await client.table("events").insert(
        {
            "tg_user_id": tg_user_id,
            "event_type": event_type,
            "payload": payload,
        }
    ).execute()
