import telebot
import json
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '7217912729:AAFuXcRQNl0p-uCQZb64cxakJD15_b414q8'
ADMIN_ID = 6994772164  # آی‌دی عددی محمد

bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'users.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_user(uid):
    data = load_data()
    if str(uid) not in data:
        data[str(uid)] = {
            'score': 0,
            'level': 'رایگان',
            'last_daily': '',
            'joined': datetime.now().isoformat()
        }
        save_data(data)
    return data[str(uid)]

def update_user(uid, field, value):
    data = load_data()
    data[str(uid)][field] = value
    save_data(data)

def change_score(uid, amount):
    data = load_data()
    data[str(uid)]['score'] += amount
    save_data(data)

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    get_user(uid)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 امتیاز روزانه", "📊 امتیاز من")
    markup.add("🛍️ خرید اشتراک", "🧑‍💼 مدیریت")
    bot.send_message(uid, "به ربات خوش آمدی!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎁 امتیاز روزانه")
def daily_reward(message):
    uid = message.from_user.id
    user = get_user(uid)
    today = datetime.now().date()
    last = datetime.fromisoformat(user['last_daily']).date() if user['last_daily'] else None
    if last == today:
        bot.send_message(uid, "تو امروز امتیازت رو گرفتی!")
    else:
        change_score(uid, 1)
        update_user(uid, 'last_daily', datetime.now().isoformat())
        bot.send_message(uid, "✅ ۱ امتیاز روزانه دریافت شد!")

@bot.message_handler(func=lambda m: m.text == "📊 امتیاز من")
def my_score(message):
    uid = message.from_user.id
    user = get_user(uid)
    bot.send_message(uid, f"امتیاز: {user['score']}\nسطح: {user['level']}")

@bot.message_handler(func=lambda m: m.text == "🛍️ خرید اشتراک")
def buy_sub(message):
    uid = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add("📦 معمولی - ۳ امتیاز", "⚙️ حرفه‌ای - ۱۰ امتیاز", "👑 VIP - 20 امتیاز", "🔙 برگشت")
    bot.send_message(uid, "یک اشتراک انتخاب کن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["📦 معمولی - ۳ امتیاز", "⚙️ حرفه‌ای - ۱۰ امتیاز", "👑 VIP - 20 امتیاز"])
def handle_buy(message):
    uid = message.from_user.id
    user = get_user(uid)
    options = {
        "📦 معمولی - ۳ امتیاز": ("معمولی", 3),
        "⚙️ حرفه‌ای - ۱۰ امتیاز": ("حرفه‌ای", 10),
        "👑 VIP - 20 امتیاز": ("VIP", 20)
    }
    level, cost = options[message.text]
    if user['score'] >= cost:
        change_score(uid, -cost)
        update_user(uid, 'level', level)
        bot.send_message(uid, f"✅ اشتراک {level} خریداری شد.")
    else:
        bot.send_message(uid, "❌ امتیاز کافی نداری.")

@bot.message_handler(func=lambda m: m.text == "🧑‍💼 مدیریت")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load_data()
    total = len(data)
    active = sum(1 for u in data.values() if u['last_daily'])
    vip = [uid for uid, u in data.items() if u['level'] == 'VIP']
    pro = [uid for uid, u in data.items() if u['level'] == 'حرفه‌ای']
    norm = [uid for uid, u in data.items() if u['level'] == 'معمولی']

    def link(uid):
        return f"[{uid}](tg://user?id={uid})"

    msg = f"""📊 آمار کاربران:

👥 کل: {total}
✅ فعال: {active}

👑 VIP:
{chr(10).join(link(u) for u in vip) or 'هیچ‌کس'}

⚙️ حرفه‌ای:
{chr(10).join(link(u) for u in pro) or 'هیچ‌کس'}

📦 معمولی:
{chr(10).join(link(u) for u in norm) or 'هیچ‌کس'}
"""
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

bot.polling()
