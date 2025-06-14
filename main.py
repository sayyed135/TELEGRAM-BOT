import telebot
import json
import os

TOKEN = "7217912729:AAE9WC3RD1Waeu3vYB0ajF7Abl3OHTsThoo"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6994772164  # آیدی عددی خودت رو اینجا بزار

DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = 0
        save_data(data)
    bot.reply_to(message, "سلام! به ربات امتیازی خوش آمدید.")


@bot.message_handler(commands=['score'])
def show_score(message):
    user_id = str(message.from_user.id)
    data = load_data()
    score = data.get(user_id, 0)
    bot.reply_to(message, f"امتیاز شما: {score}")


@bot.message_handler(commands=['add_score'])
def add_score(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "فقط مدیر می‌تونه امتیاز بده.")

    try:
        _, user_id, score_type = message.text.split()
        user_id = str(user_id)
        score_type = score_type.lower()

        if score_type == "الماسی":
            amount = 5
        elif score_type == "حرفه‌ای" or score_type == "حرفه اي":
            amount = 3
        elif score_type == "سکه‌ای" or score_type == "سکه اي":
            amount = 1
        else:
            return bot.reply_to(message, "نوع امتیاز نامعتبر است.")

        data = load_data()
        data[user_id] = data.get(user_id, 0) + amount
        save_data(data)
        bot.reply_to(message, f"{amount} امتیاز برای کاربر {user_id} اضافه شد.")
    except:
        bot.reply_to(message, "فرمت دستور اشتباه است.\nفرمت: /add_score user_id نوع_امتیاز")


@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = message.text.replace("/broadcast", "").strip()
    if not msg:
        return bot.reply_to(message, "لطفاً متنی برای ارسال همگانی بنویسید.")

    data = load_data()
    for uid in data:
        try:
            bot.send_message(uid, f"📢 پیام مدیر:\n\n{msg}")
        except:
            pass

    bot.reply_to(message, "پیام برای همه کاربران ارسال شد.")


bot.infinity_polling()
