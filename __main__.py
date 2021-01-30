"""
    Bot launch module.
"""

from flask import Flask
from flask import request
from flask import jsonify

from scripts.bot import BotHandler
from scripts.config import telegram


app = Flask(__name__)

@app.route(f"/{telegram['token']}", methods=["POST", "GET"])
def get_updates():
    """Get user action.
    """

    if request.method == "POST":
        updates = request.get_json()

        message = None
        if "message" in updates:
            message = updates["message"]

        callback_query = None
        if "callback_query" in updates:
            callback_query = updates["callback_query"]

        handler = BotHandler(message, callback_query)

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
