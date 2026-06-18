import asyncio
import logging
import os
import random
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

DB_NAME = "vip_bot.db"
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
router = Router()

TITLES = [
    "Топ 100", "Основатель", "Легенда", "Император", "Элита", 
    "VIP+", "Чемпион", "Титан", "Феникс", "Мастер"
]

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💳 Купить VIP")]
    ],
    resize_keyboard=True
)

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                invited_by INTEGER,
                referrals_count INTEGER DEFAULT 0,
                vip_access INTEGER DEFAULT 0,
                vip_title TEXT
            )
        """)
        await db.commit()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    args = message.text.split(maxsplit=1)
    
    referrer_id = None
    if len(args) > 1 and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id == user_id:
            referrer_id = None

    is_new_user = False
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            is_new_user = True
            await db.execute(
                "INSERT INTO users (user_id, username, invited_by) VALUES (?, ?, ?)",
                (user_id, username, referrer_id)
            )
            await db.commit()

    if referrer_id and is_new_user:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?", (referrer_id,))
            await db.commit()

    bot_info = await bot.get_me()
    text = (
        f"👋 <b>Добро пожаловать в VIP CLUB!</b>\n\n"
        f"Здесь вы можете получить:\n"
        f"• VIP-доступ в закрытый канал\n"
        f"• Гайд по заработку в Telegram\n"
        f"• Случайный VIP-титул\n"
        f"• Доступ к каналу отзывов\n"
        f"• <b>Благодарность от основателя</b>\n"
        f"• Поддержку через @dmitriiFadZe\n\n"
        f"💡 <b>Условия покупки:</b>\n"
        f"Обычная стоимость — 15 Telegram Stars.\n"
        f"Пригласите 3 друзей по вашей ссылке, и цена снизится до 10 Stars!\n\n"
        f"🔗 Ваша ссылка: https://t.me{bot_info.username}?start={user_id}"
    )
    
    inline_pay_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="💎 Оплатить доступ", callback_data="buy_via_inline")]]
    )
    await message.answer(text, parse_mode="HTML", reply_markup=main_kb)
    await message.answer("Вы можете приобрести доступ прямо сейчас:", reply_markup=inline_pay_kb)

async def check_and_pay(message: Message, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT referrals_count, vip_access FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

    if not row:
        await message.answer("Сначала запустите бота командой /start")
        return

    ref_count, vip_access = row
    if vip_access:
        await message.answer("У вас уже есть VIP-доступ.")
        return

    price = 10 if ref_count >= 3 else 15
    await message.answer_invoice(
        title="VIP-доступ в закрытый канал",
        description="Оплата доступа в VIP Club с помощью Telegram Stars",
        currency="XTR",
        prices=[LabeledPrice(label="VIP-доступ", amount=price)],
        payload="vip_access_payload"
    )

@router.message(F.text == "💳 Купить VIP")
async def process_kb_buy(message: Message):
    await check_and_pay(message, message.from_user.id)

@router.callback_query(F.data == "buy_via_inline")
async def process_inline_buy(callback_query: any):
    await callback_query.answer()
    await check_and_pay(callback_query.message, callback_query.from_user.id)

@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, bot: Bot):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT referrals_count, vip_access FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

    if not row:
        await message.answer("Сначала запустите бота командой /start")
        return

    ref_count, vip_access = row
    current_price = 10 if ref_count >= 3 else 15
    vip_status = "Да" if vip_access else "Нет"
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me{bot_info.username}?start={user_id}"
    
    text = (
        f"🆔 ID: {user_id}\n"
        f"👥 Приглашено друзей: {ref_count}/3\n"
        f"💎 Текущая цена: {current_price} Telegram Stars\n"
        f"👑 VIP: {vip_status}\n"
        f"🔗 Ваша ссылка: {ref_link}"
    )
    await message.answer(text, disable_web_page_preview=True)

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    chosen_title = random.choice(TITLES)

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT vip_access, vip_title FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        
        if row:
            vip_access, existing_title = row
            if vip_access == 0:
                await db.execute("UPDATE users SET vip_access = 1, vip_title = ? WHERE user_id = ?", (chosen_title, user_id))
                await db.commit()
            else:
                chosen_title = existing_title

    text = (
        f"🎉 <b>Спасибо за покупку! Добро пожаловать в VIP CLUB.</b>\n\n"
        f"🎁 Ваш случайный титул: <b>{chosen_title}</b>\n\n"
        f"📘 Гайд: https://t.me+jZRAgyhdNas4NWJi\n"
        f"💬 Отзывы: https://t.me+jWdrP1oXj6pjZDg6\n"
        f"👑 VIP-канал: https://t.me+kjSna0KD3CxkZTM6"
    )
    await message.answer(text, parse_mode="HTML")

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    
    # Принудительно удаляем вебхуки и старые зависшие сессии в Telegram перед запуском
    logging.info("Удаление старых вебхуков и очистка зависших сессий...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



    




