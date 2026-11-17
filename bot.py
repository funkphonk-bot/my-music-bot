import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- YOUR INFO ---
BOT_TOKEN = "9125443391:AAHmmlgoIlY_9H9h-ToYPwsUjNOn9oIqnlU" 
CHANNEL_1 = "@tiktok_music_lighting" 

# --- MUSIC DATABASE ---
MUSIC_DATABASE = {
    "funk_1": "PLACEHOLDER_FUNK_1",
    "phonk_1": "PLACEHOLDER_PHONK_1",
}

# --- FUNCTIONS ---
async def check_membership(user_id, context):
    if not CHANNEL_1 or CHANNEL_1 == "@your_channel_1":
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_1, user_id=user_id)
        if member.status in ['left', 'kicked']:
            return False
    except Exception as e:
        logging.error(f"Channel check error: {e}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    is_member = await check_membership(user_id, context)
    
    if not is_member:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")]]
        await update.message.reply_text(
            f"Hello {user_name}!\n⚠️ Please join our channel first.\nAfter joining, send /start again.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if context.args:
        file_key = context.args[0]
        if file_key in MUSIC_DATABASE:
            file_id = MUSIC_DATABASE[file_key]
            try:
                await context.bot.send_audio(chat_id=user_id, audio=file_id, caption="🎧 Enjoy!")
            except Exception:
                await update.message.reply_text("❌ Failed to send the music.")
        else:
            await update.message.reply_text("❌ Music not found.")
    else:
        await update.message.reply_text(f"Welcome {user_name}! 🎵\nUse the links from our channel to get music.")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.audio:
        file_id = update.message.audio.file_id
        await update.message.reply_text(f"File ID:\n`{file_id}`\n\nCopy this and paste it into MUSIC_DATABASE in the code.")
    else:
        await update.message.reply_text("Please send an audio file.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_file_id))
    application.add_handler(MessageHandler(filters.AUDIO, get_file_id)) 
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
