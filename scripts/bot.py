"""
    Module that determines bot's response to a user action.
"""

from .tools import API
from .tools import Tools
from .database import Select
from .database import Insert
from .database import Update
from .collection import Collection


class BotHandler:
    """Determining the type of user action.
    """

    def __init__(self, message, callback_query):
        self._message = None
        self._user_id = None
        self._message_text = None
        self._message_entities = None
        if message:
            self._message = message
            self._user_id = message["chat"]["id"]
            self._message_text = message["text"]

            if "entities" in message:
                self._message_entities = message["entities"][0]["type"]

        self._callback_query = None
        self._data = None
        if callback_query:
            self._callback_query = callback_query
            self._data = callback_query["data"]
            self._user_id = callback_query["from"]["id"]

    def message_handler(self):
        """Handle a user's text message.
        """

        send_menu = SendMenu(self._user_id)

        if self._message_entities == "bot_command":
            if "/start" in self._message_text:
                Tools.check_new_user(self._message)
                send_menu.private_office()

            elif "/settings" in self._message_text:
                send_menu.settings()

    def callback_query_handler(self):
        """Handle an incoming callback query
        from a callback button in an inlin keyboard.
        """

        switch_menu = SwitchMenu(self._callback_query)
        bot_tools = BotTools(self._user_id, self._callback_query)
        collection = Collection(self._message, self._callback_query)

        if self._data == "private_office":
            switch_menu.private_office()

        elif self._data == "settings":
            switch_menu.settings()

        elif "CL" in self._data:
            collection.action_handler()

        elif "collection" in self._data:
            if self._data == "collections":
                switch_menu.collections()
            elif self._data == "add_collection":
                bot_tools.add_collection_session()

        elif "locale" in self._data:
            if self._data == "locale_settings":
                switch_menu.locale_settings()
            else:
                bot_tools.change_locale()
                switch_menu.locale_settings()

        elif "level" in self._data:
            bot_tools.change_level()
            switch_menu.collections()

    def session_handler(self):
        """Handle a user session.
        """

        bot_tools = BotTools(self._user_id, self._callback_query)
        collection = Collection(self._message, self._callback_query)

        with Select("bot_users") as select:
            session = select.user_attribute(self._user_id, "session")

        if session:
            if session[-2:] == "CL":
                if session[0] == "K":
                    bot_tools.new_collection(self._message_text)
                else:
                    collection.session_handler()


class SendMenu:
    """Sending basic user menus.
    """

    def __init__(self, user_id):
        self._user_id = user_id

    def private_office(self):
        """Send a user's Private Office.
        """

        template = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)
        API.send_message(self._user_id, title, keyboard=keyboard)

    def settings(self):
        """Send a user's Settings menu.
        """

        template = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)
        API.send_message(self._user_id, title, keyboard=keyboard)


class SwitchMenu:
    """User menu switching.
    """

    def __init__(self, callback_query):
        self._data = None
        self._user_id = None
        self._message_id = None
        self._callback_id = None

        if callback_query:
            self._data = callback_query["data"]
            self._user_id = callback_query["from"]["id"]
            self._message_id = callback_query["message"]["message_id"]
            self._callback_id = callback_query["id"]

    def private_office(self):
        """Switch menu to the user's Private Office.
        """

        template = [
            [
                ["collections", "collections"],
                ["settings", "settings"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def settings(self):
        """Switch menu to the user's Settings.
        """

        template = [
            [
                ["locale_settings", "locale_settings"]
            ],
            [
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def collections(self, collections_in_page=8):
        """Switch menu to the user's Collections.

        Parameters
        ----------
        collections_in_page : int, optional
            Number of user collections per page.
        """

        template = [
            [
                ["add_collection", "add_collection"],
                ["back", "private_office"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")
            level = select.user_attribute(self._user_id, "page_level")

        with Select("bot_messages") as select:
            title = select.bot_message("collections", locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self._user_id)

        navigation = Tools.navigation_creator(len(collections_list), level)

        bord = slice(collections_in_page*level, collections_in_page*(level+1))
        collection_buttons = Tools.button_list_creator(collections_list[bord])

        buttons = Tools.button_identifier(template, locale)
        all_buttons = (navigation + collection_buttons + buttons)
        keyboard = API.inline_keyboard(*all_buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def locale_settings(self):
        """Switch menu to the user's Locale Settings.
        """

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

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("current_language", locale)

        title = title.format(locale_list[locale])
        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id, title,
                         keyboard=keyboard, parse_mode="MarkdownV2")
        API.answer_callback_query(self._callback_id)


class BotTools:
    """Basic tools for working with a bot.
    """

    def __init__(self, user_id, callback_query):
        self._user_id = user_id
        self._data = None
        self._callback_id = None

        if callback_query:
            self._data = callback_query["data"]
            self._callback_id = callback_query["id"]

    def change_locale(self):
        """Change user locale.
        """

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "locale", self._data[:2])

    def change_level(self):
        """Change the page number (level) of a user.
        """

        level = int(self._data[-2:])

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "page_level", level)

    def add_collection_session(self):
        """Switch user session to collection creation.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message("create_collection", locale)

        key = Tools.new_collection_key()

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "session", key)

        API.send_message(self._user_id, text)
        API.answer_callback_query(self._callback_id)

    def new_collection(self, name):
        """Creat a new collection.

        Parameters
        ----------
        name : str
            New collection name.
        """

        with Select("bot_users") as select:
            key = select.user_attribute(self._user_id, "session")
            locale = select.user_attribute(self._user_id, "locale")
            collections = select.user_attribute(self._user_id, "collections")

        with Select("bot_messages") as select:
            text = select.bot_message("new_collection", locale)

        with Insert("bot_collections") as insert:
            insert.new_collection(self._user_id, key, name)

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "session", None)
            update.user_attribute(self._user_id, "collections", collections+1)

        keyboard = API.inline_keyboard([[name, key]])
        API.send_message(self._user_id, text, keyboard)
