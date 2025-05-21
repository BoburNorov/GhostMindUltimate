
import telebot
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_YOUR_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом, жонам! Мен Alfa ботман. 'Переводи на англ Салом дунё' деб ёзинг.")

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("переводи на"))
def translate_and_voice(message):
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Илтимос, тил ва матнни ёзинг. Масалан: 'переводи на англ салом'")
            return
        lang = parts[2].split()[0]
        text = " ".join(parts[2].split()[1:])
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        bot.send_message(message.chat.id, f"Таржима: {translated}")
        tts = gTTS(translated, lang=lang)
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove("voice.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"Хатолик: {str(e)}")

@bot.message_handler(func=lambda m: True)
def echo(message):
    try:
        tts = gTTS(message.text, lang="ru")
        tts.save("reply.mp3")
        with open("reply.mp3", "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove("reply.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"Хатолик: {str(e)}")

bot.polling(non_stop=True)
