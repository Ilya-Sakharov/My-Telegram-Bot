import telebot
import json
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Токен из переменной окружения
TOKEN = os.getenv('TOKEN')
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

# Создаём главное меню с кнопками
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Прошёл 5000 шагов'))
    keyboard.add(KeyboardButton('Съел шоколадку'))
    keyboard.add(KeyboardButton('Показать баланс'))
    keyboard.add(KeyboardButton('Обнулить историю'))
    return keyboard

# Создаём inline-кнопки для подтверждения обнуления
def get_reset_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Да, обнулить', callback_data=f'reset_confirm_{user_id}'))
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=f'reset_cancel_{user_id}'))
    return keyboard

# Реакция на /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in balances:
        balances[user_id] = 0
        save_data()
    bot.send_message(message.chat.id, 'привет', reply_markup=get_main_keyboard())

# Обработка нажатий кнопок (основное меню)
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

    elif text == 'Обнулить историю':
        # Показываем подтверждение
        bot.send_message(
            message.chat.id, 
            f'⚠️ Вы уверены, что хотите обнулить историю?\n\nЭто действие удалит все ваши очки ({balances[user_id]} очков) и нельзя будет отменить!',
            reply_markup=get_reset_keyboard(user_id)
        )

    else:
        bot.send_message(message.chat.id, 'Используй кнопки!', reply_markup=get_main_keyboard())

# Обработка inline-кнопок (подтверждение обнуления)
@bot.callback_query_handler(func=lambda call: call.data.startswith('reset_'))
def handle_reset_callback(call):
    user_id = call.data.split('_')[2]  # Извлекаем user_id из callback_data
    
    if call.data.startswith('reset_confirm_'):
        # Пользователь подтвердил обнуление
        balances[user_id] = 0
        save_data()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='✅ История успешно обнулена! Ваш новый баланс: 0 очков.\n\nНачните заново с кнопок ниже.',
            reply_markup=get_main_keyboard()
        )
        bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=get_main_keyboard())
        
    elif call.data.startswith('reset_cancel_'):
        # Пользователь отменил обнуление
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='❌ Обнуление отменено. Ваш баланс сохранён: {} очков.'.format(balances[user_id]),
            reply_markup=get_main_keyboard()
        )

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
