import telebot
from flask import Flask, request
from gtts import gTTS
from deep_translator import GoogleTranslator
import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
memory = {}

@app.route('/', methods=['GET'])
def index():
    return "GhostMind Ultimate is online!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

def get_crypto_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        data = requests.get(url).json()
        return float(data["price"])
    except:
        return None

def get_gold_price():
    try:
        data = requests.get("https://api.metals.live/v1/spot").json()
        for item in data:
            if "gold" in item:
                return item["gold"]
    except:
        return None

def send_voice(chat_id, text):
    tts = gTTS(text=text, lang="ru")
    tts.save("voice.ogg")
    with open("voice.ogg", "rb") as f:
        bot.send_voice(chat_id, f)

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    text = message.text.lower().strip()
    chat_id = message.chat.id
    if chat_id not in memory:
        memory[chat_id] = {"Ð¸Ð¼Ñ": message.chat.first_name}
    Ð¸Ð¼Ñ = memory[chat_id]["Ð¸Ð¼Ñ"]

    if text.startswith("Ð¿ÐµÑÐµÐ²Ð¾Ð´Ð¸ Ð½Ð°"):
        try:
            lang_map = {
                "ÑÐ·Ð±ÐµÐºÑÐºÐ¸Ð¹": "uz", "ÑÑÑÑÐºÐ¸Ð¹": "ru", "Ð°Ð½Ð³Ð»Ð¸Ð¹ÑÐºÐ¸Ð¹": "en",
                "ÐºÐ¸ÑÐ°Ð¹ÑÐºÐ¸Ð¹": "zh-cn", "ÑÑÐ°Ð½ÑÑÐ·ÑÐºÐ¸Ð¹": "fr", "Ð½ÐµÐ¼ÐµÑÐºÐ¸Ð¹": "de",
                "Ð¸ÑÐ¿Ð°Ð½ÑÐºÐ¸Ð¹": "es", "ÑÐ°Ð´Ð¶Ð¸ÐºÑÐºÐ¸Ð¹": "tg", "Ð¸ÑÐ°Ð»ÑÑÐ½ÑÐºÐ¸Ð¹": "it",
                "ÐºÐ¸ÑÐ³Ð¸Ð·ÑÐºÐ¸Ð¹": "ky", "ÑÐ°ÑÐ°ÑÑÐºÐ¸Ð¹": "tt"
            }
            lang = text.split("Ð½Ð°", 1)[1].strip()
            if lang not in lang_map:
                bot.send_message(chat_id, "Ð¯ Ð½Ðµ Ð·Ð½Ð°Ñ ÑÐ°ÐºÐ¾Ð¹ ÑÐ·ÑÐº.")
                return
            last = memory[chat_id].get("last", "")
            translated = GoogleTranslator(source='auto', target=lang_map[lang]).translate(last)
            bot.send_message(chat_id, f"ÐÐµÑÐµÐ²Ð¾Ð´ Ð½Ð° {lang}:
{translated}")
            send_voice(chat_id, translated)
        except Exception as e:
            bot.send_message(chat_id, f"ÐÑÐ¸Ð±ÐºÐ° Ð¿ÐµÑÐµÐ²Ð¾Ð´Ð°: {e}")
        return

    memory[chat_id]["last"] = text
    if "ÑÐµÐ½Ð° Ð±Ð¸ÑÐºÐ¾Ð¸Ð½Ð°" in text or "btc" in text:
        price = get_crypto_price("BTCUSDT")
        if price:
            bot.send_message(chat_id, f"Ð¦ÐµÐ½Ð° Ð±Ð¸ÑÐºÐ¾Ð¸Ð½Ð°: ${price}")
            send_voice(chat_id, f"Ð¦ÐµÐ½Ð° Ð±Ð¸ÑÐºÐ¾Ð¸Ð½Ð° {int(price)} Ð´Ð¾Ð»Ð»Ð°ÑÐ¾Ð²")
        else:
            bot.send_message(chat_id, "ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¿Ð¾Ð»ÑÑÐ¸ÑÑ ÑÐµÐ½Ñ BTC.")
    elif "ÑÐµÐ½Ð° Ð·Ð¾Ð»Ð¾ÑÐ°" in text or "gold" in text:
        price = get_gold_price()
        if price:
            bot.send_message(chat_id, f"Ð¦ÐµÐ½Ð° Ð·Ð¾Ð»Ð¾ÑÐ°: ${price}")
            send_voice(chat_id, f"Ð¦ÐµÐ½Ð° Ð·Ð¾Ð»Ð¾ÑÐ° {int(price)} Ð´Ð¾Ð»Ð»Ð°ÑÐ¾Ð²")
        else:
            bot.send_message(chat_id, "ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¿Ð¾Ð»ÑÑÐ¸ÑÑ ÑÐµÐ½Ñ Ð·Ð¾Ð»Ð¾ÑÐ°.")
    else:
        bot.send_message(chat_id, "ÐÑÐ¸Ð²ÐµÑ! ÐÐ°Ð¿Ð¸ÑÐ¸ Ð¼Ð½Ðµ ÑÐµÐºÑÑ Ð¸Ð»Ð¸ ÑÐ¿ÑÐ¾ÑÐ¸ ÑÐµÐ½Ñ BTC Ð¸Ð»Ð¸ Ð·Ð¾Ð»Ð¾ÑÐ°.")

if name == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://ghostmindultimate.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
