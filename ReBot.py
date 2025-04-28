from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters
)
import sqlite3
import time
import threading
import os
from flask import Flask, redirect

# استبدل هذه القيم!
BOT_TOKEN = "7875189417:AAHeT-95FjjdewIcluWyA0FIkKNyezrdjrg"
CHANNEL_ID = -1002483195333  # الـ ID الرقمي (باستخدام الطريقة أعلاه)

# تكوين قاعدة البيانات
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
conn.commit()

# إعداد السيرفر الوهمي
app = Flask(__name__)

@app.route('/')
def home():
    return redirect("https://t.me/tasse_sy", code=302)

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        await update.message.reply_text("✅ تم تفعيلك!")
    except Exception as e:
        print(f"Error: {e}")

async def forward_to_users(update: Update, context: CallbackContext):
    if update.channel_post:
        message = update.channel_post
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()

        for user in users:
            user_id = user[0]
            for _ in range(2):
                try:
                    await context.bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=CHANNEL_ID,
                        message_id=message.message_id
                    )
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error for user {user_id}: {e}")

def main():
    # تشغيل السيرفر الوهمي بالخلفية
    threading.Thread(target=run_web).start()
    
    # تشغيل البوت
    app_tg = ApplicationBuilder().token(BOT_TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.Chat(chat_id=CHANNEL_ID), forward_to_users))
    app_tg.add_handler(CommandHandler("start", start))
    print("✅ البوت يعمل...")
    app_tg.run_polling()

if __name__ == "__main__":
    main()
