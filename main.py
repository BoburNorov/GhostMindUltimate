from flask import Flask, request
import telebot
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import requests
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
memory = {}
def get_market_data():
    try:
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        gold = requests.get("https://api.metals.live/v1/spot").json()
        btc_price = btc["bitcoin"]["usd"]
        gold_price = gold[0]["gold"]
        return f"Bitcoin: ${btc_price:,}\nGold: ${gold_price:,}"
    except Exception as e:
        return f"Error getting market data: {str(e)}"
def send_voice(chat_id, text):
    tts = gTTS(text=text, lang='ru', slow=False)
    voice_fp = BytesIO()
    tts.write_to_fp(voice_fp)
    voice_fp.seek(0)
    bot.send_voice(chat_id, voice_fp)
@app.route('/', methods=['GET'])
def index():
    return "GhostMind Ultimate Webhook is running!"
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid content type', 403
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    chat_id = message.chat.id
    memory[chat_id] = {"name": name}
    greeting = f"Ð¡Ð°Ð»Ð¾Ð¼, {name}! Ð¯ GhostMind Ultimate. ÐÐ°Ð¿Ð¸ÑÐ¸ Â«ÑÐµÐ½Ð°Â» ÑÑÐ¾Ð±Ñ Ð¿Ð¾Ð»ÑÑÐ¸ÑÑ Ð°Ð½Ð°Ð»Ð¸Ð· BTC Ð¸ Ð·Ð¾Ð»Ð¾ÑÐ°."
    bot.send_message(chat_id, greeting)
    send_voice(chat_id, greeting)
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.lower().strip()
    memory[chat_id] = memory.get(chat_id, {})
    memory[chat_id]["last"] = text
    if text.startswith("Ð¿ÐµÑÐµÐ²Ð¾Ð´Ð¸ Ð½Ð°"):
        try:
            lang_map = {
                "ÑÐ·Ð±ÐµÐºÑÐºÐ¸Ð¹": "uz",
                "ÑÑÑÑÐºÐ¸Ð¹": "ru",
                "Ð°Ð½Ð³Ð»Ð¸Ð¹ÑÐºÐ¸Ð¹": "en",
                "ÐºÐ¸ÑÐ°Ð¹ÑÐºÐ¸Ð¹": "zh-cn",
                "ÑÑÐ°Ð½ÑÑÐ·ÑÐºÐ¸Ð¹": "fr",
                "Ð½ÐµÐ¼ÐµÑÐºÐ¸Ð¹": "de",
                "Ð¸ÑÐ¿Ð°Ð½ÑÐºÐ¸Ð¹": "es",
                "ÑÐ°Ð´Ð¶Ð¸ÐºÑÐºÐ¸Ð¹": "tg",
                "Ð¸ÑÐ°Ð»ÑÑÐ½ÑÐºÐ¸Ð¹": "it",
                "ÐºÐ¸ÑÐ³Ð¸Ð·ÑÐºÐ¸Ð¹": "ky",
                "ÑÐ°ÑÐ°ÑÑÐºÐ¸Ð¹": "tt"
            }
            target_lang = text.split("Ð½Ð°", 1)[1].strip()
            if target_lang not in lang_map:
                bot.send_message(chat_id, "Ð¯Ð·ÑÐº Ð½Ðµ ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð½.")
                return
            last_text = memory[chat_id].get("last", "")
            translated = GoogleTranslator(source='auto', target=lang_map[target_lang]).translate(last_text)
            bot.send_message(chat_id, f"ÐÐµÑÐµÐ²Ð¾Ð´ Ð½Ð° {target_lang}: {translated}")
            send_voice(chat_id, translated)
        except Exception as e:
            bot.send_message(chat_id, f"ÐÑÐ¸Ð±ÐºÐ° Ð¿ÐµÑÐµÐ²Ð¾Ð´Ð°: {str(e)}")
    elif "ÑÐµÐ½Ð°" in text or "ÑÑÐ½Ð¾Ðº" in text:
        market = get_market_data()
        bot.send_message(chat_id, market)
        send_voice(chat_id, market)
    else:
        reply = f"Ð¢Ñ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»: {text}"
        bot.send_message(chat_id, reply)
        send_voice(chat_id, reply)
# Ð£ÑÑÐ°Ð½Ð¾Ð²ÐºÐ° Webhook Ð¿ÑÐ¸ Ð·Ð°Ð¿ÑÑÐºÐµ
WEBHOOK_URL = "https://ghostmindultimate.onrender.com/webhook"
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)
