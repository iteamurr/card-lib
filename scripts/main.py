# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import json

from flask import Flask
from flask import request
from flask import jsonify

import bot


app = Flask(__name__)


with open("config.json") as config_json:
    config = json.load(config_json)
    token = config["telegram"]["token"]


@app.route(f"/{token}", methods=["POST", "GET"])
def get_new_message():
    if request.method == "POST":
        json_result = request.get_json()

        save_message(json_result) # Debug
        bot_handler = bot.Handler()
        bot_handler.handler(json_result)

        return jsonify(json_result)
    return "<h1>Error!</h1>"


def save_message(json_result):
    with open("message.json", "w") as json_result_file:
        json.dump(json_result, json_result_file, indent=4)


if __name__ == "__main__":
    app.run()
