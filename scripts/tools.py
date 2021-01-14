# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import random
import string
from math import ceil

from database import Select, Insert


class API:
    @staticmethod
    def send_message(chat_id, text, parse_mode=None):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        api_url = telegram_url.format(token=token, command="sendMessage")
        if parse_mode:
            json_response = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
        else:
            json_response = {
                "chat_id": chat_id,
                "text": text
            }

        return api_url, json_response

    @staticmethod
    def edit_message(chat_id, message_id, text, parse_mode=None):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        api_url = telegram_url.format(token=token, command="editMessageText")
        if parse_mode:
            json_response = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode
            }
        else:
            json_response = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text
            }

        return api_url, json_response

    @staticmethod
    def answer_callback_query(callback_query_id, text=None, show_alert=False):
        with open("config.json") as config_json:
            config = json.load(config_json)
            token = config["telegram"]["token"]
            telegram_url = config["telegram"]["url"]

        command = "answerCallbackQuery"
        api_url = telegram_url.format(token=token, command=command)
        if text:
            json_response = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert
            }
        else:
            json_response = {"callback_query_id": callback_query_id}

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
            user_existence = select_user.user_attribute(chat_id, "locale")

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

    @staticmethod
    def new_collection_key():
        first_part = random.randrange(100000000, 1000000000)
        second_part = random.randrange(1000000000, 10000000000)
        third_part = random.choice(string.ascii_letters)

        key = f"K-{first_part}-{second_part}-{third_part}-00000-CL"

        return key

    @staticmethod
    def keyboard_creator(collections, buttons_in_layer=2):
        buttons = []
        collection_length = len(collections)

        for layer in range(ceil(collection_length/buttons_in_layer)):
            buttons.append([])
            left_border = buttons_in_layer*layer
            right_border = buttons_in_layer*(layer+1)

            for collection in collections[left_border:right_border]:
                collection_data = collection[2]
                collection_name = collection[3]
                button_data = [collection_name, collection_data]

                buttons[layer].append(button_data)

        return buttons

    @staticmethod
    def button_identifier(locale, buttons):
        with Select("bot_messages") as select_message:
            for button in buttons:
                for data in button:
                    data[0] = select_message.bot_message(data[0], locale)

        return buttons
