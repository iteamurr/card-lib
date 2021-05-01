"""
    Implementation of tools for working with the `Collection` object.
"""
from typing import Any, Optional

from ..shortcuts import CollectionTemplates
from ..tools.helpers import Bot, Tools, Errors
from ..tools.database import Select, Insert, Update, Delete
from ..config import COLLECTIONS_PER_PAGE
from ..config import USERS_DATABASE, COLLECTIONS_DATABASE, MESSAGES_DATABASE

# pylint: disable=unsubscriptable-object
class Collection:
    """Class defining the `Collection` object.

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

    def callback_handler(self) -> None:
        """Collection menu interaction handler.
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

        elif self.session_data == "collections":
            self.collections()

        elif self.session_data == "add_collection":
            self.add_collection_session()

        elif "level" in self.session_data:
            self._change_level()

        else:
            self.info()

    def session_handler(self) -> None:
        """Collection properties change handler.
        """
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
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            level = select.user_attribute(self.user_id, "page_level")

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message("collections", self.locale)

        with Select(COLLECTIONS_DATABASE) as select:
            collections_list = select.user_collections(self.user_id)

        per_page = COLLECTIONS_PER_PAGE
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
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")

        with Select(MESSAGES_DATABASE) as select:
            self.text = select.bot_message("new_collection", self.locale)

        with Insert(COLLECTIONS_DATABASE) as insert:
            insert.new_collection(self.user_id, self.key, self.message_text)

        with Update(USERS_DATABASE) as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                user_id=self.user_id,
                attribute="collections",
                value=collections + 1
            )

        self.message_menu = CollectionTemplates.new_collection_template(
            key=self.key,
            name=self.message_text
        )

    @Bot.send_message
    def copy_collection(self) -> None:
        """Copy another user's collection.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")
            cards = select.user_attribute(self.user_id, "cards")

        with Select(MESSAGES_DATABASE) as select:
            self.text = select.bot_message("copy_collection", self.locale)

        with Insert(COLLECTIONS_DATABASE) as insert:
            new_key = Tools.new_collection_key()
            insert.copy_collection(self.user_id, self.message_text, new_key)

        with Select(COLLECTIONS_DATABASE) as select:
            new_cards = select.collection_attribute(
                user_id=self.user_id,
                key=new_key,
                attribute="cards"
            )
            name = select.collection_attribute(
                user_id=self.user_id,
                key=new_key,
                attribute="name"
            )

        with Update(USERS_DATABASE) as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(
                user_id=self.user_id,
                attribute="cards",
                value=cards + new_cards
            )
            update.user_attribute(
                user_id=self.user_id,
                attribute="collections",
                value=collections + 1
            )

        self.message_menu = CollectionTemplates.new_collection_template(
            key=new_key,
            name=name
        )

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def info(self) -> None:
        """Show collection information menu.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(COLLECTIONS_DATABASE) as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    user_id=self.user_id,
                    key=self.key,
                    attribute="description"
                )
            )

        with Select(MESSAGES_DATABASE) as select:
            if description:
                self.title = select.bot_message(
                    data="description_info",
                    locale=self.locale
                ).format(name, description)
            else:
                self.title = select.bot_message(
                    data="collection_info",
                    locale=self.locale
                ).format(name)

        self.menu = CollectionTemplates.info_template(self.locale, self.key)
        self.parse_mode = "MarkdownV2"

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def public_key(self) -> None:
        """Collection Public Key menu.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message(
                data="public_key_text",
                locale=self.locale
            ).format(self.key)

        self.menu = CollectionTemplates.public_key_template(
            locale=self.locale,
            key=self.key
        )
        self.parse_mode = "MarkdownV2"

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def edit_menu(self) -> None:
        """Collection Edit menu.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(COLLECTIONS_DATABASE) as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    user_id=self.user_id,
                    key=self.key,
                    attribute="description"
                )
            )

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message(
                data="description_info",
                locale=self.locale
            ).format(name, description)

        self.menu = CollectionTemplates.edit_menu_template(
            locale=self.locale,
            key=self.key
        )
        self.parse_mode = "MarkdownV2"

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def delete_menu(self) -> None:
        """Delete collection menu.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message(
                data="delete_confirmation",
                locale=self.locale
            )

        self.menu = CollectionTemplates.delete_menu_template(
            locale=self.locale,
            key=self.key
        )

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def delete_confirmation(self) -> None:
        """Collection deletion confirmation menu.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            collections = select.user_attribute(self.user_id, "collections")
            cards = select.user_attribute(self.user_id, "cards")
            page_level = select.user_attribute(self.user_id, "page_level")

        with Select(COLLECTIONS_DATABASE) as select:
            collection_cards = select.collection_attribute(
                user_id=self.user_id,
                key=self.key,
                attribute="cards"
            )

        with Delete(COLLECTIONS_DATABASE) as delete:
            delete.collection(self.user_id, self.key)

        with Update(USERS_DATABASE) as update:
            update.user_attribute(
                user_id=self.user_id,
                attribute="collections",
                value=collections - 1
            )
            update.user_attribute(
                user_id=self.user_id,
                attribute="cards",
                value=cards - collection_cards
            )
            if page_level >= 1:
                update.user_attribute(
                    user_id=self.user_id,
                    attribute="page_level",
                    value=page_level - 1
                )

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message("collection_deleted", self.locale)

        self.menu = CollectionTemplates.delete_confirmation_template(
            locale=self.locale
        )

    @Bot.send_message
    @Bot.answer_callback_query
    def add_collection_session(self) -> None:
        """Change current user session to collection creation session.
        """
        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(MESSAGES_DATABASE) as select:
            self.text = select.bot_message("create_collection", self.locale)

        session = f"UsrCoLSe/create/{Tools.new_collection_key()}"

        with Update(USERS_DATABASE) as update:
            update.user_attribute(self.user_id, "session", session)

    @Errors.collection_existence_check
    @Bot.edit_message
    @Bot.send_message
    def change_attribute(self) -> None:
        """Change any attribute of the collection.
        """
        attribute = self.session_data.split("_")[1]

        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            self.message_id = select.user_attribute(self.user_id, "menu_id")

        with Update(COLLECTIONS_DATABASE) as update:
            update.collection_attribute(
                user_id=self.user_id,
                key=self.key,
                attribute=attribute,
                value=self.message_text
            )

        with Update(USERS_DATABASE) as update:
            update.user_attribute(self.user_id, "session", None)

        with Select(MESSAGES_DATABASE) as select:
            self.text = select.bot_message(
                data=f"collection_{attribute}_changed",
                locale=self.locale
            )

        with Select(COLLECTIONS_DATABASE) as select:
            name = Tools.text_appearance(
                select.collection_attribute(self.user_id, self.key, "name")
            )
            description = Tools.text_appearance(
                select.collection_attribute(
                    user_id=self.user_id,
                    key=self.key,
                    attribute="description"
                )
            )

        with Select(MESSAGES_DATABASE) as select:
            self.title = select.bot_message(
                data="description_info",
                locale=self.locale
            ).format(name, description)

        self.menu = CollectionTemplates.edit_menu_template(
            locale=self.locale,
            key=self.key
        )
        self.parse_mode = "MarkdownV2"

    @Errors.collection_existence_check
    @Bot.send_message
    @Bot.answer_callback_query
    def _edit_attribute_session(self, attribute: str) -> None:
        """Write a change to a specific collection attribute
        in the current session.

        Args:
            attribute: Name, description or other attribute to be changed.
        """
        key = f"UsrCoLSe/edit_{attribute}/{self.key}"

        with Select(USERS_DATABASE) as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select(MESSAGES_DATABASE) as select:
            self.text = select.bot_message(
                data=f"edit_collection_{attribute}",
                locale=self.locale
            )

        with Update(USERS_DATABASE) as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

    def _change_level(self) -> None:
        """Change the layer containing the user's collections.
        """
        with Update(USERS_DATABASE) as update:
            update.user_attribute(
                user_id=self.user_id,
                attribute="page_level",
                value=int(self.data[-2:])
            )

        self.collections()

    def _session_initialization(self) -> None:
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
