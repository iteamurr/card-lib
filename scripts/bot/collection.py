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

# pylint: disable=unsubscriptable-object
def existence_check(func: Callable) -> Callable:
    """Decorator that checks if a collection exists in the database.
    """

    def wrapper_func(self, *args, **kwargs):
        with Select("bot_collections") as select:
            name = bool(
                select.collection_attribute(self.user_id, self.key, "name")
            )

        if name:
            func(self, *args, **kwargs)
        else:
            with Select("bot_users") as select:
                locale = select.user_attribute(self.user_id, "locale")

            with Select("bot_messages") as select:
                title = select.bot_message("does_not_exist", locale)

            API.answer_callback_query(
                self.callback_id,
                text=title, show_alert=True
            )
            return
    return wrapper_func


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

            elif self.session_data == "edit_description":
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

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLSe", data="collection_learning",
                    name=f"collection_learning/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRsSe", data="collection_cards",
                    name=f"collection_cards/{self.key}", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="CoLSe", data="public_key",
                    name=f"public_key/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="settings",
                    name=f"edit_collection/{self.key}", locale=locale
                ),
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name="private_office", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLsSe", data="back",
                    name="collections", locale=locale
                ),
            )
        )

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

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(buttons), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def public_key(self) -> None:
        """Collection Public Key menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{self.key}", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message(
                "public_key_text", locale
            ).format(self.key)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(buttons), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def edit_menu(self) -> None:
        """Collection Edit menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLSe", data="edit_name",
                    name=f"edit_name/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="edit_description",
                    name=f"edit_description/{self.key}", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="CoLSe", data="delete_collection",
                    name=f"delete_collection/{self.key}", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name=f"private_office/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{self.key}", locale=locale
                )
            )
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

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(buttons), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def delete_menu(self) -> None:
        """Delete collection menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLSe", data="confirm_deletion",
                    name=f"confirm_delete/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="undo_delete",
                    name=f"edit_collection/{self.key}", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("delete_confirmation", locale)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(buttons)
        )
        API.answer_callback_query(self.callback_id)

    def delete_confirmation(self) -> None:
        """Collection deletion confirmation menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="collections", locale=locale
                )
            )
        )

        with Delete("bot_collections") as delete:
            delete.collection(self.user_id, self.key)

        with Update("bot_users") as update:
            update.user_attribute(
                self.user_id, "collections", collections - 1
            )

        with Select("bot_messages") as select:
            title = select.bot_message("collection_deleted", locale)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(buttons)
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

        self._session_initialization()

    def handler(self) -> None:
        """Collections-related user actions handler.
        """

        if self.data == "collections":
            self.collections()

        elif self.data == "add_collection":
            self.add_collection_session()

        else:
            self._undefined_menu()

    def collections(self, collections_in_page: Optional[int] = 8) -> None:
        """Show all user collections.

        Args:
            collections_in_page: Number of collections per page.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            level = select.user_attribute(self.user_id, "page_level")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLsSe", data="add_collection",
                    name="add_collection", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="back",
                    name="private_office", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("collections", locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self.user_id)

        navigation = Tools.navigation_creator(len(collections_list), level)

        bord = slice(collections_in_page*level,
                     collections_in_page*(level + 1))
        collection_buttons = Tools.button_list_creator(
            list_of_items=collections_list[bord],
            header="CoLSe", data="info"
        )

        all_buttons = (navigation + collection_buttons + buttons)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(all_buttons)
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

        buttons = (
            (
                Tools.button_template(
                    header="CoLSe",
                    data=f"info/{self.key}", name=self.message_text
                )
            )
        )

        with Select("bot_messages") as select:
            text = select.bot_message("new_collection", locale)

        with Insert("bot_collections") as insert:
            insert.new_collection(self.user_id, self.key, self.message_text)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                self.user_id, "collections", collections + 1
            )

        API.send_message(
            self.user_id, text,
            keyboard=API.inline_keyboard(buttons)
        )

    def change_collection_attribute(self) -> None:
        """Change any attribute of the collection.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            menu_id = select.user_attribute(self.user_id, "menu_id")

        attribute = self.session_data.split("_")[1]
        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLSe", data="edit_name",
                    name=f"edit_name/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="edit_description",
                    name=f"edit_description/{self.key}", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="CoLSe", data="delete_collection",
                    name=f"delete_collection/{self.key}", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name=f"private_office/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{self.key}", locale=locale
                )
            )
        )

        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id, self.key, attribute, self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_messages") as select:
            text = select.bot_message(
                f"collection_{attribute}_changed",
                locale
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

        API.send_message(self.user_id, text)
        API.edit_message(
            self.user_id, menu_id, title,
            keyboard=API.inline_keyboard(buttons), parse_mode="MarkdownV2"
        )

    def _session_initialization(self):
        user_session = Tools.get_session(self.user_id)

        if user_session:
            session = Tools.define_session(user_session)
            self.session_data = session[1]
            self.key = session[2]
