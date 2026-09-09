#!/usr/bin/env bash
set -euo pipefail

UNIT_NAME="${1:-unknown}"

if [ -z "${ADMIN_CHAT_ID:-}" ]; then
  exit 0
fi

PROXY_ARGS=()
if [ -n "${PROXY_URL:-}" ]; then
  PROXY_ARGS=(--proxy "$PROXY_URL")
fi

IFS=',' read -ra CHAT_IDS <<< "${ADMIN_CHAT_ID}"
for CHAT_ID in "${CHAT_IDS[@]}"; do
  curl -s "${PROXY_ARGS[@]}" -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="🔴 Бот «Женщины нового времени» упал и не смог перезапуститься сам (${UNIT_NAME}). Нужно проверить сервер."
done
