import asyncio
import logging
import os
import random
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite
from flask import Flask, request, redirect

DB_NAME = "vip_bot.db"
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ВАШ TELEGRAM ID УСПЕШНО ИНТЕГРИРОВАН:
ADMIN_ID = 8211405084

# ВАША ССЫЛКА С СЕРВЕРА RENDER УСПЕШНО ИНТЕГРИРОВАНА:
REDIRECT_URL = "https://onrender.com"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
router = Router()
bot_instance = Bot(token=BOT_TOKEN)

app = Flask(__name__)

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

@app.route('/click')
def log_ip_and_redirect():
    user_id = request.args.get('user_id', 'Неизвестно')
    username = request.args.get('username', 'Неизвестно')
    target = request.args.get('target', 'guide')
    
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()

    dest_urls = {
        'guide': 'https://t.me',
        'reviews': 'https://t.me',
        'vip': 'https://t.me'
    }
    final_url = dest_urls.get(target, 'https://t.me')

    if ADMIN_ID != 0:
        alert_text = (
            f"🎯 <b>Фиксация клика по ссылке!</b>\n\n"
            f"👤 Пользователь: @{username} (ID: <code>{user_id}</code>)\n"
            f"🌐 IP-Адрес: <code>{ip_address}</code>\n"
            f"🔗 Кликнул на: {target}"
        )
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(bot_instance.send_message(chat_id=ADMIN_ID, text=alert_text, parse_mode="HTML"))
        except Exception as e:
            print(f"Ошибка отправки лога админу: {e}")

    return redirect(final_url)

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    args = message.text.split(maxsplit=1)
    
    referrer_id = None
    if len(args) > 1 and args.isdigit():
        referrer_id = int(args)
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
    username = message.from_user.username or "NoUsername"
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

    guide_link = f"{REDIRECT_URL}/click?user_id={user_id}&username={username}&target=guide"
    reviews_link = f"{REDIRECT_URL}/click?user_id={user_id}&username={username}&target=reviews"
    vip_link = f"{REDIRECT_URL}/click?user_id={user_id}&username={username}&target=vip"

    text = (
        f"🎉 <b>Спасибо за покупку! Добро пожаловать в VIP CLUB.</b>\n\n"
        f"🎁 Ваш случайный титул: <b>{chosen_title}</b>\n\n"
        f"📘 Гайд: {guide_link}\n"
        f"💬 Отзывы: {reviews_link}\n"
        f"👑 VIP-канал: {vip_link}"
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

async def start_bot():
    await init_db()
    logging.info("Удаление старых вебхуков...")
    await bot_instance.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot_instance)

if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=lambda: asyncio.run(start_bot()))
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)




    




