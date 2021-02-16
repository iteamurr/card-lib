"""
    Module responsible for working with the object "Card".
"""

from typing import Any
from typing import Callable
from typing import Optional

from ..tools import API
from ..tools import Tools
from ..database import Select
from ..database import Insert
from ..database import Update


def existence_check(func: Callable) -> Callable:
    """Decorator that checks if the collection and card exist in the database.
    """

    def wrapper_func(self, *args, **kwargs):
        with Select("bot_cards") as select:
            card_exists = bool(
                select.card_attribute(
                    self.user_id, self.key, self.card_key, "name"
                )
            )

        with Select("bot_collections") as select:
            collection_exists = bool(
                select.collection_attribute(
                    self.user_id, self.key, "name"
                )
            )

        if collection_exists and card_exists:
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
class Card:
    """Class defining the card object.

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
        """Card-related user actions handler.
        """

        if self.session_data == "info":
            self.info()

    def info(self) -> None:
        """Card Information menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CaRSe",
                    data="edit_name",
                    name=f"edit_name/{self.key}/{self.card_key}",
                    locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRSe",
                    data="edit_description",
                    name=f"edit_description/{self.key}/{self.card_key}",
                    locale=locale
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
            name = select.card_attribute(
                self.user_id, self.key, self.card_key, "name"
            )
            description = select.card_attribute(
                self.user_id, self.key, self.card_key, "description"
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

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_header = session[0]
        self.session_data = session[1]
        self.key = session[2]
        self.card_key = session[3]


class Cards:
    """Class that defines cards objects.

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
        """Cards-related user actions handler.
        """

        if self.session_data == "collection_cards":
            self.cards()
        elif self.session_data == "add_card":
            self.add_card_session()

    def cards(self, cards_in_page: Optional[int] = 8) -> None:
        """Show all user cards.

        Args:
            cards_in_page: Number of cards per page.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CaRsSe", data="add_card",
                    name=f"add_card/{self.key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{self.key}", locale=locale
                )
            )
        )

        with Select("bot_collections") as select:
            level = select.collection_attribute(
                self.user_id, self.key, "page_level"
            )
            collection_name = select.collection_attribute(
                self.user_id, self.key, "name"
            )
            cards_list = select.collection_cards(self.user_id, self.key)

        with Select("bot_messages") as select:
            title = select.bot_message(
                "cards", locale
            ).format(collection_name)

        navigation = Tools.navigation_creator(len(cards_list), level)

        bord = slice(cards_in_page*level, cards_in_page*(level + 1))
        card_buttons = Tools.button_list_creator(
            list_of_items=cards_list[bord], header="CoLSe", data="info"
        )

        all_buttons = (navigation + card_buttons + buttons)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(all_buttons)
        )
        API.answer_callback_query(self.callback_id)

    def add_card_session(self) -> None:
        """Change current user session to card creation session.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message("create_card", locale)

        session = f"UsrCaRSe/create/{self.key}/{Tools.new_card_key()}"

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", session)

        API.send_message(self.user_id, text)
        API.answer_callback_query(self.callback_id)

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_data = session[1]
        self.key = session[2]


class CardSession:
    """Class that handles the card session.

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
            self.new_card()

    def new_card(self) -> None:
        """Create a new user card.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            cards = select.user_attribute(self.user_id, "cards")

        buttons = (
            (
                Tools.button_template(
                    header="CaRSe",
                    data=f"info/{self.key}/{self.card_key}",
                    name=self.message_text
                )
            )
        )

        with Select("bot_collections") as select:
            collection_cards = select.collection_attribute(
                self.user_id, self.key, "cards"
            )

        with Select("bot_messages") as select:
            text = select.bot_message("new_card", locale)

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

        API.send_message(
            self.user_id, text,
            keyboard=API.inline_keyboard(buttons)
        )

    def _session_initialization(self):
        user_session = Tools.get_session(self.user_id)

        if user_session:
            session = Tools.define_session(user_session)
            self.session_data = session[1]
            self.key = session[2]
            self.card_key = session[3]
