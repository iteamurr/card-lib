# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import requests

from tools import API, Tools
from database import Select, Update


class Handler:
    def handler(self, request):
        if "message" in request:
            message = request["message"]
            self._message_handler(message)

        elif "callback_query" in request:
            callback_query = request["callback_query"]
            self._callback_query_handler(callback_query)

    @staticmethod
    def _message_handler(message):
        chat_id = message["chat"]["id"]
        message_text = message["text"]

        send_menu = SendMenu(chat_id)
        if "entities" in message:
            message_entities = message["entities"]

            if message_entities[0]["type"] == "bot_command":
                if "/start" in message_text:
                    Tools.check_new_user(message)
                    send_menu.private_office()
                elif "/settings" in message_text:
                    send_menu.settings()

    @staticmethod
    def _callback_query_handler(callback_query):
        data = callback_query["data"]

        callback_id = callback_query["id"]
        chat_id = callback_query["from"]["id"]
        message_id = callback_query["message"]["message_id"]

        switch_menu = SwitchMenu(chat_id, message_id, callback_id)
        if data == "settings":
            switch_menu.settings()
        elif data == "private_office":
            switch_menu.private_office()
        elif "locale" in data:
            if data == "locale_settings":
                switch_menu.locale_settings()
            else:
                switch_menu.change_locale(data)


class SendMenu:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def private_office(self):
        buttons = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        url, structure = self._wrapper("private_office", buttons)
        requests.post(url, json=structure)

    def settings(self):
        buttons = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        url, structure = self._wrapper("settings", buttons)
        requests.post(url, json=structure)

    def _wrapper(self, menu_name, buttons):
        with Select("bot_users") as select_locale:
            locale = select_locale.user_attributes(self.chat_id)[3]

        with Select("bot_messages") as select_message:
            title = select_message.bot_message(menu_name, locale)

            for button in buttons:
                for data in button:
                    data[0] = select_message.bot_message(data[0], locale)

        url, head = API.send_message(self.chat_id, title)
        keyboard = API.inline_keyboard(*buttons)
        structure = {**head, **keyboard}

        return url, structure


class SwitchMenu:
    def __init__(self, chat_id, message_id, callback_id):
        self.chat_id = chat_id
        self.message_id = message_id
        self.callback_id = callback_id

    def private_office(self):
        buttons = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        request, callback_request = self._wrapper("private_office", buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def settings(self):
        buttons = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        request, callback_request = self._wrapper("settings", buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def locale_settings(self):
        buttons = [
            [
                ["change_language_to_en", "en_locale"],
                ["change_language_to_ru", "ru_locale"]
            ],
            [
                ["main", "private_office"],
                ["back", "settings"]
            ]
        ]

        request, callback_request = self._wrapper("current_language", buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        with Select("bot_users") as select_locale:
            user_locale = select_locale.user_attributes(self.chat_id)[3]

        locales = {"en": "English", "ru": "Русский"}
        structure["text"] = structure["text"].format(locales[user_locale])

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def change_locale(self, data):
        with Update("bot_users") as update_locale:
            update_locale.user_attribute(self.chat_id, "locale", data[:2])

        self.locale_settings()

    def _wrapper(self, menu_name, buttons):
        with Select("bot_users") as select_locale:
            locale = select_locale.user_attributes(self.chat_id)[3]

        with Select("bot_messages") as select_message:
            title = select_message.bot_message(menu_name, locale)

            for button in buttons:
                for data in button:
                    data[0] = select_message.bot_message(data[0], locale)

        url, head = API.edit_message(self.chat_id, self.message_id, title)
        keyboard = API.inline_keyboard(*buttons)
        structure = {**head, **keyboard}

        callback_url, callback_answer = API.answer_callback_query(
            callback_query_id=self.callback_id)

        return (url, structure), (callback_url, callback_answer)
