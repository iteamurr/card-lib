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
from ..database import Delete
from ..shortcuts import CardTemplates


def existence_check(func: Callable) -> Callable:
    """Decorator that checks if the collection and card exist in the database.
    """

    def wrapper_func(self, *args, **kwargs):
        card_exists = Tools.check_card_existence(
            self.user_id, self.key, self.card_key
        )

        collection_exists = Tools.check_collection_existence(
            self.user_id, self.key
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

        self.session_header = None
        self.session_data = None
        self.key = None
        self.card_key = None

        self._session_initialization()

    @existence_check
    def handler(self) -> None:
        """Card-related user actions handler.
        """

        if "edit" in self.session_data:
            if self.session_data == "edit_name":
                self._edit_attribute_session("name")

            elif self.session_data == "edit_desc":
                self._edit_attribute_session("description")

        elif "delete" in self.session_data:
            if self.session_data == "confirm_delete":
                self.delete_confirmation()

            else:
                self.delete_menu()

        else: # info
            self.info()

    def info(self) -> None:
        """Card Information menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

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

        menu = CardTemplates.info_template(locale, self.key, self.card_key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)

    def delete_menu(self) -> None:
        """Delete card menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("card_delete_confirm", locale)

        menu = CardTemplates.delete_menu_template(
            locale, self.key, self.card_key
        )
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def delete_confirmation(self) -> None:
        """Card deletion confirmation menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
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
            title = select.bot_message("card_deleted", locale)

        menu = CardTemplates.delete_confirmation_template(locale, self.key)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_header = session[0]
        self.session_data = session[1]
        self.key = session[2]
        self.card_key = session[3]

    def _edit_attribute_session(self, attribute):
        key = f"UsrCaRSe/edit_{attribute}/{self.key}/{self.card_key}"

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            text = select.bot_message(f"edit_card_{attribute}", locale)

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", key)
            update.user_attribute(self.user_id, "menu_id", self.message_id)

        API.send_message(self.user_id, text)
        API.answer_callback_query(self.callback_id)


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

        self.session_data = None
        self.key = None

        self._session_initialization()

    def handler(self) -> None:
        """Cards-related user actions handler.
        """

        if self.session_data == "collection_cards":
            self.cards()

        elif self.session_data == "add_card":
            self.add_card_session()

        elif "level" in self.session_data:
            self._change_level()

        else:
            self._undefined_menu()

    def cards(self, per_page: Optional[int] = 8) -> None:
        """Show all user cards.

        Args:
            per_page: Number of cards per page.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

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

        navigation = Tools.navigation_creator(
            "CaRsSe", len(cards_list),
            level=level, key=self.key, per_page=per_page
        )
        items = cards_list[per_page*level:per_page*(level + 1)]
        card_buttons = Tools.button_list_creator(
            "card", "CaRSe", "info", items
        )
        buttons = CardTemplates.cards_template(locale, self.key)
        menu = (navigation + card_buttons + buttons)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
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

    def _change_level(self):
        with Update("bot_collections") as update:
            update.collection_attribute(
                self.user_id, self.key,
                "page_level", int(self.session_data[-2:])
            )

        self.cards()

    def _undefined_menu(self):
        pass


class CardSession:
    """Class that handles the card session.

    Attributes:
        user_id: Unique identifier for the target user.
        message_text: User's message text.
    """

    def __init__(self, user_id: int, message_text: str) -> None:
        self.user_id = user_id
        self.message_text = message_text

        self.session_data = None
        self.key = None
        self.card_key = None

        self._session_initialization()

    def handler(self) -> None:
        """Handler taking action from session.
        """

        if self.session_data == "create":
            self.new_card()

        elif self.session_data in ("edit_name", "edit_description"):
            self.change_card_attribute()

    def new_card(self) -> None:
        """Create a new user card.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            cards = select.user_attribute(self.user_id, "cards")

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

        menu = CardTemplates.new_card_template(
            self.key, self.card_key, self.message_text
        )
        API.send_message(
            self.user_id, text, keyboard=API.inline_keyboard(menu)
        )

    def change_card_attribute(self) -> None:
        """Change any attribute of the card.
        """

        attribute = self.session_data.split("_")[1]

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")
            menu_id = select.user_attribute(self.user_id, "menu_id")

        with Update("bot_collections") as update:
            update.card_attribute(
                self.user_id, self.key, self.card_key,
                attribute, self.message_text
            )

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_messages") as select:
            text = select.bot_message(f"card_{attribute}_changed", locale)

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

        menu = CardTemplates.info_template(locale, self.key, self.card_key)
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
            self.card_key = session[3]
