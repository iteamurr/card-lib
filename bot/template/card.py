"""
    Implementation of tools for working with the ``Card`` object.
"""
from typing import Any
from typing import Optional

from ..tools.helpers import Bot
from ..tools.helpers import Tools
from ..tools.database import Select
from ..tools.database import Insert
from ..tools.database import Update
from ..tools.database import Delete
from ..shortcuts import CardTemplates
from ..config import bot_settings


class Card:
    """Class defining the ``Card`` object.

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
        self.card_key = None

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

        # Edit menu options.
        self.menu = None
        self.locale = None
        self.title = None
        self.parse_mode = None

        self._session_initialization()

    def handler(self) -> None:
        """Card-related user actions handler.
        """

        if self.session_header == "CaRSe":
            if self.session_data == "collection_cards":
                self.cards()

            elif self.session_data == "add_card":
                self.new_card_session()

            elif "edit" in self.session_data:
                if self.session_data == "edit_name":
                    self._edit_attribute_session("name")

                elif self.session_data == "edit_desc":
                    self._edit_attribute_session("description")

            elif "delete" in self.session_data:
                if self.session_data == "confirm_delete":
                    self.delete_confirmation()

                else:
                    self.delete_menu()

            elif "level" in self.session_data:
                self._change_level()

            else:
                self.info()

        elif self.session_header == "UsrCaRSe":
            if self.session_data == "create":
                self.new_card()

            elif self.session_data in ("edit_name", "edit_desc"):
                self.change_attribute()

    @Bot.edit_message
    @Bot.answer_callback_query
    def cards(self) -> None:
        """Show all user cards.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            level = select.collection_attribute(
                self.user_id, self.key, "page_level"
            )
            collection_name = select.collection_attribute(
                self.user_id, self.key, "name"
            )
            cards_list = select.collection_cards(self.user_id, self.key)

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "cards", self.locale
            ).format(collection_name)

        per_page = bot_settings["cards_per_page"]
        navigation = Tools.navigation_creator(
            header="CaRSe",
            number_of_items=len(cards_list),
            level=level,
            key=self.key,
            per_page=per_page
        )
        card_buttons = Tools.button_list_creator(
            obj="card",
            header="CaRSe",
            data="info",
            list_of_items=cards_list[per_page*level:per_page*(level + 1)]
        )
        buttons = CardTemplates.cards_template(self.locale, self.key)
        self.menu = (navigation + card_buttons + buttons)

    @Bot.edit_message
    @Bot.answer_callback_query
    @Bot.card_and_collection_existence_check
    def info(self) -> None:
        """Card Information menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            name = Tools.text_appearance(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "name"
                )
            )
            description = Tools.text_appearance(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "description"
                )
            )

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "description_info", self.locale
            ).format(name, description)

        self.menu = CardTemplates.info_template(
            self.locale, self.key, self.card_key
        )
        self.parse_mode="MarkdownV2"

    @Bot.send_message
    def new_card(self) -> None:
        """Create a new user card.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            cards = select.user_attribute(self.user_id, "cards")

        with Select("bot_collections") as select:
            collection_cards = select.collection_attribute(
                self.user_id, self.key, "cards"
            )

        with Select("bot_messages") as select:
            self.text = select.bot_message("new_card", self.locale)

        with Insert("bot_collections") as insert:
            insert.new_card(
                self.user_id, self.key, self.card_key, self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)
            update.user_attribute(self.user_id, "cards", cards + 1)

        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id, self.key, "cards", collection_cards + 1
            )

        self.message_menu = CardTemplates.new_card_template(
            self.key, self.card_key, self.message_text
        )

    @Bot.send_message
    @Bot.answer_callback_query
    def new_card_session(self) -> None:
        """Change current user session to card creation session.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("create_card", self.locale)

        session = f"UsrCaRSe/create/{self.key}/{Tools.new_card_key()}"

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", session)

    @Bot.edit_message
    @Bot.answer_callback_query
    @Bot.card_and_collection_existence_check
    def delete_menu(self) -> None:
        """Delete card menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "card_delete_confirm", self.locale
            )

        self.menu = CardTemplates.delete_menu_template(
            self.locale, self.key, self.card_key
        )

    @Bot.edit_message
    @Bot.answer_callback_query
    @Bot.card_and_collection_existence_check
    def delete_confirmation(self) -> None:
        """Card deletion confirmation menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            cards = select.user_attribute(self.user_id, "cards")

        with Select("bot_collections") as select:
            collection_cards = select.collection_attribute(
                self.user_id, self.key, "cards"
            )
            page_level = select.collection_attribute(
                self.user_id, self.key, "page_level"
            )

        with Delete("bot_collections") as delete:
            delete.card(self.user_id, self.key, self.card_key)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "cards", cards - 1)

        with Update("bot_collections") as update:
            if collection_cards >= 1:
                update.collection_attribute(
                    self.user_id, self.key, "cards", collection_cards - 1
                )
            if page_level >= 1:
                update.collection_attribute(
                    self.user_id, self.key, "page_level", page_level - 1
                )

        with Select("bot_messages") as select:
            self.title = select.bot_message("card_deleted", self.locale)

        self.menu = CardTemplates.delete_confirmation_template(
            self.locale, self.key
        )

    @Bot.edit_message
    @Bot.send_message
    @Bot.card_and_collection_existence_check
    def change_attribute(self) -> None:
        """Change any attribute of the card.
        """

        if "edit_desc" in self.session_data:
            attribute = "description"

        if "edit_name" in self.session_data:
            attribute = "name"

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            self.message_id = select.user_attribute(self.user_id, "menu_id")

        with Update("bot_collections") as update:
            update.card_attribute(
                self.user_id,
                self.key,
                self.card_key,
                attribute,
                self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_messages") as select:
            self.text = select.bot_message(
                f"card_{attribute}_changed", self.locale
            )

        with Select("bot_collections") as select:
            name = Tools.text_appearance(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "name"
                )
            )
            description = Tools.text_appearance(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "description"
                )
            )

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "description_info", self.locale
            ).format(name, description)

        self.menu = CardTemplates.info_template(
            self.locale, self.key, self.card_key
        )
        self.parse_mode = "MarkdownV2"

    @Bot.send_message
    @Bot.answer_callback_query
    @Bot.card_and_collection_existence_check
    def _edit_attribute_session(self, attribute):
        key = f"UsrCaRSe/session_edit_{attribute}/{self.key}/{self.card_key}"

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                f"edit_card_{attribute}", self.locale
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

    def _change_level(self):
        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id,
                self.key,
                "page_level",
                int(self.session_data[-2:])
            )

        self.cards()

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

        if len(session) > 3:
            self.card_key = session[3]
