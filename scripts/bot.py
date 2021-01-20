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

        user_interaction = UserInteraction(
            chat_id, message_id,
            callback_id, data)
        switch_menu = SwitchMenu(chat_id, message_id, callback_id, data)
        if data == "private_office":
            switch_menu.private_office()

        elif "CL" in data:
            if "edit" in data:
                if "name" in data:
                    user_interaction.edit_name()
                else:
                    switch_menu.edit_collection()
            else:
                switch_menu.collection_info()

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
                user_interaction.change_locale()
                switch_menu.locale_settings()

        elif "level" in data:
            user_interaction.change_level()
            switch_menu.collections()

    @staticmethod
    def _session_handler(message):
        message_text = message["text"]
        chat_id = message["chat"]["id"]

        with Select("bot_users") as select_session:
            session = select_session.user_attribute(chat_id, "session")

        user_interaction = UserInteraction(chat_id)
        if session:
            if session[-2:] == "CL":
                if session[1] == "K":
                    user_interaction.new_collection(message_text)
                elif session[:4] == "EDNM":
                    user_interaction.new_collection_name(message_text)


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

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_menu_title:
            locale = select_user_locale.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        self._send(title, buttons)

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

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_menu_title:
            locale = select_user_locale.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        self._send(title, buttons)

    def _send(self, title, buttons, parse_mode=None):
        api = API()
        if parse_mode:
            request = api.send_message(self._chat_id, title, parse_mode)
        else:
            request = api.send_message(self._chat_id, title)

        keyboard = API.inline_keyboard(*buttons)
        request["body"] = {**request["body"], **keyboard}

        requests.post(request["url"], json=request["body"])


class SwitchMenu:
    def __init__(self, chat_id, message_id, callback_id, data):
        self._chat_id = chat_id
        self._message_id = message_id
        self._callback_id = callback_id
        self._data = data

    def private_office(self):
        user_id = self._chat_id
        template = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_menu_title:
            locale = select_user_locale.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        self._switch(title, buttons)

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

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_menu_title:
            locale = select_user_locale.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        self._switch(title, buttons)

    def locale_settings(self):
        user_id = self._chat_id
        locale_list = {"en": "English", "ru": "Русский"}
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

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_menu_title:
            locale = select_user_locale.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("current_language", locale)

        title = title.format(locale_list[locale])
        buttons = Tools.button_identifier(template, locale)
        self._switch(title, buttons, "MarkdownV2")

    def collections(self, collections_in_page=8):
        user_id = self._chat_id
        template = [
            [
                ["add_collection", "add_collection"],
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select_attribute, \
             Select("bot_messages") as select_menu_title, \
             Select("bot_collections") as select_collections:
            locale = select_attribute.user_attribute(user_id, "locale")
            level = select_attribute.user_attribute(user_id, "page_level")
            title = select_menu_title.bot_message("collections", locale)
            collections_list = select_collections.user_collections(user_id)

        bord = slice(collections_in_page*level, collections_in_page*(level+1))
        navigation = Tools.navigation_creator(len(collections_list), level)
        collection_buttons = Tools.keyboard_creator(collections_list[bord])
        buttons = Tools.button_identifier(template, locale)

        self._switch(title, navigation + collection_buttons + buttons)

    def collection_info(self):
        user_id = self._chat_id
        key = self._data
        template = [
            [
                ["collection_learning", f"collection_learning_{key}"],
                ["collection_cards", f"collection_cards_{key}"]
            ],
            [
                ["public_key", f"public_key_{key}"],
                ["settings", f"edit_collection_{key}"]
            ],
            [
                ["main", "private_office"],
                ["back", "collections"]
            ]
        ]

        with Select("bot_users") as select_attribute, \
             Select("bot_messages") as select_menu_title:
            locale = select_attribute.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message("collection_info", locale)

        with Select("bot_collections") as select_attribute:
            name = select_attribute.collection_attribute(user_id, key, "name")

        title = title.format(name)
        buttons = Tools.button_identifier(template, locale)
        self._switch(title, buttons, "MarkdownV2")

    def edit_collection(self):
        user_id = self._chat_id
        menu_title = "edit_collection_menu"
        key = Tools.get_key_from_string(self._data)
        template = [
            [
                ["edit_name", f"edit_name_{key}"],
                ["edit_description", f"edit_description_{key}"]
            ],
            [
                ["delete_collection", f"delete_collection_{key}"]
            ],
            [
                ["main", "private_office"],
                ["back", key]
            ]
        ]

        with Select("bot_users") as select_attribute, \
             Select("bot_messages") as select_menu_title:
            locale = select_attribute.user_attribute(user_id, "locale")
            title = select_menu_title.bot_message(menu_title, locale)

        with Select("bot_collections") as select:
            name = select.collection_attribute(user_id, key, "name")
            desc = select.collection_attribute(user_id, key, "description")

        description = "🚫" if not desc else desc
        title = title.format(name, description)
        buttons = Tools.button_identifier(template, locale)
        self._switch(title, buttons, "MarkdownV2")

    def _switch(self, title, buttons, parse_mode=None):
        user_id = self._chat_id
        message_id = self._message_id

        api = API()
        if parse_mode:
            request = api.edit_message(user_id, message_id, title, parse_mode)
        else:
            request = api.edit_message(user_id, message_id, title)

        keyboard = API.inline_keyboard(*buttons)
        request["body"] = {**request["body"], **keyboard}
        callback = api.answer_callback_query(self._callback_id)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])


class UserInteraction:
    def __init__(self, chat_id, message_id=None, callback_id=None, data=None):
        self._chat_id = chat_id
        self._message_id = message_id
        self._callback_id = callback_id
        self._data = data

    def change_locale(self):
        user_id = self._chat_id
        data = self._data

        with Update("bot_users") as update_locale:
            update_locale.user_attribute(user_id, "locale", data[:2])

    def change_level(self):
        user_id = self._chat_id
        level = int(self._data[-2:])

        with Update("bot_users") as update_level:
            update_level.user_attribute(user_id, "page_level", level)

    def add_collection(self):
        user_id = self._chat_id
        key = Tools.new_collection_key()

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_message:
            locale = select_user_locale.user_attribute(user_id, "locale")
            text = select_message.bot_message("create_collection", locale)

        with Update("bot_users") as update_session:
            update_session.user_attribute(user_id, "session", key)

        self._send(text)

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

        keyboard = API.inline_keyboard([[collection_name, key]])
        request["body"] = {**request["body"], **keyboard}

        requests.post(request["url"], json=request["body"])

    def edit_name(self):
        user_id = self._chat_id
        menu_id = self._message_id
        key = f"EDNM_{Tools.get_key_from_string(self._data)}"

        if key[-2:] == "CL":
            get_bot_message = "edit_collection_name"
        else:
            get_bot_message = "edit_card_name"

        with Select("bot_users") as select_user_locale, \
             Select("bot_messages") as select_message:
            locale = select_user_locale.user_attribute(user_id, "locale")
            text = select_message.bot_message(get_bot_message, locale)

        with Update("bot_users") as update_attribute:
            update_attribute.user_attribute(user_id, "session", key)
            update_attribute.user_attribute(user_id, "menu_id", menu_id)

        self._send(text)

    def new_collection_name(self, new_name):
        user_id = self._chat_id
        text_data = "collection_name_changed"
        value = new_name

        with Select("bot_users") as select_attribute:
            key_string = select_attribute.user_attribute(user_id, "session")
            locale = select_attribute.user_attribute(user_id, "locale")
            menu_id = select_attribute.user_attribute(user_id, "menu_id")

        key = Tools.get_key_from_string(key_string)

        with Update("bot_collections") as update_attribute:
            update_attribute.collection_attribute(user_id, key, "name", value)

        with Update("bot_users") as update_attribute:
            update_attribute.user_attribute(user_id, "session", None)

        with Select("bot_messages") as select_message:
            text = select_message.bot_message(text_data, locale)

        self._send(text)
        switch_menu = SwitchMenu(user_id, menu_id, self._callback_id, key)
        switch_menu.edit_collection()

    def _send(self, text):
        user_id = self._chat_id
        callback_id = self._callback_id

        api = API()
        request = api.send_message(user_id, text)
        callback = api.answer_callback_query(callback_id)

        requests.post(request["url"], json=request["body"])
        requests.post(callback["url"], json=callback["body"])
