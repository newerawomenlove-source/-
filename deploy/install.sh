#!/usr/bin/env bash
# Запускать на сервере из корня проекта: bash deploy/install.sh [пользователь]
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_USER="${1:-$(whoami)}"

chmod +x "$PROJECT_DIR/deploy/notify_down.sh"

sed \
  -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
  -e "s|__USER__|$SERVICE_USER|g" \
  "$PROJECT_DIR/deploy/wnw-bot.service" | sudo tee /etc/systemd/system/wnw-bot.service > /dev/null

sed \
  -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
  "$PROJECT_DIR/deploy/wnw-bot-notify-down@.service" | sudo tee /etc/systemd/system/wnw-bot-notify-down@.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable --now wnw-bot.service

echo "Готово. Статус: sudo systemctl status wnw-bot"
echo "Логи:        sudo journalctl -u wnw-bot -f"
