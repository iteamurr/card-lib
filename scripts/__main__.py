"""
    Bot launch module.
"""
from flask import Flask
from flask import request
from flask import jsonify

from . import bot
from .config import telegram


app = Flask(__name__)

@app.route(f"/{telegram['token']}", methods=["POST", "GET"])
def get_updates():
    """Getting user action.
    """
    if request.method == "POST":
        updates = request.get_json()

        message = updates["message"]
        callback_query = updates["callback_query"]
        handler = bot.Handler(message, callback_query)

        if "message" in updates:
            if "entities" in message:
                handler.message_handler()
            else:
                handler.session_handler()

        elif "callback_query" in updates:
            handler.callback_query_handler()

        return jsonify(updates)
    return "<h1>Error!</h1>"

if __name__ == "__main__":
    app.run()
