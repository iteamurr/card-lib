# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import re
import json
import random
import string
from math import ceil

from database import Select, Insert


class API:
    def __init__(self):
        with open("config.json") as config_json:
            config = json.load(config_json)
            self._token = config["telegram"]["token"]
            self._url = config["telegram"]["url"]

    def send_message(self, chat_id, text, parse_mode=None):
        request = {"url": "", "body": {}}
        request["url"] = self._url.format(self._token, "sendMessage")

        request["body"] = {"chat_id": chat_id, "text": text}
        if parse_mode:
            request["body"]["parse_mode"] = parse_mode

        return request

    def edit_message(self, chat_id, message_id, text, parse_mode=None):
        request = {"url": "", "body": {}}
        request["url"] = self._url.format(self._token, "editMessageText")

        request["body"] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if parse_mode:
            request["body"]["parse_mode"] = parse_mode

        return request

    def answer_callback_query(
            self, callback_query_id,
            text=None, show_alert=False):
        request = {"url": "", "body": {}}
        request["url"] = self._url.format(self._token, "answerCallbackQuery")

        request["body"] = {"callback_query_id": callback_query_id}
        if text:
            request["body"]["text"] = text
            request["body"]["show_alert"] = show_alert

        return request

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

        return f"K-{first_part}-{second_part}-{third_part}-00000-CL"

    @staticmethod
    def keyboard_creator(collections, buttons_in_layer=2):
        buttons = []
        collection_length = len(collections)
        layers = ceil(collection_length/buttons_in_layer)

        for layer in range(layers):
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
    def button_identifier(buttons, locale="en"):
        with Select("bot_messages") as select_button_title:
            for button in buttons:
                for data in button:
                    data[0] = select_button_title.bot_message(data[0], locale)

        return buttons

    @staticmethod
    def navigation_creator(
            number_of_items, level=0,
            items_in_page=8, number_of_navigation_buttons=5):
        pages = (number_of_items//items_in_page
                 + bool(number_of_items%items_in_page))

        buttons = [[]]
        if number_of_items < number_of_navigation_buttons*items_in_page + 1:
            for button in range(pages):
                page_state = ["• {} •", "{}"][button != level]

                button_name = page_state.format(button + 1)
                button_data = f"level_{'0'*(1 - button//10)}{button}"
                buttons[0].append([button_name, button_data])

        else:
            for button in range(number_of_navigation_buttons):
                if level in (0, 1):
                    navigation = ["{}", "{}", "{}", "{} ›", "{} »"]
                    navigation[level] = "• {} •"

                    data = pages if button == 4 else button + 1

                elif level in (pages - 1, pages - 2):
                    navigation = ["« {}", "‹ {}", "{}", "{}", "{}"]
                    navigation[level - pages + 5] = "• {} •"

                    if button:
                        data = pages + button - 4
                    else:
                        data = button + 1

                else:
                    navigation = ["« {}", "‹ {}", "• {} •", "{} ›", "{} »"]

                    if button:
                        if button == 4:
                            data = pages
                        else:
                            data = button + level - 1
                    else:
                        data = 1

                button_name = navigation[button].format(data)
                button_data = f"level_{'0'*(1 - data//10)}{data - 1}"
                buttons[0].append([button_name, button_data])

        return buttons

    @staticmethod
    def get_key_from_string(text):
        return re.search(r"(K-\d+-\d+-\w-\d+-CL)", text)[0]
