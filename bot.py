import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ሎግ ማዘጋጀት
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==========================================
# 1. የአንተ መረጃ (እንዳለ ተወው)
# ==========================================
BOT_TOKEN = "9125443391:AAHmmlgoIlY_9H9h-ToYPwsUjNOn9oIqnlU" 
CHANNEL_1 = "@tiktok_music_lighting" 

# ==========================================
# 2. የሙዚቃ ፋይሎች ማከማቻ
# ==========================================
MUSIC_DATABASE = {
    "funk_1": "የመጀመሪያው_ፋንክ_ሙዚቃ_file_id_እዚህ_ይገባል",
    "phonk_1": "የመጀመሪያው_ፎንክ_ሙዚቃ_file_id_እዚህ_ይገባል",
}

# --- የቦት ተግባራት (እንዳሉ ተዋቸው) ---
async def check_membership(user_id, context):
    if not CHANNEL_1 or CHANNEL_1 == "@your_channel_1": return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_1, user_id=user_id)
        if member.status in ['left', 'kicked']: return False
    except Exception as e:
        logging.error(f"Channel check error: {e}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    is_member = await check_membership(user_id, context)
    if not is_member:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("📢 ቻናል ተቀላቀል", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")]]
        await update.message.reply_text(f"ሰላም {user_name}!\n⚠️ እባክህ መጀመሪያ ቻናሉን ተቀላቀል።\nከተቀላቀልክ በኋላ /start ን ተጫን።", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    if context.args:
        file_key = context.args[0]
        if file_key in MUSIC_DATABASE:
            try: await context.bot.send_audio(chat_id=user_id, audio=MUSIC_DATABASE[file_key], caption="🎧 ይደሰቱ!")
            except Exception: await update.message.reply_text("❌ ሙዚቃውን መላክ አልቻልኩም።")
        else: await update.message.reply_text("❌ ይህ ሙዚቃ አልተገኘም።")
    else: await update.message.reply_text(f"እንኳን ደህና መጣህ {user_name}! 🎵\nከቻናላችን ላይ ያለውን ሊንክ ተጭነህ ተጠቀም።")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.audio: await update.message.reply_text(f"File ID:\n`{update.message.audio.file_id}`")
    else: await update.message.reply_text("እባክህ አንድ የሙዚቃ (Audio) ፋይል ላክ።")

# --- Flask ዌብ ሰርቨር (Render እንዲያየው) ---
app = Flask(__name__)

@app.route('/')
def home(): return "Bot is running!"

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_file_id))
    application.add_handler(MessageHandler(filters.AUDIO, get_file_id))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ቦቱን በተለየ መስመር (Thread) ማስኬድ
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    # Render የሚሰጠውን ፖርት መጠቀም
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
