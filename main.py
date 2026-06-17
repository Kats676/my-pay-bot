import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ContentType
from aiogram.filters import CommandStart

# Токен автоматически подтянется из настроек сервера
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        text="👋 Привет! В этом боте ты можешь купить эксклюзивный Гайд.\n"
             "Стоимость: 50 Telegram Stars.\n"
             "Для покупки нажмите на кнопку ниже 👇"
    )
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Гайд по заработку в Telegram",
        description="Полное практическое руководство.",
        payload="digital_guide_payload",
        provider_token="", 
        currency="XTR",    
        prices=[LabeledPrice(label="Гайд", amount=50)]
    )

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment_handler(message: Message):
    await message.answer(text="🎉 Спасибо за покупку! Вот тут ваш гайд. : https://t.me/+6HlX7mRtuqg5OGEy.)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
