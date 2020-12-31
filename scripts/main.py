# Flask
from flask import Flask
from flask import request
from flask import jsonify

# Other imports
import json

# Project imports
import bot
import config

app = Flask(__name__)


@app.route(f'/{config.TOKEN}', methods=['POST', 'GET'])
def get_new_message():
    if request.method == 'POST':
        JSON_result = request.get_json()

        save_message(JSON_result) # Debug
        bot.message_handler(JSON_result)

        return jsonify(JSON_result)
    return '<h1>Error!</h1>'


def save_message(JSON):
    with open('message.json', 'w') as JSON_file:
        json.dump(JSON, JSON_file, indent=4)


if __name__ == '__main__':
    app.run()
