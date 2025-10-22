import telebot
import json
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import threading
import time

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

# Создаём главное меню
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Положительные действия'))
    keyboard.add(KeyboardButton('Отрицательные действия'))
    keyboard.add(KeyboardButton('Показать баланс'))
    keyboard.add(KeyboardButton('Обнулить историю'))
    keyboard.add(KeyboardButton('Дополнительно'))
    return keyboard

# Создаём меню "Положительные действия"
def get_positive_actions_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('5 000 шагов (+15)'))
    keyboard.add(KeyboardButton('Полноценная тренировка (+30)'))
    keyboard.add(KeyboardButton('Мини-тренировка (+15)'))
    keyboard.add(KeyboardButton('Вернуться в главное меню'))
    return keyboard

# Создаём меню "Отрицательные действия"
def get_negative_actions_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Мини-шоколадка (-10)'))
    keyboard.add(KeyboardButton('Большая шоколадка (-20)'))
    keyboard.add(KeyboardButton('Бокал вина/пива (-20)'))
    keyboard.add(KeyboardButton('Кекс/круассан/пирожное (-20)'))
    keyboard.add(KeyboardButton('Тяжёлое блюдо (-30)'))
    keyboard.add(KeyboardButton('Сигара (-30)'))
    keyboard.add(KeyboardButton('Вернуться в главное меню'))
    return keyboard

# Создаём меню "Дополнительно"
def get_extra_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Обнулять историю каждый день'))
    keyboard.add(KeyboardButton('Вернуться в главное меню'))
    return keyboard

# Создаём inline-кнопки для подтверждения обнуления
def get_reset_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Да, обнулить', callback_data=f'reset_confirm_{user_id}'))
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=f'reset_cancel_{user_id}'))
    return keyboard

# Создаём inline-кнопки для включения/выключения автообнуления
def get_auto_reset_keyboard(user_id, enable):
    keyboard = InlineKeyboardMarkup()
    action = 'Включить' if not enable else 'Выключить'
    callback = f'auto_reset_on_{user_id}' if not enable else f'auto_reset_off_{user_id}'
    keyboard.add(InlineKeyboardButton(f'{action} автообнуление', callback_data=callback))
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=f'auto_reset_cancel_{user_id}'))
    return keyboard

# Приветственное сообщение с экранированными символами
WELCOME_MESSAGE = r"""
Привет\!\ Это бот от телеграм-канала @caxapandwine\. **Вы хотите быть в форме, но считать калории вам лень?** Есть решение\!\n\n
Это игра-тамагочи для вашего тела\. За каждое "хорошее" действие вы будете получать очки\. За каждое плохое – тратить\.\n\n
**Как в соревновании факультетов в Гарри Поттере\!\**\n\n
Например, прошли 5 000 шагов \– получили 15 очков\.\n
Съели большую шоколадку \– потратили 20 очков\.\n\n
Вам не нужно считать калории или очень сильно заморачиваться в выборе диеты\.\n\n
**Смысл намного легче \– просто старайтесь, чтобы в конце каждого дня у вас был положительный баланс\.**\n\n
В боте есть кнопка "Обнулить историю"\. Она позволит начать всё сначала\.\n\n
Если хотите, чтобы история автоматически обнулялась каждый день \– нажмите на кнопку "Дополнительно", затем выберите "Обнулять историю каждый день"\.\n\n
Приятного использования\!\n\n
P\.S\. Пожелания и комментарии о работе бота присылайте в лс @Ilia_caxap\n
P\.P\.S\. И подпишитесь на канал @caxapandwine
"""

# Реакция на /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in balances:
        balances[user_id] = {'balance': 0, 'auto_reset': False, 'last_reset': None}
        save_data()
    bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode='MarkdownV2', reply_markup=get_main_keyboard())

# Обработка нажатий кнопок (основное меню и подменю)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    if user_id not in balances:
        balances[user_id] = {'balance': 0, 'auto_reset': False, 'last_reset': None}
        save_data()

    text = message.text

    # Главное меню
    if text == 'Положительные действия':
        bot.send_message(message.chat.id, 'Выберите положительное действие:', reply_markup=get_positive_actions_keyboard())

    elif text == 'Отрицательные действия':
        bot.send_message(message.chat.id, 'Выберите отрицательное действие:', reply_markup=get_negative_actions_keyboard())

    elif text == 'Показать баланс':
        bot.send_message(message.chat.id, f'Ваш баланс \\– {balances[user_id]["balance"]} очков', reply_markup=get_main_keyboard())

    elif text == 'Обнулить историю':
        bot.send_message(
            message.chat.id, 
            f'⚠️ Вы уверены, что хотите обнулить историю?\n\nЭто действие удалит все ваши очки ({balances[user_id]["balance"]} очков) и нельзя будет отменить\\!',
            reply_markup=get_reset_keyboard(user_id)
        )

    elif text == 'Дополнительно':
        bot.send_message(message.chat.id, 'Дополнительные настройки:', reply_markup=get_extra_keyboard())

    # Подменю "Положительные действия"
    elif text == '5 000 шагов (+15)':
        balances[user_id]['balance'] += 15
        save_data()
        bot.send_message(message.chat.id, f'Добавлено 15 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_positive_actions_keyboard())

    elif text == 'Полноценная тренировка (+30)':
        balances[user_id]['balance'] += 30
        save_data()
        bot.send_message(message.chat.id, f'Добавлено 30 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_positive_actions_keyboard())

    elif text == 'Мини-тренировка (+15)':
        balances[user_id]['balance'] += 15
        save_data()
        bot.send_message(message.chat.id, f'Добавлено 15 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_positive_actions_keyboard())

    # Подменю "Отрицательные действия"
    elif text == 'Мини-шоколадка (-10)':
        balances[user_id]['balance'] -= 10
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 10 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    elif text == 'Большая шоколадка (-20)':
        balances[user_id]['balance'] -= 20
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 20 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    elif text == 'Бокал вина/пива (-20)':
        balances[user_id]['balance'] -= 20
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 20 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    elif text == 'Кекс/круассан/пирожное (-20)':
        balances[user_id]['balance'] -= 20
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 20 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    elif text == 'Тяжёлое блюдо (-30)':
        balances[user_id]['balance'] -= 30
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 30 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    elif text == 'Сигара (-30)':
        balances[user_id]['balance'] -= 30
        save_data()
        bot.send_message(message.chat.id, f'Вычтено 30 очков! Текущий баланс: {balances[user_id]["balance"]} очков', reply_markup=get_negative_actions_keyboard())

    # Подменю "Дополнительно"
    elif text == 'Обнулять историю каждый день':
        enable = not balances[user_id].get('auto_reset', False)
        action = 'включить' if enable else 'выключить'
        bot.send_message(
            message.chat.id,
            f'Вы хотите {action} автоматическое обнуление баланса каждый день в 00:00?',
            reply_markup=get_auto_reset_keyboard(user_id, enable)
        )

    elif text == 'Вернуться в главное меню':
        bot.send_message(message.chat.id, 'Возвращаемся в главное меню:', reply_markup=get_main_keyboard())

    else:
        bot.send_message(message.chat.id, 'Используй кнопки!', reply_markup=get_main_keyboard())

# Обработка inline-кнопок (подтверждение обнуления)
@bot.callback_query_handler(func=lambda call: call.data.startswith('reset_'))
def handle_reset_callback(call):
    user_id = call.data.split('_')[2]
    
    if call.data.startswith('reset_confirm_'):
        balances[user_id]['balance'] = 0
        balances[user_id]['last_reset'] = datetime.now().isoformat()
        save_data()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Ваша история обнулилась. Теперь у вас 0 очков.',
            reply_markup=None
        )
        bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=get_main_keyboard())
        
    elif call.data.startswith('reset_cancel_'):
        bot.edit_message_text(
            cha
t_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'❌ Обнуление отменено. Ваш баланс сохранён: {balances[user_id]["balance"]} очков.',
            reply_markup=get_main_keyboard()
        )

# Обработка inline-кнопок (автообнуление)
@bot.callback_query_handler(func=lambda call: call.data.startswith('auto_reset_'))
def handle_auto_reset_callback(call):
    user_id = call.data.split('_')[3]
    
    if call.data.startswith('auto_reset_on_'):
        balances[user_id]['auto_reset'] = True
        save_data()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='✅ Автообнуление включено! Баланс будет сбрасываться каждый день в 00:00.',
            reply_markup=None
        )
        bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=get_extra_keyboard())
        
    elif call.data.startswith('auto_reset_off_'):
        balances[user_id]['auto_reset'] = False
        save_data()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='❌ Автообнуление выключено.',
            reply_markup=None
        )
        bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=get_extra_keyboard())
        
    elif call.data.startswith('auto_reset_cancel_'):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='❌ Действие отменено.',
            reply_markup=get_extra_keyboard()
        )

# Функция для автообнуления балансов
def auto_reset_balances():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:  # Проверка на 00:00 UTC
            for user_id in balances:
                if balances[user_id].get('auto_reset', False):
                    balances[user_id]['balance'] = 0
                    balances[user_id]['last_reset'] = now.isoformat()
                    try:
                        bot.send_message(user_id, '🕛 Ваш баланс обнулился автоматически. Теперь у вас 0 очков.')
                    except:
                        pass  # Игнорируем ошибки отправки
            save_data()
        time.sleep(60)  # Проверяем каждую минуту

# Запускаем автообнуление в отдельном потоке
threading.Thread(target=auto_reset_balances, daemon=True).start()

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
