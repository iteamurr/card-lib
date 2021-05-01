"""
    Implementation of tools for working with the ``Card`` object.
"""
from typing import Any
from typing import Optional
from datetime import datetime

from ..tools.helpers import Bot
from ..tools.helpers import Tools
from ..tools.helpers import Errors
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
        self.user_date = None
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
        """Card-related user actions handler.
        """

        if self.session_header == "CaRSe":
            if self.session_data == "collection_cards":
                self.cards()

            elif self.session_data == "collection_learning":
                self.collection_learning()

            elif self.session_data == "show_answer":
                self.show_answer()

            elif self.session_data in ("correct_answer", "wrong_answer"):
                if self.session_data == "correct_answer":
                    self._difficulty_calculation(True)
                else:
                    self._difficulty_calculation(False)

                self.collection_learning()

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

            elif self.session_data in ("edit_name", "edit_description"):
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

    @Bot.collection_existence_check
    def collection_learning(self) -> None:
        """Issue a card for study to the user.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            collection_cards = select.collection_cards(self.user_id, self.key)

        if len(collection_cards) < 1:
            Errors.empty_collection(self.callback_id, self.locale)
        else:
            self.next_card()

    @Bot.collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def next_card(self) -> None:
        """Get the next card for training.
        """

        with Select("bot_collections") as select:
            collection_cards = select.collection_cards(self.user_id, self.key)

        weak_card = sorted(collection_cards, key=lambda x: x[8])[0]
        self.title = weak_card[4]
        self.menu = CardTemplates.learning_menu(
            self.locale, self.key, weak_card[3]
        )
        self.parse_mode = "Markdown"

    @Bot.card_and_collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
    def show_answer(self) -> None:
        """Show card description.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_collections") as select:
            self.title = Tools.text_appearance(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "description"
                )
            )

        self.menu =  CardTemplates.answer_menu(
            self.locale, self.key, self.card_key
        )
        self.parse_mode = "Markdown"

    @Bot.card_and_collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
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
                self.user_id,
                self.key,
                self.card_key,
                self.message_text,
                "🚫",
                int(datetime.now().timestamp())
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

    @Bot.card_and_collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
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

    @Bot.card_and_collection_existence_check
    @Bot.edit_message
    @Bot.answer_callback_query
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

    @Bot.card_and_collection_existence_check
    @Bot.edit_message
    @Bot.send_message
    def change_attribute(self) -> None:
        """Change any attribute of the card.
        """

        attribute = self.session_data.split("_")[1]

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

    @Bot.card_and_collection_existence_check
    @Bot.send_message
    @Bot.answer_callback_query
    def _edit_attribute_session(self, attribute) -> None:
        key = f"UsrCaRSe/edit_{attribute}/{self.key}/{self.card_key}"

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message(
                f"edit_card_{attribute}", self.locale
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

    def _change_level(self) -> None:
        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id,
                self.key,
                "page_level",
                int(self.session_data[-2:])
            )

        self.cards()

    @Bot.card_and_collection_existence_check
    def _difficulty_calculation(self, answer: bool) -> None:
        with Select("bot_collections") as select:
            difficulty = select.card_attribute(
                self.user_id, self.key, self.card_key, "difficulty"
            )
            repetition = select.card_attribute(
                self.user_id, self.key, self.card_key, "repetition"
            )
            easy_factor = select.card_attribute(
                self.user_id, self.key, self.card_key, "easy_factor"
            )

        if answer:
            if difficulty < 5:
                difficulty += 1
        else:
            if difficulty > 0:
                difficulty -= 1

        next_repetition_date, easy_factor = Tools.memorization_algorithm(
            repetition, difficulty, easy_factor
        )
        current_time = int(datetime.now().timestamp())
        next_repetition_date += current_time
        next_repetition_date = min(current_time + 172800, next_repetition_date)

        with Update("bot_collections") as update:
            update.card_attribute(
                self.user_id, self.key, self.card_key,
                "difficulty", difficulty
            )
            update.card_attribute(
                self.user_id, self.key, self.card_key,
                "repetition", repetition + 1
            )
            update.card_attribute(
                self.user_id, self.key, self.card_key,
                "next_repetition_date", next_repetition_date
            )
            update.card_attribute(
                self.user_id, self.key, self.card_key,
                "easy_factor", easy_factor
            )

    def _session_initialization(self) -> None:
        if self.message:
            self.user_id = self.message["chat"]["id"]
            self.message_text = self.message["text"]
            self.user_date = self.message["date"]

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
