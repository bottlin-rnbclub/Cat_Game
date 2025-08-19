import telebot
import requests
from time import sleep
import warnings



warnings.filterwarnings('ignore') # python -W ignore bot.py

SERVER_URL = "http://localhost:5000"
TOKEN = "8421861669:AAHtD89LD76iPA61N4_qNZ-izsVP4I200Ms" # BotFather

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'join'])
def handle_main_join(message):
    response = requests.post(
        f"{SERVER_URL}/api/join",
        json={
            'username': message.from_user.username,
            'telegram_id': message.from_user.id
        }
    )
    if response.json().get('status') == 'success': # проверка статуса
        markup = telebot.types.ReplyKeyboardMarkup(row_width=3)
        markup.add(telebot.types.KeyboardButton('↑'))  #  https://symbl.cc/ru/2191/


        markup.add(
            telebot.types.KeyboardButton('←'),
            telebot.types.KeyboardButton('⏹'),
            telebot.types.KeyboardButton('→')
        )
        markup.add(telebot.types.KeyboardButton('↓'))
        
        bot.send_message(
            message.chat.id,
            f"Добро пожаловать в Cat Game, {message.from_user.username}! Используй кнопки для передвижения кота",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "Не удалось присоединиться к игре. Попробуйте ещё раз.")


@bot.message_handler(func=lambda message: True)
def handle_main_movement(message):

    direction_map = {
        '↑': 'up',
        '↓': 'down',
        '←': 'left',
        '→': 'right',
        '⏹': 'stop'
    }
    


    direction = direction_map.get(message.text)
    if direction:

        if direction == 'stop':

            bot.send_message(message.chat.id, "Ваш кот остановился.")
            return
            
        response = requests.post(
            f"{SERVER_URL}/api/move",
            json={
                'telegram_id': message.from_user.id,
                'direction': direction
            }
        )
        if  response.json().get('status') == 'success':
             bot.send_message(message.chat.id, f" Moving {direction}!")
        else:
           bot.send_message(message.chat.id, "Перемещение не удалось. Вы в игре? Попробуйте /join.")
    else:
         bot.send_message(message.chat.id, "Неизвестная команда. Используйте кнопки, чтобы управлять котом.")

def run_bot():
     while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f" Bot error : {e}")

            sleep(5)


if __name__ == '__main__':
    run_bot()