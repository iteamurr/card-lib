"""
    Module for working with user collections.
"""

from typing import Any
from typing import Callable
from typing import Optional

from ..tools import API
from ..tools import Tools
from ..database import Select
from ..database import Insert
from ..database import Update
from ..database import Delete
from ..shortcuts import CollectionTemplates


def existence_check(func: Callable) -> Callable:
    """Decorator that checks if a collection exists in the database.
    """

    def wrapper_func(self, *args, **kwargs):
        is_exists = Tools.check_collection_existence(self.user_id, self.key)

        if is_exists:
            func(self, *args, **kwargs)
        else:
            with Select("bot_users") as select:
                locale = select.user_attribute(self.user_id, "locale")

            with Select("bot_messages") as select:
                title = select.bot_message("does_not_exist", locale)

            API.answer_callback_query(
                self.callback_id, text=title, show_alert=True
            )
            return
    return wrapper_func


# pylint: disable=unsubscriptable-object
class Collection:
    """Class defining the collection object.

    Attributes:
        callback_query: An object containing
            all information about the user's query.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        self.data = callback_query["data"]
        self.callback_id = callback_query["id"]
        self.user_id = callback_query["from"]["id"]
        self.message_id = callback_query["message"]["message_id"]

        self.session_data = None
        self.key = None

        self._session_initialization()

    @existence_check
    def handler(self) -> None:
        """Collection-related user actions handler.
        """

        if self.session_data == "public_key":
            self.public_key()

        elif "edit" in self.session_data:
            if self.session_data == "edit_name":
                self._edit_attribute_session("name")

            elif self.session_data == "edit_desc":
                self._edit_attribute_session("description")

            else:
                self.edit_menu()

        elif "delete" in self.session_data:
            if self.session_data == "confirm_delete":
                self.delete_confirmation()

            else:
                self.delete_menu()

        else: # info
            self.info()

    def info(self) -> None:
        """Collection Information menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            name = select.collection_attribute(self.user_id, self.key, "name")
            description = select.collection_attribute(
                self.user_id, self.key, "description"
            )

        with Select("bot_messages") as select:
            if description:
                title = select.bot_message(
                    "description_info", locale
                ).format(name, description)
            else:
                title = select.bot_message(
                    "collection_info", locale
                ).format(name)

        menu = CollectionTemplates.info_template(locale, self.key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def public_key(self) -> None:
        """Collection Public Key menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message(
                "public_key_text", locale
            ).format(self.key)

        menu = CollectionTemplates.public_key_template(locale, self.key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def edit_menu(self) -> None:
        """Collection Edit menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            name = select.collection_attribute(self.user_id, self.key, "name")
            description = select.collection_attribute(
                self.user_id, self.key, "description"
            )

        with Select("bot_messages") as select:
            title = select.bot_message(
                "description_info", locale
            ).format(name, description)

        menu = CollectionTemplates.edit_menu_template(locale, self.key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def delete_menu(self) -> None:
        """Delete collection menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("delete_confirmation", locale)

        menu = CollectionTemplates.delete_menu_template(locale, self.key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def delete_confirmation(self) -> None:
        """Collection deletion confirmation menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")
            cards = select.user_attribute(self.user_id, "cards")
            page_level = select.user_attribute(self.user_id, "page_level")

        with Select("bot_collections") as select:
            collection_cards = select.collection_attribute(
                self.user_id, self.key, "cards"
            )

        with Delete("bot_collections") as delete:
            delete.collection(self.user_id, self.key)

        with Update("bot_users") as update:
            update.user_attribute(
                self.user_id, "collections", collections - 1
            )
            update.user_attribute(
                self.user_id, "cards", cards - collection_cards
            )
            if page_level >= 1:
                update.user_attribute(
                    self.user_id, "page_level", page_level - 1
                )

        with Select("bot_messages") as select:
            title = select.bot_message("collection_deleted", locale)

        menu = CollectionTemplates.delete_confirmation_template(locale)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_data = session[1]
        self.key = session[2]

    def _edit_attribute_session(self, attribute):
        key = f"UsrCoLSe/edit_{attribute}/{self.key}"

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message(f"edit_collection_{attribute}", locale)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

        API.send_message(self.user_id, text)
        API.answer_callback_query(self.callback_id)


class Collections:
    """Class that defines collections objects.

    Attributes:
        callback_query: An object containing
            all information about the user's query.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        self.data = callback_query["data"]
        self.callback_id = callback_query["id"]
        self.user_id = callback_query["from"]["id"]
        self.message_id = callback_query["message"]["message_id"]

        self.session_data = None

        self._session_initialization()

    def handler(self) -> None:
        """Collections-related user actions handler.
        """

        if self.session_data == "collections":
            self.collections()

        elif self.session_data == "add_collection":
            self.add_collection_session()

        elif "level" in self.session_data:
            self._change_level()

        else:
            self._undefined_menu()

    def collections(self, per_page: Optional[int] = 8) -> None:
        """Show all user collections.

        Args:
            per_page: Number of collections per page.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            level = select.user_attribute(self.user_id, "page_level")

        with Select("bot_messages") as select:
            title = select.bot_message("collections", locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self.user_id)

        navigation = Tools.navigation_creator(
            "CoLsSe", len(collections_list), level=level, per_page=per_page
        )
        items = collections_list[per_page*level:per_page*(level + 1)]
        collection_buttons = Tools.button_list_creator(
            "collection", "CoLSe", "info", items
        )
        buttons = CollectionTemplates.collections_template(locale)
        menu = (navigation + collection_buttons + buttons)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def add_collection_session(self) -> None:
        """Change current user session to collection creation session.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message("create_collection", locale)

        session = f"UsrCoLSe/create/{Tools.new_collection_key()}"

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", session)

        API.send_message(self.user_id, text)
        API.answer_callback_query(self.callback_id)

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_data = session[1]

    def _change_level(self):
        with Update("bot_users") as update:
            update.user_attribute(
                self.user_id, "page_level", int(self.data[-2:])
            )

        self.collections()

    def _undefined_menu(self):
        pass


class CollectionSession:
    """Class that handles the collection session.

    Attributes:
        user_id: Unique identifier for the target user.
        message_text: User's message text.
    """

    def __init__(self, user_id: int, message_text: str) -> None:
        self.user_id = user_id
        self.message_text = message_text

        self.session_data = None
        self.key = None

        self._session_initialization()

    def handler(self) -> None:
        """Handler taking action from session.
        """

        if self.session_data == "create":
            self.new_collection()

        elif self.session_data in ("edit_name", "edit_description"):
            self.change_collection_attribute()

    def new_collection(self) -> None:
        """Create a new user collection.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")

        with Select("bot_messages") as select:
            text = select.bot_message("new_collection", locale)

        with Insert("bot_collections") as insert:
            insert.new_collection(self.user_id, self.key, self.message_text)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                self.user_id, "collections", collections + 1
            )

        menu = CollectionTemplates.new_collection_template(
            self.key, self.message_text
        )
        API.send_message(
            self.user_id, text, keyboard=API.inline_keyboard(menu)
        )

    def change_collection_attribute(self) -> None:
        """Change any attribute of the collection.
        """

        attribute = self.session_data.split("_")[1]

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            menu_id = select.user_attribute(self.user_id, "menu_id")

        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id, self.key, attribute, self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_messages") as select:
            text = select.bot_message(
                f"collection_{attribute}_changed", locale
            )

        with Select("bot_collections") as select:
            name = select.collection_attribute(self.user_id, self.key, "name")
            description = select.collection_attribute(
                self.user_id, self.key, "description"
            )

        with Select("bot_messages") as select:
            title = select.bot_message(
                "description_info", locale
            ).format(name, description)

        menu = CollectionTemplates.edit_menu_template(locale, self.key)
        API.send_message(self.user_id, text)
        API.edit_message(
            self.user_id, menu_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )

    def _session_initialization(self):
        user_session = Tools.get_session(self.user_id)

        if user_session:
            session = Tools.define_session(user_session)
            self.session_data = session[1]
            self.key = session[2]
