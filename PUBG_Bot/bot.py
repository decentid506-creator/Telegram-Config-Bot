import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🤖 Bot Configuration
BOT_TOKEN = "8946440943:AAHqB33DivGL1jHaLLERgdt5jwZGdrffCU0"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# 👑 Aapki Real Telegram Numeric Admin ID
ADMIN_ID = 8716485628

# 📞 Aapka WhatsApp Support Number
WHATSAPP_SUPPORT = "923020604753"

# 📌 Dynamic Database (Files, Prices, Description & Links)
CONFIG_FILES = {
    "config_1": {
        "title": "VIP Ultra Smooth Config (90 FPS)",
        "price": "500 PKR",
        "desc": "🔥 Yeh config lagane ke baad game bilkul makkhan chalegi, zero lag aur 90 FPS stable rahenge!",
        "link": "https://www.mediafire.com/file/example1/config.zip"
    },
    "config_2": {
        "title": "No Recoil + Safe Main ID Config",
        "price": "800 PKR",
        "desc": "🛡️ 100% Anti-Ban safe config hai. Har gun ka recoil bilkul zero ho jayega.",
        "link": "https://www.mediafire.com/file/example2/config.zip"
    }
}

# 📌 Valid Transaction IDs (Test ke liye)
VALID_TRANSACTIONS = {
    "12345678901": {"used": False},
    "98765432109": {"used": False}
}

SMS_SERVER_ONLINE = True 

# 🏠 1. User /start kare -> Files Menu Show Hoga
@dp.message_handler(commands=['start', 'help'])
@dp.message_handler()
async def show_menu(message: types.Message):
    # Agar user ne Trx ID bheji hai
    if message.text.strip().isdigit() and len(message.text.strip()) >= 10:
        return await verify_payment(message)

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
        
    # WhatsApp Support Button
    keyboard.add(InlineKeyboardButton(text="📞 Contact WhatsApp Support", url=f"https://wa.me/{WHATSAPP_SUPPORT}"))

    await message.answer(
        "👋 **Welcome to PUBG Config Store!**\n\n"
        "Niche di gayi list me se apni pasandida file select karein:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# 📄 2. File Click Hone Par -> Details & Description Show Ho
@dp.callback_query_handler(lambda c: c.data.startswith('select_'))
async def show_file_details(callback_query: types.CallbackQuery):
    file_id = callback_query.data.split('_')[1]
    if file_id not in CONFIG_FILES:
        await bot.answer_callback_query(callback_query.id, "Yeh file ab available nahi hai!")
        return
        
    info = CONFIG_FILES[file_id]
    
    # AGAR ADMIN HAI: Toh Direct Link milega (Bina Payment ke)
    if callback_query.from_user.id == ADMIN_ID:
        text = (
            f"👑 **[ADMIN MODE] File Details**\n\n"
            f"🎮 **Name:** {info['title']}\n"
            f"💰 **Price:** {info['price']}\n"
            f"🔗 **MediaFire Link:** `{info['link']}`\n\n"
            "*(Aap Admin hain, aapko payment ki zaroorat nahi hai!)*"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_menu"))
        
        await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
        return

    # Normal User Flow
    text = (
        f"🎮 **File Name:** {info['title']}\n"
        f"💰 **Price:** {info['price']}\n\n"
        f"📝 **Description:**\n{info['desc']}\n\n"
        "Niche diye gaye button par click karke order place karein:"
    )
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🛒 Place Order (JazzCash)", callback_data=f"order_{file_id}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_menu"))
    
    await bot.edit_message_text(text=text, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

# 🛒 3. Place Order Click Hone Par -> Payment Instructions
@dp.callback_query_handler(lambda c: c.data.startswith('order_'))
async def place_order(callback_query: types.CallbackQuery):
    file_id = callback_query.data.split('_')[1]
    info = CONFIG_FILES[file_id]
    
    text = (
        f"🛒 **Order Details: {info['title']}**\n"
        f"💰 **Total Amount:** {info['price']}\n\n"
        "📌 **Payment ka Tarika:**\n"
        "1. Apne JazzCash App se is account par payment bhejein: `0302-0604753`\n"
        "2. Payment bhejne ke baad jo **11-digit Transaction ID (Trx ID)** SMS me aaye, woh seedha is chat me type karke bhej dein.\n\n"
        "⚠️ *Trx ID bhejte hi system auto-verify karke link de dega!*"
    )
    
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query.id)

# 🔙 Back to Menu
@dp.callback_query_handler(lambda c: c.data == 'back_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for file_id, info in CONFIG_FILES.items():
        keyboard.add(InlineKeyboardButton(text=f"📁 {info['title']} - {info['price']}", callback_data=f"select_{file_id}"))
    keyboard.add(InlineKeyboardButton(text="📞 Contact WhatsApp Support", url=f"https://wa.me/{WHATSAPP_SUPPORT}"))
    
    await bot.edit_message_text(text="👋 **Welcome to PUBG Config Store!**", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

# ✅ 4. Trx ID Verification & Error Handling
async def verify_payment(message: types.Message):
    global SMS_SERVER_ONLINE
    
    if not SMS_SERVER_ONLINE:
        await message.answer(
            "⚠️ **Server Error / SMS Forwarder Offline!**\n\n"
            "Filhal payment verification server se rabta nahi ho pa raha. Barah-e-karam thori der baad koshish karein ya WhatsApp Support par rabta karein."
        )
        return

    trx_id = message.text.strip()
    
    if trx_id in VALID_TRANSACTIONS:
        if VALID_TRANSACTIONS[trx_id]["used"]:
            await message.answer("❌ Yeh Transaction ID pehle hi use ho chuki hai!")
        else:
            VALID_TRANSACTIONS[trx_id]["used"] = True
            link = list(CONFIG_FILES.values())[0]["link"]
            
            await message.answer(
                "✅ **Payment Successful & Verified!**\n\n"
                f"🔗 Aapki File ka MediaFire Link yeh hai:\n{link}\n\n"
                "Aapki kharidari ka shukriya! 🎮",
                parse_mode="Markdown"
            )
    else:
        await message.answer(
            "❌ **Transaction ID Match Nahi Hui!**\n\n"
            "Barah-e-karam apni theek 11-digit Trx ID likhein ya **WhatsApp Support** se rabta karein."
        )

# 🛠️ 5. ADMIN COMMAND: File Delete (/del config_1)
@dp.message_handler(commands=['del'])
async def delete_config(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⚠️ Aap is command ko use nahi kar sakte!")
    
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("❌ Sahi tareeqa: `/del config_1`", parse_mode="Markdown")
    
    file_id = args[1]
    if file_id in CONFIG_FILES:
        del CONFIG_FILES[file_id]
        await message.answer(f"✅ File `{file_id}` kamiyabi se delete ho gayi hai!", parse_mode="Markdown")
    else:
        await message.answer("❌ Yeh File ID mojood nahi hai!")

if __name__ == '__main__':
    print("Bot is running with Admin & WhatsApp support...")
    executor.start_polling(dp, skip_updates=True)