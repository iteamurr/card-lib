"""
    Bot launch module.
"""

from flask import Flask
from flask import request
from flask import jsonify

from .config import telegram
from .tools.handlers import CommandHandler
from .tools.handlers import SessionHandler
from .tools.handlers import CallbackQueryHandler


app = Flask(__name__)

@app.route(f"/{telegram['token']}", methods=["POST", "GET"])
def get_updates():
    """Get user action.
    """

    if request.method == "POST":
        updates = request.get_json()

        if "message" in updates:
            message = updates["message"]

            if "entities" in message:
                command_handler = CommandHandler(message)
                command_handler.handler()
            else:
                session_handler = SessionHandler(message)
                session_handler.handler()

        elif "callback_query" in updates:
            callback_query = updates["callback_query"]

            callback_query_handler = CallbackQueryHandler(callback_query)
            callback_query_handler.handler()

        return jsonify(updates)
    return "<h1>Error!</h1>"

if __name__ == "__main__":
    app.run()
