"""
    Module that determines bot's response to a user action.
"""

from typing import Any

from .bot.menu import SendMenu
from .bot.menu import SwitchMenu
from .bot.collection import Collection
from .bot.collection import Collections
from .bot.collection import CollectionSession
from .bot.card import Card
from .bot.card import Cards
from .bot.card import CardSession
from .tools import Tools


class CommandHandler:
    """Bot command handler.

    Attributes:
        message: An object containing all information
            about the user's message.
    """

    def __init__(self, message: dict[str, Any]) -> None:
        self.menu = None

        self.message = message
        self.command = message["text"]
        self.user_id = message["chat"]["id"]
        self.entity = message["entities"][0]["type"]

    def handler(self) -> None:
        """Handler defines the command and sends the menu.
        """

        if self.entity == "bot_command":
            self.menu = SendMenu(self.user_id)

            if "/start" in self.command:
                self._private_office_menu()

            elif "/settings" in self.command:
                self._settings_menu()

            elif "/collections" in self.command:
                self._collections_menu()

            else:
                self._undefined_command()

    def _private_office_menu(self):
        if not Tools.check_user_existence(self.user_id):
            Tools.add_new_user(self.message)

        self.menu.private_office()

    def _settings_menu(self):
        self.menu.settings()

    def _collections_menu(self):
        self.menu.collections()

    def _undefined_command(self):
        pass


class CallbackQueryHandler:
    """Handle an incoming callback query
       from a callback button in an inline keyboard.

    Attributes:
        callback_query: An object containing
            all information about the user's query.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        self.menu = None

        self.callback_query = callback_query
        self.data = callback_query["data"]
        self.user_id = callback_query["from"]["id"]

        self.session_header = None
        self.session_data = None

        self._session_initialization()

    def handler(self) -> None:
        """Handler delegates control to other processes or switches menu.
        """

        if self.session_header == "CaRSe":
            self._card_handler()

        elif self.session_header == "CaRsSe":
            self._cards_handler()

        elif self.session_header == "CoLSe":
            self._collection_handler()

        elif self.session_header == "CoLsSe":
            self._collections_handler()

        else: # "MnSe"
            self.menu = SwitchMenu(self.callback_query)

            if self.session_data == "private_office":
                self._private_office_menu()

            elif self.session_data == "settings":
                self._settings_menu()

            elif "locale" in self.session_data:
                self._locale_settings_menu()

            else:
                self._undefined_menu()

    def _session_initialization(self):
        session = Tools.define_session(self.data)
        self.session_header = session[0]
        self.session_data = session[1]

    def _card_handler(self):
        card = Card(self.callback_query)
        card.handler()

    def _cards_handler(self):
        cards = Cards(self.callback_query)
        cards.handler()

    def _collection_handler(self):
        collection = Collection(self.callback_query)
        collection.handler()

    def _collections_handler(self):
        collections = Collections(self.callback_query)
        collections.handler()

    def _private_office_menu(self):
        self.menu.private_office()

    def _settings_menu(self):
        self.menu.settings()

    def _locale_settings_menu(self):
        if self.session_data != "locale_settings":
            Tools.change_locale(self.user_id, self.session_data)

        self.menu.locale_settings()

    def _undefined_menu(self):
        pass


class SessionHandler:
    """User session handler.

    Attributes:
        message: An object containing all information
            about the user's message.
    """

    def __init__(self, message: dict[str, Any]) -> None:
        self.message_text = message["text"]
        self.user_id = message["chat"]["id"]

        self.session_header = None
        self.session_action = None

        self._session_initialization()

    def handler(self) -> None:
        """Session defining handler.
        """

        if self.session_header:
            if self.session_header == "UsrCoLSe":
                self._collection_session_handler()

            elif self.session_header == "UsrCaRSe":
                self._card_session_handler()

            else:
                self._undefined_session()

    def _session_initialization(self):
        user_session = Tools.get_session(self.user_id)

        if user_session:
            session_data = Tools.define_session(user_session)
            self.session_header = session_data[0]

    def _collection_session_handler(self):
        session = CollectionSession(self.user_id, self.message_text)
        session.handler()

    def _card_session_handler(self):
        session = CardSession(self.user_id, self.message_text)
        session.handler()

    def _undefined_session(self):
        pass
