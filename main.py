import os
import telebot
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import requests
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)
memory = {}

@app.route('/')
def home():
    return "GhostMind Ultimate Pro is online!"

def run():
    app.run(host='0.0.0.0', port=8081)

Thread(target=run).start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    greeting = "Салом, Бобур!" if user_id not in memory else "Жонам, сизга қандай ёрдам бера оламан?"
    bot.send_message(user_id, greeting)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file = bot.download_file(file_info.file_path)
        ogg_audio = BytesIO(file)
        ogg_audio.name = "voice.ogg"

        audio = AudioSegment.from_ogg(ogg_audio)
        wav_audio = BytesIO()
        audio.export(wav_audio, format="wav")
        wav_audio.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_audio) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ru-RU')

        user_id = message.chat.id
        memory["last"] = text
        bot.send_message(user_id, f"Вы сказали: {text}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка распознавания: {e}")

@bot.message_handler(func=lambda msg: msg.text and msg.text.lower().startswith("переводи на"))
def translate_message(message):
    user_id = message.chat.id
    text = message.text.lower().split("на", 1)[1].strip()

    lang_map = {
        "узбекский": "uz",
        "русский": "ru",
        "английский": "en",
        "китайский": "zh-CN",
        "французский": "fr",
        "немецкий": "de",
        "испанский": "es",
        "таджикский": "tg",
        "татарский": "tt",
        "киргизский": "ky",
        "итальянский": "it"
    }

    if text not in lang_map:
        bot.send_message(user_id, "Язык не распознан")
        return

    try:
        translated = GoogleTranslator(source='auto', target=lang_map[text]).translate(memory.get("last", ""))
        bot.send_message(user_id, f"Перевод на {text}:\n{translated}")
    except Exception as e:
        bot.send_message(user_id, f"Ошибка перевода: {e}")

@bot.message_handler(func=lambda msg: True)
def handle_text_message(message):
    user_id = message.chat.id
    user_text = message.text.strip()
    memory["last"] = user_text

    bot.send_message(user_id, "Думаю...")

    reply = get_gpt_response(user_text)
    bot.send_message(user_id, reply)

    # Отправка голоса с чуть ускоренной скоростью речи
    tts = gTTS(text=reply, lang='ru', slow=False)
    voice_fp = BytesIO()
    tts.write_to_fp(voice_fp)
    voice_fp.seek(0)
    bot.send_voice(user_id, voice_fp)

def get_gpt_response(prompt):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.7,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Ошибка от OpenAI: {response.text}"

print("GhostMind Ultimate Pro запущен...")
bot.infinity_polling()
