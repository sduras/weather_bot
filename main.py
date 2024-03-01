import os
from telebot import TeleBot
from weather import get_weather_data_sync

TOKEN = os.environ['TOKEN']

bot = TeleBot(TOKEN, parse_mode='HTML', threaded=False)

@bot.message_handler(commands=['start','help','dnipro'])

def lviv_weather_report(message):
    today_report, tomorrow_report = get_weather_data_sync()
    a = f'{today_report}'
    b = f'{tomorrow_report}'
    bot.reply_to(message, "Привіт, 👤" + message.from_user.first_name + "!")
    bot.reply_to(message, f'{a}')
    bot.reply_to(message, f'{b}')

# bot.infinity_polling()


