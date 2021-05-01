"""
    Bot launch module.
"""
from flask import Flask, request, jsonify

from .bot.config import TELEGRAM_TOKEN
from .bot.tools.handlers import CommandHandler
from .bot.tools.handlers import SessionHandler
from .bot.tools.handlers import CallbackQueryHandler
from .bot.tools.settings import SettingsPanel

SettingsPanel.first_launch_of_bot()
SettingsPanel.ru_insert_messages()
SettingsPanel.en_insert_messages()
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST", "GET"])
def get_updates():
    """Get user action.
    """
    if request.method == "POST":
        updates = request.get_json()

        if "message" in updates:
            message = updates["message"]

            if ("entities" in message and
                    message["entities"][0]["type"] == "bot_command"):
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
