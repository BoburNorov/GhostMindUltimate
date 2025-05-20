
from threading import Thread
import os
from dotenv import load_dotenv
import requests
from flask import Flask, request
import telebot
from gtts import gTTS
from io import BytesIO
from deep_translator import GoogleTranslator
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN is missing from .env")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
memory = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "GhostMind Ultimate Pro is online!", 200

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return '!', 200

def send_voice(chat_id, text):
    tts = gTTS(text=text, lang='ru', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    bot.send_voice(chat_id, fp)

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    text = message.text.lower().strip()
    chat_id = message.chat.id

    if chat_id not in memory:
        memory[chat_id] = {"context": ""}

    if "bitcoin" in text or "btc" in text:
        price = get_price("bitcoin")
        bot.send_message(chat_id, f"BTC: {price}")
        send_voice(chat_id, f"Цена биткоина: {price}")

    elif "gold" in text or "xau" in text:
        price = get_price("gold")
        bot.send_message(chat_id, f"Gold: {price}")
        send_voice(chat_id, f"Цена золота: {price}")

    elif "привет" in text or "салом" in text:
        answer = "Салом, жонам! Я GhostMind Ultimate Pro. Готов анализировать рынок!"
        bot.send_message(chat_id, answer)
        send_voice(chat_id, answer)

    elif "nonfarm" in text or "новости" in text:
        msg = "Следующее событие NonFarm будет в ближайшую пятницу. Я дам сигнал заранее."
        bot.send_message(chat_id, msg)
        send_voice(chat_id, msg)

    elif "совет" in text or "что делать" in text:
        msg = "Совет: жди подтверждение объема и не входи против тренда."
        bot.send_message(chat_id, msg)
        send_voice(chat_id, msg)

    else:
        reply = f"Принято: {text}"
        bot.send_message(chat_id, reply)
        send_voice(chat_id, reply)

def get_price(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url).json()
        return r[coin]['usd']
    except:
        return "ошибка получения цены"

def run():
    app.run(host='0.0.0.0', port=8081)

Thread(target=run).start()
