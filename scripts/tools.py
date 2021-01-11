# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json

from database import Select, Insert


class API:
    @staticmethod
    def send_message(chat_id, text, parse_mode="MarkdownV2"):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        api_url = telegram_url.format(token=token, command="sendMessage")
        json_response = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        return api_url, json_response

    @staticmethod
    def edit_message(chat_id, message_id, text, parse_mode="MarkdownV2"):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        api_url = telegram_url.format(token=token, command="editMessageText")
        json_response = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }

        return api_url, json_response

    @staticmethod
    def answer_callback_query(callback_query_id, text=None, show_alert=False):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        api_url = telegram_url.format(
            token=token, command="answerCallbackQuery")

        if not text:
            json_response = {
                "callback_query_id": callback_query_id
            }
        else:
            json_response = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert
            }

        return api_url, json_response

    @staticmethod
    def inline_keyboard(*button_data_list):
        keyboard = {
            "reply_markup":{
                "inline_keyboard":[
                ]
            }
        }

        button_index = 0
        inline_keyboard = keyboard["reply_markup"]["inline_keyboard"]
        for button_data in button_data_list:
            inline_keyboard.append([])

            for button_text, callback_data in button_data:
                button = {"text": button_text, "callback_data": callback_data}
                inline_keyboard[button_index].append(button)

            button_index += 1

        return keyboard


class Tools:
    @staticmethod
    def check_new_user(message):
        chat_id = message["chat"]["id"]
        with Select("bot_users") as select_user:
            user_existence = select_user.user_attributes(chat_id)

        if not user_existence:
            menu_id = message["message_id"]
            username = message["from"]["username"]
            locale = message["from"]["language_code"]
            user_locale = locale if locale in ["en", "ru"] else "en"

            with Insert("bot_users") as db_insert:
                db_insert.new_user(
                    user_id=chat_id, username=username,
                    locale=user_locale, menu_id=menu_id
                )
