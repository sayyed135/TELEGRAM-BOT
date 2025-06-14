import telebot

# توکن رباتت رو اینجا قرار بده
TOKEN = "7217912729:AAFjqdGSBKl3XfDtVHXUaz1GjvKLPaEYS6k"
bot = telebot.TeleBot(TOKEN)

# وقتی کاربر /start رو بفرسته
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! ربات من روشنه.")

# اجرای ربات
if __name__ == '__main__':
    print("Bot started...")
    bot.polling()
