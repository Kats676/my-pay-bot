import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    "💎 VIP CLUB BOT\n\n"
    "📘 Гайд по заработку в Telegram\n"
    "💎 VIP CLUB\n"
    "⭐ Канал отзывов\n"
    "🏆 Случайный титул\n\n"
    "Стоимость: 15 Telegram Stars ⭐"
)

await bot.send_invoice(
    chat_id=message.chat.id,
    title="VIP CLUB",
    description="VIP доступ + Гайд",
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
    f"""
```

🎉 Спасибо за покупку!

🏆 Ваш титул:
{title}

📘 Гайд:
{GUIDE_LINK}

💎 VIP канал:
{VIP_LINK}

⭐ Отзывы:
{REVIEWS_LINK}

🤝 Спасибо от основателя

💬 Поддержка:
@dmitriiFadZe
"""
)

async def main():
await dp.start_polling(bot)

if **name** == "**main**":
asyncio.run(main())


