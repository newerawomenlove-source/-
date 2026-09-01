import json
from typing import Any

import asyncpg

from bot.config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def init_client() -> None:
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, init=_init_connection)


def _require_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized, call init_client() first")
    return _pool


async def upsert_user(tg_user_id: int, username: str | None, first_name: str | None, status: str) -> None:
    pool = _require_pool()
    await pool.execute(
        """
        insert into users (tg_user_id, username, first_name, status)
        values ($1, $2, $3, $4)
        on conflict (tg_user_id) do update
        set username = excluded.username,
            first_name = excluded.first_name,
            status = excluded.status,
            updated_at = now()
        """,
        tg_user_id,
        username,
        first_name,
        status,
    )


async def update_user_status(tg_user_id: int, status: str) -> None:
    pool = _require_pool()
    await pool.execute(
        "update users set status = $1, updated_at = now() where tg_user_id = $2",
        status,
        tg_user_id,
    )


async def save_phone_number(tg_user_id: int, phone_number: str) -> None:
    pool = _require_pool()
    await pool.execute(
        "update users set phone_number = $1, updated_at = now() where tg_user_id = $2",
        phone_number,
        tg_user_id,
    )


async def save_survey_answer(tg_user_id: int, selected_options: list[str], custom_text: str | None) -> None:
    pool = _require_pool()
    await pool.execute(
        """
        insert into funnel_answers (tg_user_id, selected_options, custom_text)
        values ($1, $2, $3)
        """,
        tg_user_id,
        selected_options,
        custom_text,
    )


async def count_occupied_spots() -> int:
    pool = _require_pool()
    result = await pool.fetchval(
        "select count(*) from users where status = any($1::text[])",
        ["joined", "paid"],
    )
    return result or 0


async def log_event(tg_user_id: int, event_type: str, payload: dict[str, Any] | None = None) -> None:
    pool = _require_pool()
    await pool.execute(
        "insert into events (tg_user_id, event_type, payload) values ($1, $2, $3)",
        tg_user_id,
        event_type,
        payload,
    )
