import logging
import re
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiohttp import web

# 🤖 Bot Configuration
BOT_TOKEN = "8946440943:AAHqB33DivGL1jHaLLERgdt5jwZGdrffCU0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# 👑 System Settings
ADMIN_ID = 8716485628
WHATSAPP_SUPPORT = "923020604753"
JAZZCASH_NUMBER = "03275326511"
JAZZCASH_NAME = "Asiya Imtiaz"

# 📌 Dynamic Database
CONFIG_FILES = {
    "config_1": {
        "title": "VIP Ultra Smooth Config (90 FPS)",
        "price": "500 PKR",
        "desc": "🔥 High performance 90 FPS config for smooth gameplay and zero lag!",
        "link": "https://www.mediafire.com/file/example_1/config.zip"
    }
}

# 📌 Verified Transaction IDs Storage
RECEIVED_TRANSACTIONS = {}

# ------------------- 🏠 USER HANDLERS ------------------- #

@dp.message_handler(commands=['start', 'help'])
@dp.message_handler()
async def main_handler(message: types.Message):
    # Check if text is an 11-digit Trx ID sent by user
    user_text = message.text.strip()
    if user_text.isdigit() and len(user_text) >= 10:
        return await verify_payment(message, user_text)

    # Standard /start Command Menu
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if not CONFIG_FILES:
        await message.answer("⚠️ Filhal koi bhi config file available nahi hai.")
        return

    for file_id, info in CONFIG_FILES.items():
        btn = InlineKeyboardButton(
            text=f"📁 {info['title']} - {info['price']}",
            callback_data=f"select_{file_id}"
        )
        keyboard.add(btn)
        
    keyboard.add(InlineKeyboardButton(text="📞 Contact WhatsApp Support", url=f"https://wa.me/{WHATSAPP_SUPPORT}"))

    await message.answer(
        "👋 **Welcome to PUBG Config Store!**\n\n"
        "Niche di gayi list me se apni pasandida file select karein:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# 📄 File Details Callback
@dp.callback_query_handler(lambda c: c.data.startswith('select_'))
async def show_file_details(callback_query: types.CallbackQuery):
    file_id = callback_query.data.split('_')[1]
    if file_id not in CONFIG_FILES:
        await bot.answer_callback_query(callback_query.id, "Yeh file ab available nahi hai!")
        return
        
    info = CONFIG_FILES[file_id]
    
    # ADMIN Mode Direct View
    if callback_query.from_user.id == ADMIN_ID:
        text = (
            f"👑 **[ADMIN MODE] Direct Access**\n\n"
            f"🎮 **Name:** {info['title']}\n"
            f"💰 **Price:** {info['price']}\n"
            f"📝 **Desc:** {info['desc']}\n\n"
            f"🔗 **Direct Link:** `{info['link']}`"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu"))
        await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
        return

    text = (
        f"🎮 **File Name:** {info['title']}\n"
        f"💰 **Price:** {info['price']}\n\n"
        f"📝 **Description:**\n{info['desc']}\n\n"
        "Order place karne ke liye niche button par click karein:"
    )
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🛒 Place Order (JazzCash QR)", callback_data=f"order_{file_id}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_menu"))
    
    await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

# 🛒 Order & QR Code Handler
@dp.callback_query_handler(lambda c: c.data.startswith('order_'))
async def place_order(callback_query: types.CallbackQuery):
    file_id = callback_query.data.split('_')[1]
    info = CONFIG_FILES[file_id]
    
    text = (
        f"🛒 **Order Details: {info['title']}**\n"
        f"💰 **Total Amount:** {info['price']}\n\n"
        "📌 **Payment Instructions:**\n"
        f"1. Is JazzCash QR Code ko scan karein ya account par payment bhejein:\n"
        f"👉 Account: `{JAZZCASH_NUMBER}` ({JAZZCASH_NAME})\n\n"
        "2. Payment bhejne ke baad jo **11-digit Transaction ID (Trx ID)** SMS me aaye, usko **is chat me type karke bhej dein**.\n\n"
        "⚡ *Trx ID bhejte hi system auto-verify karke link bhej dega!*"
    )
    
    qr_path = "jazzcash_qr.png"
    if os.path.exists(qr_path):
        photo = InputFile(qr_path)
        await bot.send_photo(callback_query.from_user.id, photo=photo, caption=text, parse_mode="Markdown")
    else:
        await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
        
    await bot.answer_callback_query(callback_query.id)

# 🔙 Back Menu
@dp.callback_query_handler(lambda c: c.data == 'back_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file_id, info in CONFIG_FILES.items():
        keyboard.add(InlineKeyboardButton(text=f"📁 {info['title']} - {info['price']}", callback_data=f"select_{file_id}"))
    keyboard.add(InlineKeyboardButton(text="📞 Contact WhatsApp Support", url=f"https://wa.me/{WHATSAPP_SUPPORT}"))
    
    await bot.edit_message_text(text="👋 **Welcome to PUBG Config Store!**\n\nNiche di gayi list me se apni pasandida file select karein:", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

# ✅ Verify Payment Logic
async def verify_payment(message: types.Message, trx_id: str):
    if trx_id in RECEIVED_TRANSACTIONS:
        if RECEIVED_TRANSACTIONS[trx_id]["used"]:
            await message.answer("❌ Yeh Transaction ID pehle hi use ho chuki hai!")
        else:
            RECEIVED_TRANSACTIONS[trx_id]["used"] = True
            link = list(CONFIG_FILES.values())[0]["link"]
            
            await message.answer(
                "✅ **Payment Auto-Verified & Successful!**\n\n"
                f"🔗 **Aapki File ka Download Link:**\n{link}\n\n"
                "Aapki kharidari ka shukriya! 🎮",
                parse_mode="Markdown"
            )
    else:
        await message.answer(
            "❌ **Transaction ID Match Nahi Hui!**\n\n"
            "Barah-e-karam thori der intezar karein ya sahi 11-digit Trx ID type karein. Agar masla aaye toh Support par rabta karein."
        )

# ------------------- 👑 ADMIN PANEL COMMANDS ------------------- #

# Add File Syntax: /add file_id | Title | Price | Description | Link
@dp.message_handler(commands=['add'])
async def add_config(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = [p.strip() for p in message.text.replace("/add", "").split('|')]
        CONFIG_FILES[parts[0]] = {"title": parts[1], "price": parts[2], "desc": parts[3], "link": parts[4]}
        await message.answer(f"✅ Config File `{parts[0]}` Add ho gayi!")
    except Exception:
        await message.answer("❌ Format Error!\nUse: `/add id | Title | Price | Desc | Link`", parse_mode="Markdown")

# Delete File Syntax: /del file_id
@dp.message_handler(commands=['del'])
async def delete_config(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) >= 2 and args[1] in CONFIG_FILES:
        del CONFIG_FILES[args[1]]
        await message.answer(f"✅ File `{args[1]}` delete ho gayi!")
    else:
        await message.answer("❌ Valid file ID likhein. Example: `/del config_1`", parse_mode="Markdown")

# Stats Command: /stats
@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    total_files = len(CONFIG_FILES)
    total_trx = len(RECEIVED_TRANSACTIONS)
    await message.answer(f"📊 **Store Stats:**\n\n📁 Total Files: `{total_files}`\n💳 Received TrxIDs: `{total_trx}`", parse_mode="Markdown")

# ------------------- 🌐 WEBHOOK SERVER FOR APP ------------------- #

async def handle_sms_webhook(request):
    try:
        data = await request.json()
        sms_text = data.get("message", "") or data.get("text", "")
        
        # Regex to extract 11-digit Trx ID
        match = re.search(r'TrxID[:\s]*(\d{11})', sms_text, re.IGNORECASE) or re.search(r'\b\d{11}\b', sms_text)
        if match:
            trx_id = match.group(1) if match.lastindex else match.group(0)
            RECEIVED_TRANSACTIONS[trx_id] = {"used": False}
            print(f"✅ Webhook Received New TrxID: {trx_id}")
            return web.json_response({"status": "success", "trx_id": trx_id})
    except Exception as e:
        print("Webhook Exception:", e)
    return web.json_response({"status": "failed"})

# App Startup & Dynamic Port for Cloud Hosting
async def on_startup(dp):
    app = web.Application()
    app.router.add_post('/sms_webhook', handle_sms_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Environment variable PORT is used by cloud hosts like Render
    port = int(os.environ.get("PORT", 5000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🚀 Webhook listening on port {port}...")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
