import os
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

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return "MindCode Ultimate AI is online", 200

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

def send_voice(chat_id, text):
    tts = gTTS(text=text, lang='ru', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    bot.send_voice(chat_id, fp)

def get_price(asset):
    try:
        if asset == "bitcoin":
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
            return f"Bitcoin: ${r['bitcoin']['usd']}"
        elif asset == "gold":
            r = requests.get("https://api.metals.live/v1/spot").json()
            for i in r:
                if "gold" in i:
                    return f"Gold: ${i['gold']}"
        return "Цены не найдены."
    except:
        return "Ошибка при получении цен."

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        img_data = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(img_data))
        text = pytesseract.image_to_string(image)
        bot.send_message(message.chat.id, f"Текст с изображения:\n{text}")
        send_voice(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки изображения: {e}")

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    try:
        bot.send_message(message.chat.id, "Слушаю, жонам...")
        file_info = bot.get_file(message.voice.file_id)
        audio_data = bot.download_file(file_info.file_path)
        ogg = BytesIO(audio_data)
        wav = BytesIO()
        sound = AudioSegment.from_ogg(ogg)
        sound.export(wav, format="wav")
        wav.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="ru-RU")
        bot.send_message(message.chat.id, f"Вы сказали: {text}")
        handle_command(message.chat.id, text)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка распознавания речи: {e}")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    handle_command(message.chat.id, message.text)

def handle_command(chat_id, text):
    lower = text.lower()
    if lower.startswith("переводи на"):
        try:
            lang = lower.split("на", 1)[1].strip()
            langs = {
                "узбекский": "uz", "русский": "ru", "английский": "en", "таджикский": "tg",
                "китайский": "zh-cn", "французский": "fr", "немецкий": "de", "итальянский": "it",
                "татарский": "tt", "киргизский": "ky", "испанский": "es"
            }
            code = langs.get(lang)
            if not code:
                return bot.send_message(chat_id, "Язык не распознан.")
            translated = GoogleTranslator(source='auto', target=code).translate(text)
            bot.send_message(chat_id, f"Перевод на {lang}:\n{translated}")
            send_voice(chat_id, translated)
        except:
            bot.send_message(chat_id, "Ошибка перевода.")
    elif "btc" in lower or "биткоин" in lower:
        price = get_price("bitcoin")
        bot.send_message(chat_id, price)
        send_voice(chat_id, price)
    elif "gold" in lower or "золото" in lower or "xau" in lower:
        price = get_price("gold")
        bot.send_message(chat_id, price)
        send_voice(chat_id, price)
    elif "привет" in lower or "салом" in lower:
        text = "Салом, жонам! Я MindCode Ultimate. Готов анализировать и помогать тебе!"
        bot.send_message(chat_id, text)
        send_voice(chat_id, text)
    elif "nonfarm" in lower or "новости" in lower:
        bot.send_message(chat_id, "Следующее событие NonFarm будет объявлено в ближайшую пятницу. Я дам сигнал заранее.")
    elif "совет" in lower or "что делать" in lower:
        bot.send_message(chat_id, "Совет: жди подтверждение объёма и не входи против тренда. Хочешь сигнал — пришли график.")
    else:
        bot.send_message(chat_id, f"Принято: {text}")
        send_voice(chat_id, text)

if name == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://ghostmindultimate.onrender.com/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
