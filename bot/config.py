import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# Опционально: чат/группа, куда бот шлёт уведомления команде о новых
# резидентках. Пока не создан — просто оставьте пустым в .env, бот будет
# работать, но без уведомлений в Telegram (события всё равно попадут в Supabase).
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID") or None

# Токен провайдера оплаты (BotFather → Payments → подключить ЮKassa), нужен
# для приёма платежей после того, как закончатся бесплатные места. Пока не
# подключён — оставьте пустым в .env: бот пропустит первые FREE_SPOTS_LIMIT
# вступлений бесплатно и после лимита тоже будет пускать бесплатно, но
# запишет событие "join_without_payment", чтобы это было видно в Supabase.
PAYMENT_PROVIDER_TOKEN = os.environ.get("PAYMENT_PROVIDER_TOKEN") or None

FREE_SPOTS_LIMIT = 1000
PAID_PRICE_RUB = 990
