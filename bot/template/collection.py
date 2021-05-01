"""
    Implementation of tools for working with the ``Collection`` object.
"""

from typing import Any
from typing import Optional

from ..tools.helpers import Bot
from ..tools.helpers import Tools
from ..tools.database import Select
from ..tools.database import Insert
from ..tools.database import Update
from ..tools.database import Delete
from ..shortcuts import CollectionTemplates
from ..config import bot_settings

class Collection:
    """Class defining the ``Collection`` object.

    Attributes:
        message: An object containing all information
                 about the user's message.
        callback_query: An object containing
                        all information about the user's query.
    """

    def __init__(
        self,
        message: Optional[dict[str, Any]] = None,
        callback_query: Optional[dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.callback_query = callback_query

        # Current session parameters.
        self.session_header = None
        self.session_data = None
        self.key = None

        # User parameters.
        self.user_id = None
        self.message_text = None
        self.message_id = None
        self.data = None
        self.callback_id = None

        self.callback_query_text = None
        self.show_alert = None

        # Send message options.
        self.text = None
        self.message_menu = None
        self.disable_web_page_preview = False

        # Edit menu options.
        self.menu = None
        self.locale = None
        self.title = None
        self.parse_mode = None

        self._session_initialization()

    def handler(self) -> None:
        """Collection-related user actions handler.
        """

        if self.session_header == "CoLSe":
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

            elif self.session_data == "collections":
                self.collections()

            elif self.session_data == "add_collection":
                self.add_collection_session()

            elif "level" in self.session_data:
                self._change_level()

            else:
                self.info()

        elif self.session_header == "UsrCoLSe":
            if self.session_data == "create":
                if Tools.collection_search(self.message_text):
                    self.copy_collection()
                else:
                    self.new_collection()

            elif self.session_data in ("edit_name", "edit_description"):
                self.change_attribute()

    @Bot.edit_message
    @Bot.answer_callback_query
    def collections(self) -> None:
        """Show all user collections.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            level = select.user_attribute(self.user_id, "page_level")

        with Select("bot_messages") as select:
            self.title = select.bot_message("collections", self.locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self.user_id)

        per_page = bot_settings["collections_per_page"]
        navigation = Tools.navigation_creator(
            header="CoLSe",
            number_of_items=len(collections_list),
            level=level,
            per_page=per_page
        )
        items = collections_list[per_page*level:per_page*(level + 1)]
        collection_buttons = Tools.button_list_creator(
            obj="collection",
            header="CoLSe",
            data="info",
            list_of_items=items
        )
        buttons = CollectionTemplates.collections_template(self.locale)
        self.menu = (navigation + collection_buttons + buttons)

    @Bot.send_message
    def new_collection(self) -> None:
        """Create a new user collection.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")

        with Select("bot_messages") as select:
            self.text = select.bot_message("new_collection", self.locale)

        with Insert("bot_collections") as insert:
            insert.new_collection(self.user_id, self.key, self.message_text)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                self.user_id, "collections", collections + 1
            )

        self.message_menu = CollectionTemplates.new_collection_template(
            self.key, self.message_text
        )

    @Bot.send_message
    def copy_collection(self) -> None:
        """Copy another user's collection.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")
            cards = select.user_attribute(self.user_id, "cards")

        with Select("bot_messages") as select:
            self.text = select.bot_message("copy_collection", self.locale)

        with Insert("bot_collections") as insert:
            new_key = Tools.new_collection_key()
            insert.copy_collection(self.user_id, self.message_text, new_key)

        with Select("bot_collections") as select:
            new_cards = select.collection_attribute(
                self.user_id, new_key, "cards"
            )
            name = select.collection_attribute(
                self.user_id, new_key, "name"
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                self.user_id, "cards", cards + new_cards
            )
            update.user_attribute(
                self.user_id, "collections", collections + 1
            )

        self.message_menu = CollectionTemplates.new_collection_template(
            new_key, name
        )

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def info(self) -> None:
        """Collection Information menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    self.user_id, self.key, "description"
                )
            )

        with Select("bot_messages") as select:
            if description:
                self.title = select.bot_message(
                    "description_info", self.locale
                ).format(name, description)
            else:
                self.title = select.bot_message(
                    "collection_info", self.locale
                ).format(name)

        self.menu = CollectionTemplates.info_template(self.locale, self.key)
        self.parse_mode = "MarkdownV2"

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def public_key(self) -> None:
        """Collection Public Key menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "public_key_text", self.locale
            ).format(self.key)

        self.menu = CollectionTemplates.public_key_template(
            self.locale, self.key
        )
        self.parse_mode = "MarkdownV2"

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def edit_menu(self) -> None:
        """Collection Edit menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    self.user_id, self.key, "description"
                )
            )

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "description_info", self.locale
            ).format(name, description)

        self.menu = CollectionTemplates.edit_menu_template(
            self.locale, self.key
        )
        self.parse_mode = "MarkdownV2"

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def delete_menu(self) -> None:
        """Delete collection menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "delete_confirmation", self.locale
            )

        self.menu = CollectionTemplates.delete_menu_template(
            self.locale, self.key
        )

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def delete_confirmation(self) -> None:
        """Collection deletion confirmation menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
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
            self.title = select.bot_message("collection_deleted", self.locale)

        self.menu = CollectionTemplates.delete_confirmation_template(
            self.locale
        )

    @Bot.send_message
    @Bot.answer_callback_query
    def add_collection_session(self) -> None:
        """Change current user session to collection creation session.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("create_collection", self.locale)

        session = f"UsrCoLSe/create/{Tools.new_collection_key()}"

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", session)

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.send_message
    def change_attribute(self) -> None:
        """Change any attribute of the collection.
        """

        attribute = self.session_data.split("_")[1]

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            self.message_id = select.user_attribute(self.user_id, "menu_id")

        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id, self.key, attribute, self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_messages") as select:
            self.text = select.bot_message(
                f"collection_{attribute}_changed", self.locale
            )

        with Select("bot_collections") as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    self.user_id, self.key, "description"
                )
            )

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "description_info", self.locale
            ).format(name, description)

        self.menu = CollectionTemplates.edit_menu_template(
            self.locale, self.key
        )
        self.parse_mode = "MarkdownV2"

    @Bot.collection_existence_check
    @Bot.send_message
    @Bot.answer_callback_query
    def _edit_attribute_session(self, attribute):
        key = f"UsrCoLSe/edit_{attribute}/{self.key}"

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message(
                f"edit_collection_{attribute}", self.locale
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

    def _change_level(self):
        with Update("bot_users") as update:
            update.user_attribute(
                self.user_id,
                "page_level",
                int(self.data[-2:])
            )

        self.collections()

    def _session_initialization(self):
        if self.message:
            self.user_id = self.message["chat"]["id"]
            self.message_text = self.message["text"]

        if self.callback_query:
            self.user_id = self.callback_query["from"]["id"]
            self.message_id = self.callback_query["message"]["message_id"]
            self.data = self.callback_query["data"]
            self.callback_id = self.callback_query["id"]

        user_session = Tools.get_session(self.user_id)
        if user_session:
            session = Tools.define_session(user_session)
        else:
            session = Tools.define_session(self.data)

        self.session_header = session[0]
        self.session_data = session[1]

        if len(session) > 2:
            self.key = session[2]
