import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart

# Токен автоматически подтягивается из настроек сервера Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        text="Привет! В этом боте ты можешь купить эксклюзивный Гайд.\n"
             "Стоимость: 15 Telegram Stars.\n"
             "Для покупки нажмите на кнопку ниже 👇"
    )
    
    # Отправка счета на оплату через Telegram Stars (XTR)
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Гайд по заработку в Telegram",
        description="Полное практическое руководство.",
        payload="digital_guide_payload",
        provider_token="",  # Для Telegram Stars поле оставляют пустым
        currency="XTR",
        prices=[LabeledPrice(label="Гайд", amount=15)]  # Цена изменена на 15 Stars
    )

# 2. Обработчик предварительной проверки платежа (PreCheckoutQuery)
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 3. Обработчик успешного платежа
@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    # Ваша ссылка на канал без лишних пробелов
    await message.answer(text="🎉 Спасибо за покупку! Вот тут ваш гайд:https://t.me/+jZRAgyhdNas4NWJi")

# 4. Главная функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
