import telebot
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
from telebot import types

# Token from environment or directly
TOKEN = os.getenv("TELEGRAM_TOKEN", "7863175057:AAG0Ow55iLDXjMMyOvQKLutKgcqueDyCLgw")
bot = telebot.TeleBot(TOKEN)

# /start handler
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салом, жонам! Мен тайёрман. Бирор сўз юборинг ёки 'переводи на [til]' деб ёзинг.")

# Таржима буйруғи
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("переводи на"))
def translate_command(message):
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Илтимос, таржима қилинадиган сўзни ҳам ёзинг.")
            return
        target_lang = parts[2].split()[0]
        text_to_translate = " ".join(parts[2].split()[1:])
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text_to_translate)
        bot.send_message(message.chat.id, f"Таржима ({target_lang}): {translated}")
        # Генерация аудио
        tts = gTTS(translated, lang=target_lang)
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove("voice.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"Хатолик: {str(e)}")

# Оддий текстни қайта гапириш
@bot.message_handler(content_types=['text'])
def echo_text(message):
    try:
        tts = gTTS(message.text, lang="ru")
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove("voice.mp3")
    except Exception as e:
        bot.send_message(message.chat.id, f"Хатолик: {str(e)}")

# Run the bot in polling mode
bot.polling(non_stop=True)
