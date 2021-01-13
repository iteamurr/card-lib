# pylint: disable=import-error
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import requests

from tools import API, Tools
from database import Select, Insert, Update


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
        user_interaction = UserInteraction(chat_id)
        if "entities" in message:
            message_entities = message["entities"]

            if message_entities[0]["type"] == "bot_command":
                if "/start" in message_text:
                    Tools.check_new_user(message)
                    send_menu.private_office()
                elif "/settings" in message_text:
                    send_menu.settings()
        else:
            user_interaction.new_collection(message_text)

    @staticmethod
    def _callback_query_handler(callback_query):
        data = callback_query["data"]

        callback_id = callback_query["id"]
        chat_id = callback_query["from"]["id"]
        message_id = callback_query["message"]["message_id"]

        user_interaction = UserInteraction(chat_id, callback_id)
        switch_menu = SwitchMenu(chat_id, message_id, callback_id)
        if data == "private_office":
            switch_menu.private_office()
        elif "collection" in data:
            if data == "collections":
                switch_menu.collections()
            elif data == "add_collection":
                user_interaction.create_collection()
        elif data == "settings":
            switch_menu.settings()
        elif "locale" in data:
            if data == "locale_settings":
                switch_menu.locale_settings()
            else:
                user_interaction.change_locale(data)
                switch_menu.locale_settings()


class SendMenu:
    def __init__(self, chat_id):
        self._chat_id = chat_id

        with Select("bot_users") as select:
            self._user_locale = select.user_attribute(chat_id, "locale")

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
        with Select("bot_messages") as select_message:
            title = select_message.bot_message(menu_name, self._user_locale)

            for button in buttons:
                for data in button:
                    locale = self._user_locale
                    data[0] = select_message.bot_message(data[0], locale)

        url, head = API.send_message(self._chat_id, title)
        keyboard = API.inline_keyboard(*buttons)
        structure = {**head, **keyboard}

        return url, structure


class SwitchMenu:
    def __init__(self, chat_id, message_id, callback_id):
        self._chat_id = chat_id
        self._message_id = message_id
        self._callback_id = callback_id

        with Select("bot_users") as select:
            self._user_locale = select.user_attribute(chat_id, "locale")

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

        locale = {"en": "English", "ru": "Русский"}[self._user_locale]
        structure["text"] = structure["text"].format(locale)

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def collections(self):
        with Select("bot_collections") as select:
            collections = select.user_collections(self._chat_id)

        buttons = [
            [
                ["add_collection", "add_collection"],
                ["back", "private_office"]
            ]
        ]

        request, callback_request = self._wrapper("collections", buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def _wrapper(self, menu_name, buttons):
        with Select("bot_messages") as select_message:
            title = select_message.bot_message(menu_name, self._user_locale)

            for button in buttons:
                for data in button:
                    locale = self._user_locale
                    data[0] = select_message.bot_message(data[0], locale)

        url, head = API.edit_message(self._chat_id, self._message_id, title)
        keyboard = API.inline_keyboard(*buttons)
        structure = {**head, **keyboard}

        callback_url, callback_answer = API.answer_callback_query(
            callback_query_id=self._callback_id)

        return (url, structure), (callback_url, callback_answer)


class UserInteraction:
    def __init__(self, chat_id, callback_id=None):
        self._chat_id = chat_id
        self._callback_id = callback_id

        with Select("bot_users") as select:
            self._user_locale = select.user_attribute(chat_id, "locale")

    def change_locale(self, data):
        with Update("bot_users") as update_locale:
            update_locale.user_attribute(self._chat_id, "locale", data[:2])

    def create_collection(self):
        key = Tools.new_collection_key()
        with Update("bot_users") as update_session:
            update_session.user_attribute(self._chat_id, "session", key)

        with Select("bot_messages") as select_message:
            locale = self._user_locale
            text = select_message.bot_message("create_collection", locale)

        url, structure = API.send_message(self._chat_id, text)
        callback_url, callback_answer = API.answer_callback_query(
            callback_query_id=self._callback_id)
        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def new_collection(self, collection_name):
        user_id = self._chat_id
        with Select("bot_users") as select_collection_key:
            key = select_collection_key.user_attribute(user_id, "session")

        with Insert("bot_collections") as insert_collection:
            insert_collection.new_collection(user_id, key, collection_name)

        with Select("bot_messages") as select_message:
            locale = self._user_locale
            text = select_message.bot_message("new_collection", locale)

        url, structure = API.send_message(self._chat_id, text)
        requests.post(url, json=structure)
