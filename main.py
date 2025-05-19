import os
from flask import Flask
from threading import Thread
import telebot
import requests
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "GhostMind Ultimate is online!"

def run():
    app.run(host='0.0.0.0', port=8081)

Thread(target=run).start()

memory = {}

def get_gpt_response(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Кечирасиз, жонам. OpenAI'dан хатолик: " + response.text

def send_voice(chat_id, text):
    tts = gTTS(text=text, lang='ru', slow=False)
    voice = BytesIO()
    tts.write_to_fp(voice)
    voice.seek(0)
    bot.send_voice(chat_id, voice)

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "жонам"
    memory[message.chat.id] = {"name": name}
    bot.send_message(message.chat.id, f"Салом, {name}! Мен сунъий интеллектман. Савол беринг!")
    send_voice(message.chat.id, f"Салом, {name}! Мен тайёрман!")

@bot.message_handler(content_types=['voice'])
def voice_msg(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)
        ogg_path = "voice.ogg"
        wav_path = "voice.wav"
        with open(ogg_path, 'wb') as f:
            f.write(downloaded)
        sound = AudioSegment.from_ogg(ogg_path)
        sound.export(wav_path, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="ru-RU")
        bot.send_message(message.chat.id, f"Таниган овоз: {text}")
        reply = get_gpt_response(text)
        bot.send_message(message.chat.id, reply)
        send_voice(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Овозни таниб бўлмади: {str(e)}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.lower().strip()
    chat_id = message.chat.id

    if chat_id not in memory:
        memory[chat_id] = {"name": message.from_user.first_name or "жонам"}

    name = memory[chat_id]["name"]

    if text.startswith("переводи на"):
        try:
            lang_map = {
                "узбекский": "uz", "русский": "ru", "английский": "en",
                "китайский": "zh-cn", "французский": "fr", "немецкий": "de",
                "испанский": "es", "таджикский": "tg", "татарский": "tt",
                "итальянский": "it", "киргизский": "ky"
            }
            lang = text.split("на", 1)[1].strip()
            if lang not in lang_map:
                bot.send_message(chat_id, "Язык не распознан.")
                return
            last_text = memory[chat_id].get("last", "")
            translated = GoogleTranslator(source='auto', target=lang_map[lang]).translate(last_text)
            bot.send_message(chat_id, f"Перевод на {lang}: {translated}")
            send_voice(chat_id, translated)
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка перевода: {str(e)}")
    else:
        memory[chat_id]["last"] = text
        bot.send_message(chat_id, "Думаю...")
        reply = get_gpt_response(text)
        bot.send_message(chat_id, reply)
        send_voice(chat_id, reply)

print("GhostMind Ultimate запущен...")
bot.infinity_polling()
