# bot.py
import telebot
from telebot import types
from pdf_utils import get_pdf_data, compare_pdf_data
from config import TOKEN
from flask import Flask
from threading import Thread
 
# 1. Заглушка для Render, чтобы он не выключал бота
app = Flask('')
@app.route('/')
def home():
    return "Бот работает!"
 
def run_web():
    app.run(host='0.0.0.0', port=8080)
 
# Запускаем веб-сервер в отдельном потоке
t = Thread(target=run_web)
t.start()
 
# 2. Основной код бота
bot = telebot.TeleBot(TOKEN)
MY_ID = 1041292897 
 
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.from_user.id == MY_ID:
        bot.send_message(message.chat.id, "Привет! Я бот для проверки чеков.\nНажмите 'Проверить чек', чтобы начать.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Проверить чек")
        markup.add(item1)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Извините, этот бот только для владельца.")
 
@bot.message_handler(func=lambda message: message.text == "Проверить чек")
def check_receipt(message):
    if message.from_user.id == MY_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Сбербанк")
        item2 = types.KeyboardButton("Т-Банк")
        markup.add(item1, item2)
        bot.send_message(message.chat.id, "Выберите банк:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа.")
 
@bot.message_handler(func=lambda message: message.text in ["Сбербанк", "Т-Банк"])
def receive_file(message):
    if message.from_user.id == MY_ID:
        bank = message.text
        bot.send_message(message.chat.id, "Отправьте PDF файл чека:")
        bot.register_next_step_handler(message, handle_pdf_file, bank)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа.")
 
def handle_pdf_file(message, bank):
    if message.from_user.id != MY_ID:
        return
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
 
        with open("received_receipt.pdf", 'wb') as f:
            f.write(downloaded_file)
 
        pdf_data = get_pdf_data("received_receipt.pdf")
        result = compare_pdf_data(bank, pdf_data)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте именно PDF файл.")
 
if __name__ == '__main__':
    bot.polling(none_stop=True)
