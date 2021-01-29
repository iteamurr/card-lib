"""
    Module for working with user collections.
"""

from .tools import API
from .tools import Tools
from .database import Select
from .database import Update
from .database import Delete


class Collection:
    """Class defining the collection object.
    """

    def __init__(self, message, callback_query):
        self._message = None
        self._user_id = None
        self._message_text = None
        if message:
            self._message = message
            self._user_id = message["chat"]["id"]
            self._message_text = message["text"]

        self._data = None
        self._message_id = None
        self._callback_id = None
        if callback_query:
            self._data = callback_query["data"]
            self._user_id = callback_query["from"]["id"]
            self._message_id = callback_query["message"]["message_id"]
            self._callback_id = callback_query["id"]

    def action_handler(self):
        """Collection-related user actions handler.
        """

        if "edit" in self._data:
            if "name" in self._data:
                self._edit_attribute_session("name")
            elif "description" in self._data:
                self._edit_attribute_session("description")
            else:
                self.edit_menu()
        elif "delete" in self._data:
            if "confirm" in self._data:
                self.delete_confirmation()
            else:
                self.delete_menu()
        else:
            self.info()

    def session_handler(self):
        """Handle a user session.
        """

        with Select("bot_users") as select:
            session = select.user_attribute(self._user_id, "session")

        if "edit" in session:
            if "name" in session:
                self._new_attribute_value("name", self._message_text)
            elif "description" in session:
                self._new_attribute_value("description", self._message_text)

    def info(self):
        """Collection Information menu.
        """

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

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_collections") as select:
            name = select.collection_attribute(self._user_id, key, "name")
            desc = select.collection_attribute(self._user_id, key,
                                               "description")

        with Select("bot_messages") as select:
            if desc:
                title = select.bot_message("collection_description_info",
                                           locale)
            else:
                title = select.bot_message("collection_info", locale)

        if desc:
            title = title.format(name, desc)
        else:
            title = title.format(name)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id, title,
                         keyboard=keyboard, parse_mode="MarkdownV2")
        API.answer_callback_query(self._callback_id)

    def edit_menu(self):
        """Collection Edit menu.
        """

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

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("collection_description_info", locale)

        with Select("bot_collections") as select:
            name = select.collection_attribute(self._user_id, key, "name")
            desc = select.collection_attribute(self._user_id, key,
                                               "description")

        description = "🚫" if not desc else desc
        title = title.format(name, description)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id, title,
                         keyboard=keyboard, parse_mode="MarkdownV2")
        API.answer_callback_query(self._callback_id)

    def delete_menu(self):
        """Delete collection menu.
        """

        key = Tools.get_key_from_string(self._data)
        template = [
            [
                ["confirm_deletion", f"confirm_delete_{key}"],
                ["undo_delete",  f"edit_collection_{key}"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("delete_confirmation", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def delete_confirmation(self):
        """Collection deletion confirmation menu.
        """

        key = Tools.get_key_from_string(self._data)
        template = [
            [
                ["collections", "collections"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")
            collections = select.user_attribute(self._user_id, "collections")

        with Delete("bot_collections") as delete:
            delete.collection(self._user_id, key)

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "collections", collections-1)

        with Select("bot_messages") as select:
            title = select.bot_message("collection_deleted", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def _edit_attribute_session(self, attribute):
        key = f"edit_{attribute}_{Tools.get_key_from_string(self._data)}"

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message(f"edit_collection_{attribute}", locale)

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "session", key)
            update.user_attribute(self._user_id, "menu_id", self._message_id)

        API.send_message(self._user_id, text)
        API.answer_callback_query(self._callback_id)

    def _new_attribute_value(self, attribute, value):
        data = f"collection_{attribute}_changed"

        with Select("bot_users") as select:
            key_string = select.user_attribute(self._user_id, "session")
            locale = select.user_attribute(self._user_id, "locale")
            menu_id = select.user_attribute(self._user_id, "menu_id")

        key = Tools.get_key_from_string(key_string)

        with Update("bot_collections") as update:
            update.collection_attribute(self._user_id, key, attribute, value)

        with Update("bot_users") as update:
            update.user_attribute(self._user_id, "session", None)

        with Select("bot_messages") as select:
            text = select.bot_message(data, locale)

        API.send_message(self._user_id, text)
        self._message_id, self._data = menu_id, key
        self.edit_menu()
