import telebot
import json
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Вставь сюда свой токен от BotFather
TOKEN = 7327050078:AAHNRHkHQbnI3xftSd170IHl63sEy0V35wU
bot = telebot.TeleBot(TOKEN)

# Файл для хранения балансов
DATA_FILE = 'balances.json'

# Загружаем балансы
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        balances = json.load(f)
else:
    balances = {}

# Сохраняем балансы
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(balances, f)

# Создаём меню с кнопками
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Прошёл 5000 шагов'))
    keyboard.add(KeyboardButton('Съел шоколадку'))
    keyboard.add(KeyboardButton('Показать баланс'))
    return keyboard

# Реакция на /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in balances:
        balances[user_id] = 0
        save_data()
    bot.send_message(message.chat.id, 'привет', reply_markup=get_main_keyboard())

# Реакция на кнопки
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    if user_id not in balances:
        balances[user_id] = 0
        save_data()

    text = message.text

    if text == 'Прошёл 5000 шагов':
        balances[user_id] += 10
        save_data()
        bot.send_message(message.chat.id, f'Добавлено 10 очков! Текущий баланс: {balances[user_id]} очков', reply_markup=get_main_keyboard())

    elif text == 'Съел шоколадку':
        balances[user_id] -= 10
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 10 очков! Текущий баланс: {balances[user_id]} очков', reply_markup=get_main_keyboard())

    elif text == 'Показать баланс':
        bot.send_message(message.chat.id, f'Ваш баланс – {balances[user_id]} очков', reply_markup=get_main_keyboard())

    else:
        bot.send_message(message.chat.id, 'Используй кнопки!', reply_markup=get_main_keyboard())

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
