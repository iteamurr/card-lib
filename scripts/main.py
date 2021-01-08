# -*- coding: utf-8 -*-
'''Program entry point.

The model receives messages from the Telegram
and passes further instructions to the bot.py module.
'''

# Other imports
import json

# Flask
from flask import Flask
from flask import request
from flask import jsonify

# Project imports
import bot


app = Flask(__name__)


with open('config.json') as config_json:
    config = json.load(config_json)
    token = config['telegram']['token']


@app.route(f'/{token}', methods=['POST', 'GET'])
def get_new_message():
    '''Receiving a message from a user using a webhook.
    '''

    if request.method == 'POST':
        json_result = request.get_json()

        save_message(json_result) # Debug
        bot_handler = bot.Handler()
        bot_handler.handler(json_result)

        return jsonify(json_result)
    return '<h1>Error!</h1>'


def save_message(json_result):
    '''Debug function.
    '''

    with open('message.json', 'w') as json_result_file:
        json.dump(json_result, json_result_file, indent=4)


if __name__ == '__main__':
    app.run()
