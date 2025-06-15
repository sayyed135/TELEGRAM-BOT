import telebot
from datetime import datetime, timedelta
import json
import os

TOKEN = "7217912729:AAFuXcRQNl0p-uCQZb64cxakJD15_b414q8"
ADMIN_ID = 6994772164

bot = telebot.TeleBot(TOKEN)
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

def get_user(uid):
    data = load_data()
    if str(uid) not in data:
        data[str(uid)] = {
            "score": 0,
            "level": "معمولی",
            "last_daily": ""
        }
        save_data(data)
    return data[str(uid)]

@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    get_user(uid)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("امتیاز روزانه", "امتیاز من")
    keyboard.row("خرید اشتراک")
    if uid == ADMIN_ID:
        keyboard.row("پنل مدیر")
    bot.send_message(uid, "سلام! به ربات خوش آمدی.", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "امتیاز روزانه")
def daily_score(msg):
    uid = msg.from_user.id
    data = load_data()
    user = get_user(uid)
    today = datetime.now().date()
    last_date = user["last_daily"]
    if last_date == str(today):
        bot.send_message(uid, "امتیاز امروز را قبلاً دریافت کردی.")
    else:
        user["score"] += 1
        user["last_daily"] = str(today)
        data[str(uid)] = user
        save_data(data)
        bot.send_message(uid, "امتیاز روزانه‌ات اضافه شد +1")

@bot.message_handler(func=lambda m: m.text == "امتیاز من")
def show_score(msg):
    uid = msg.from_user.id
    user = get_user(uid)
    bot.send_message(uid, f"امتیاز شما: {user['score']}\nسطح: {user['level']}")

@bot.message_handler(func=lambda m: m.text == "خرید اشتراک")
def buy_sub(msg):
    uid = msg.from_user.id
    user = get_user(uid)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("معمولی - 3 امتیاز", "حرفه‌ای - 10 امتیاز", "VIP - 20 امتیاز", "بازگشت")
    bot.send_message(uid, "یک اشتراک انتخاب کن:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text in ["معمولی - 3 امتیاز", "حرفه‌ای - 10 امتیاز", "VIP - 20 امتیاز"])
def handle_buy(msg):
    uid = msg.from_user.id
    user = get_user(uid)
    levels = {
        "معمولی - 3 امتیاز": ("معمولی", 3),
        "حرفه‌ای - 10 امتیاز": ("حرفه‌ای", 10),
        "VIP - 20 امتیاز": ("VIP", 20)
    }
    level, cost = levels[msg.text]
    if user["score"] >= cost:
        user["score"] -= cost
        user["level"] = level
        data = load_data()
        data[str(uid)] = user
        save_data(data)
        bot.send_message(uid, f"اشتراک {level} خریداری شد.")
    else:
        bot.send_message(uid, "امتیاز کافی نداری.")

@bot.message_handler(func=lambda m: m.text == "بازگشت")
def back(msg):
    start(msg)

@bot.message_handler(func=lambda m: m.text == "پنل مدیر" and m.from_user.id == ADMIN_ID)
def admin_panel(msg):
    data = load_data()
    total = len(data)
    active = sum(1 for u in data.values() if u["last_daily"])
    levels = {"VIP": [], "حرفه‌ای": [], "معمولی": []}
    for uid, user in data.items():
        levels[user["level"]].append(uid)
    def make_links(uids):
        return "\n".join([f"[{uid}](tg://user?id={uid})" for uid in uids]) or "هیچ‌کس"
    msg_text = f"""آمار کاربران:
کل کاربران: {total}
کاربران فعال: {active}

VIP:
{make_links(levels["VIP"])}

حرفه‌ای:
{make_links(levels["حرفه‌ای"])}

معمولی:
{make_links(levels["معمولی"])}
"""
    bot.send_message(msg.chat.id, msg_text, parse_mode="Markdown")

bot.infinity_polling()
