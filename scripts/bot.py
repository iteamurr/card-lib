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
        chat_id = message["chat"]["id"]
        message_entities = message["entities"]

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

        with Select("bot_users") as select_session:
            session = select_session.user_attribute(chat_id, "session")

        user_interaction = UserInteraction(chat_id)
        if session[-2:] == "CL":
            user_interaction.new_collection(message_text)


class SendMenu:
    def __init__(self, chat_id):
        self._chat_id = chat_id

    def private_office(self):
        user_id = self._chat_id
        template = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        request = self._wrapper(title, buttons)

        requests.post(request["url"], json=request["body"])

    def settings(self):
        user_id = self._chat_id
        template = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        request = self._wrapper(title, buttons)

        requests.post(request["url"], json=request["body"])

    def _wrapper(self, title, buttons):
        api = API()
        request = api.send_message(self._chat_id, title)
        keyboard = API.inline_keyboard(*buttons)
        request["body"] = {**request["body"], **keyboard}

        return request


class SwitchMenu:
    def __init__(self, chat_id, message_id, callback_id):
        self._chat_id = chat_id
        self._message_id = message_id
        self._callback_id = callback_id

    def private_office(self):
        user_id = self._chat_id
        template = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        request, callback = self._wrapper(title, buttons)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])

    def settings(self):
        user_id = self._chat_id
        template = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        request, callback = self._wrapper(title, buttons)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])

    def locale_settings(self):
        user_id = self._chat_id
        template = [
            [
                ["change_language_to_en", "en_locale"],
                ["change_language_to_ru", "ru_locale"]
            ],
            [
                ["main", "private_office"],
                ["back", "settings"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("current_language", locale)

        buttons = Tools.button_identifier(template, locale)
        request, callback = self._wrapper(title, buttons)

        locales = {"en": "English", "ru": "Русский"}[locale]
        request["body"]["text"] = request["body"]["text"].format(locales)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])

    def collections(self):
        user_id = self._chat_id
        template = [
            [
                ["add_collection", "add_collection"],
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Select("bot_messages") as select_menu_title:
            title = select_menu_title.bot_message("collections", locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(user_id)

        collections = Tools.keyboard_creator(collections_list)
        buttons = Tools.button_identifier(template, locale)
        request, callback = self._wrapper(title, collections + buttons)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])

    def _wrapper(self, title, buttons):
        user_id = self._chat_id
        message_id = self._message_id
        callback_id = self._callback_id

        api = API()
        request = api.edit_message(user_id, message_id, title)
        callback = api.answer_callback_query(callback_id)

        keyboard = API.inline_keyboard(*buttons)
        request["body"] = {**request["body"], **keyboard}

        return request, callback


class UserInteraction:
    def __init__(self, chat_id, callback_id=None):
        self._chat_id = chat_id
        self._callback_id = callback_id

    def change_locale(self, data):
        with Update("bot_users") as update_locale:
            update_locale.user_attribute(self._chat_id, "locale", data[:2])

    def add_collection(self):
        user_id = self._chat_id
        callback_id = self._callback_id
        key = Tools.new_collection_key()

        with Select("bot_users") as select_user_locale:
            locale = select_user_locale.user_attribute(user_id, "locale")

        with Update("bot_users") as update_session:
            update_session.user_attribute(user_id, "session", key)

        with Select("bot_messages") as select_message:
            text = select_message.bot_message("create_collection", locale)

        api = API()
        request = api.send_message(user_id, text)
        callback = API.answer_callback_query(callback_id)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])

    def new_collection(self, collection_name):
        user_id = self._chat_id

        with Select("bot_users") as select:
            key = select.user_attribute(user_id, "session")
            locale = select.user_attribute(user_id, "locale")
            collections = select.user_attribute(user_id, "collections")

        with Insert("bot_collections") as insert_collection:
            insert_collection.new_collection(user_id, key, collection_name)

        with Update("bot_users") as update:
            update.user_attribute(user_id, "session", None)
            update.user_attribute(user_id, "collections", collections + 1)

        with Select("bot_messages") as select_message:
            text = select_message.bot_message("new_collection", locale)

        api = API()
        request = api.send_message(user_id, text)

        requests.post(request["url"], json=request["body"])
