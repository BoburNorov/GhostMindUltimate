# main.py - основной файл бота

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'GhostMind Ultimate is online!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)