import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Строка подключения к своей PostgreSQL (сервер на Selectel), формат:
# postgresql://user:password@host:5432/dbname
DATABASE_URL = os.environ["DATABASE_URL"]

# Опционально: чат/группа, куда бот шлёт уведомления команде о новых
# резидентках. Пока не создан — просто оставьте пустым в .env, бот будет
# работать, но без уведомлений в Telegram (события всё равно попадут в базу).
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID") or None

# Токен провайдера оплаты (BotFather → Payments → подключить ЮKassa), нужен
# для приёма платежей после того, как закончатся бесплатные места. Пока не
# подключён — оставьте пустым в .env: бот пропустит первые FREE_SPOTS_LIMIT
# вступлений бесплатно и после лимита тоже будет пускать бесплатно, но
# запишет событие "join_without_payment", чтобы это было видно в базе.
PAYMENT_PROVIDER_TOKEN = os.environ.get("PAYMENT_PROVIDER_TOKEN") or None

# Прокси для подключения к api.telegram.org (нужен, если сервер в РФ не
# достукивается до Telegram напрямую). Формат: socks5://login:password@host:port
# (или http://... для HTTP-прокси). Пусто — бот ходит в Telegram напрямую.
PROXY_URL = os.environ.get("PROXY_URL") or None

FREE_SPOTS_LIMIT = 1000
PAID_PRICE_RUB = 990

# Модерация сообщений в темах групп сообщества (например, «Вакансии»,
# «Анкеты о себе») — поддерживает сразу несколько разных групп. Пока
# сообщество не создано, оставьте оба поля пустыми — модерация автоматически
# не активируется, остальной бот работает как обычно.
# ID чата, куда шлются заявки на проверку (с кнопками «Опубликовать»/«Отклонить»),
# общий для всех модерируемых групп.
MODERATION_CHAT_ID = os.environ.get("MODERATION_CHAT_ID") or None
# Модерируемые темы — пары "chat_id:message_thread_id" через запятую,
# например: "-1001111:12,-1002222:34" (можно из разных групп сразу).
MODERATED_TOPICS: set[tuple[int, int]] = set()
for _pair in os.environ.get("MODERATED_TOPICS", "").split(","):
    if ":" in _pair:
        _chat_id, _thread_id = _pair.split(":", 1)
        MODERATED_TOPICS.add((int(_chat_id), int(_thread_id)))
