
# GhostMind Ultimate - main.py (v1)
from flask import Flask, request
import telebot
import os
from dotenv import load_dotenv
from gtts import gTTS
from deep_translator import GoogleTranslator
import time
import requests

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Салом, жонам! GhostMind Ultimate хизматига хуш келибсан.")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("переводи на "))
def translate_text(message):
    lang = message.text.lower().replace("переводи на ", "").strip()
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.reply_to_message.text)
        bot.send_message(message.chat.id, f"Таржима ({lang}):\n{translated}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Хатолик: {str(e)}")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_voice(message):
    tts = gTTS(message.text, lang='ru')
    filename = f"voice_{int(time.time())}.mp3"
    tts.save(filename)
    with open(filename, 'rb') as audio:
        bot.send_voice(message.chat.id, audio)
    os.remove(filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
