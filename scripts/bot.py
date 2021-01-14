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

            if "entities" in message:
                self._message_handler(message)
            else:
                self._session_handler(message)

        elif "callback_query" in request:
            callback_query = request["callback_query"]
            self._callback_query_handler(callback_query)

    @staticmethod
    def _message_handler(message):
        message_text = message["text"]
        message_entities = message["entities"]

        chat_id = message["chat"]["id"]
        send_menu = SendMenu(chat_id)

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

        user_interaction = UserInteraction(chat_id, callback_id)
        switch_menu = SwitchMenu(chat_id, message_id, callback_id)

        if data == "private_office":
            switch_menu.private_office()

        elif "collection" in data:
            if data == "collections":
                switch_menu.collections()
            elif data == "add_collection":
                user_interaction.add_collection()

        elif data == "settings":
            switch_menu.settings()

        elif "locale" in data:
            if data == "locale_settings":
                switch_menu.locale_settings()
            else:
                user_interaction.change_locale(data)
                switch_menu.locale_settings()

    @staticmethod
    def _session_handler(message):
        message_text = message["text"]

        chat_id = message["chat"]["id"]
        user_interaction = UserInteraction(chat_id)

        with Select("bot_users") as select_session:
            session = select_session.user_attribute(chat_id, "session")

        if session[-2:] == "CL":
            user_interaction.new_collection(message_text)


class SendMenu:
    def __init__(self, chat_id):
        self._chat_id = chat_id

        with Select("bot_users") as select:
            self._user_locale = select.user_attribute(chat_id, "locale")

    def private_office(self):
        locale = self._user_locale

        with Select("bot_messages") as select_message:
            title = select_message.bot_message("private_office", locale)

        buttons = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        buttons = Tools.button_identifier(locale, buttons)

        url, structure = self._wrapper(title, buttons)
        requests.post(url, json=structure)

    def settings(self):
        with Select("bot_messages") as select_message:
            title = select_message.bot_message("settings", self._user_locale)

        buttons = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        buttons = Tools.button_identifier(self._user_locale, buttons)

        url, structure = self._wrapper(title, buttons)
        requests.post(url, json=structure)

    def _wrapper(self, title, buttons):
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
        locale = self._user_locale

        with Select("bot_messages") as select_message:
            title = select_message.bot_message("private_office", locale)

        buttons = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        buttons = Tools.button_identifier(locale, buttons)

        request, callback_request = self._wrapper(title, buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def settings(self):
        with Select("bot_messages") as select_message:
            title = select_message.bot_message("settings", self._user_locale)

        buttons = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        buttons = Tools.button_identifier(self._user_locale, buttons)

        request, callback_request = self._wrapper(title, buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def locale_settings(self):
        locale = self._user_locale

        with Select("bot_messages") as select_message:
            title = select_message.bot_message("current_language", locale)

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

        buttons = Tools.button_identifier(locale, buttons)

        request, callback_request = self._wrapper(title, buttons)
        url, structure = request
        callback_url, callback_answer = callback_request

        locales = {"en": "English", "ru": "Русский"}[locale]
        structure["text"] = structure["text"].format(locales)

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def collections(self):
        locale = self._user_locale

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self._chat_id)

        with Select("bot_messages") as select_message:
            title = select_message.bot_message("collections", locale)

        buttons = [
            [
                ["add_collection", "add_collection"],
                ["back", "private_office"]
            ]
        ]

        collections = Tools.keyboard_creator(collections_list)
        buttons = Tools.button_identifier(locale, buttons)
        keyboard = collections + buttons

        request, callback_request = self._wrapper(title, keyboard)
        url, structure = request
        callback_url, callback_answer = callback_request

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def _wrapper(self, title, keyboard):
        callback = self._callback_id

        url, head = API.edit_message(self._chat_id, self._message_id, title)
        callback_url, callback_answer = API.answer_callback_query(callback)

        inline_keyboard = API.inline_keyboard(*keyboard)
        structure = {**head, **inline_keyboard}

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

    def add_collection(self):
        locale = self._user_locale
        callback = self._callback_id
        key = Tools.new_collection_key()

        with Update("bot_users") as update_session:
            update_session.user_attribute(self._chat_id, "session", key)

        with Select("bot_messages") as select_message:
            text = select_message.bot_message("create_collection", locale)

        url, structure = API.send_message(self._chat_id, text)
        callback_url, callback_answer = API.answer_callback_query(callback)

        requests.post(url, json=structure)
        requests.post(callback_url, json=callback_answer)

    def new_collection(self, collection_name):
        user_id = self._chat_id
        locale = self._user_locale

        with Select("bot_users") as select:
            key = select.user_attribute(user_id, "session")
            collections = select.user_attribute(user_id, "collections")

        with Insert("bot_collections") as insert_collection:
            insert_collection.new_collection(user_id, key, collection_name)

        with Update("bot_users") as update:
            update.user_attribute(user_id, "session", None)
            update.user_attribute(user_id, "collections", collections + 1)

        with Select("bot_messages") as select_message:
            text = select_message.bot_message("new_collection", locale)

        url, structure = API.send_message(user_id, text)
        requests.post(url, json=structure)
