# Other imports
import json
import requests

# Flask
from flask import Flask
from flask import request
from flask import jsonify

# Project imports
import config


app = Flask(__name__)


@app.route(f'/{config.TOKEN}', methods=['POST', 'GET'])
def get_new_message():
    if request.method == 'POST':
        JSON_result = request.get_json()
        message_handler(JSON_result)
        return jsonify(JSON_result)
    return 'Error'


@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'


def message_handler(JSON):
    chat_id = JSON['result'][0]['message']['chat']['id']

    URL = f'https://api.telegram.org/bot{config.TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': 'Hello, World!'
    }
    requests.post(URL, data=payload)


if __name__ == '__main__':
    app.run()
