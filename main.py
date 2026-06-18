import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
raise ValueError("BOT_TOKEN не найден в Render")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

VIP_LINK = "https://t.me/+kjSna0KD3CxkZTM6"
REVIEWS_LINK = "https://t.me/+jWdrP1oXj6pjZDg6"
GUIDE_LINK = "https://t.me/+jZRAgyhdNas4NWJi"

TITLES = [
"Топ 100",
"Основатель",
"Легенда",
"Император",
"Элита",
"VIP+",
"Чемпион",
"Титан",
"Феникс",
"Мастер"
]

@dp.message(CommandStart())
async def start_command(message: Message):

```
await message.answer(
    """
```

💎 VIP CLUB BOT

Добро пожаловать!

🔥 Возможности бота:

📘 Гайд по заработку в Telegram
💎 Доступ в VIP CLUB
⭐ Доступ в канал отзывов
🏆 Случайный VIP-титул
🎁 Спасибо от основателя
👑 Статус VIP участника

⭐ Стоимость: 15 Telegram Stars

💬 Поддержка:
@dmitriiFadZe

Для покупки используйте счёт ниже 👇
"""
)

```
await bot.send_invoice(
    chat_id=message.chat.id,
    title="VIP CLUB",
    description="VIP доступ + Гайд + Титул",
    payload="vip_access",
    provider_token="",
    currency="XTR",
    prices=[
        LabeledPrice(
            label="VIP CLUB",
            amount=15
        )
    ]
)
```

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
await bot.answer_pre_checkout_query(
pre_checkout_query.id,
ok=True
)

@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):

```
title = random.choice(TITLES)

await message.answer(
```

f"""
🎉 Спасибо за покупку VIP CLUB!

🏆 Ваш титул:
{title}

📘 Гайд:
{GUIDE_LINK}

💎 VIP канал:
{VIP_LINK}

⭐ Канал отзывов:
{REVIEWS_LINK}

🤝 Спасибо от основателя!

💬 Поддержка:
@dmitriiFadZe

Добро пожаловать в VIP CLUB 🚀
"""
)

async def main():
print("Бот запущен")
await dp.start_polling(bot)

if **name** == "**main**":
asyncio.run(main())

