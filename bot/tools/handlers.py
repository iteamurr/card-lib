"""
    Implementing user action handlers
"""

from typing import Any

from ..tools.helpers import Tools
from ..template.menu import Menu
from ..template.card import Card
from ..template.collection import Collection


class CommandHandler:
    """Bot command handler.

    Attributes:
        message: An object containing
                 all information about the user's message.
    """

    def __init__(self, message: dict[str, Any]) -> None:
        # The menu that will be sent to the user.
        self.menu = None

        # Contents of the incoming message.
        self.message = message
        self.user_id = None
        self.command = None
        self.entity = None

        # Retrieving details from a user's message.
        self._session_initialization()

    def handler(self) -> None:
        """Handler defines the command and sends the menu.
        """

        if self.entity == "bot_command":
            self.menu = Menu()

            if "/start" in self.command:
                self._select_private_office_menu()

            elif "/settings" in self.command:
                self._select_settings_menu()

            elif "/collections" in self.command:
                self._select_collections_menu()

            else:
                self._undefined_command()

            self.menu.send(self.user_id)

    def _session_initialization(self) -> None:
        self.user_id = self.message["chat"]["id"]
        self.command = self.message["text"]
        self.entity = self.message["entities"][0]["type"]

    def _select_private_office_menu(self):
        if not Tools.check_user_existence(self.user_id):
            Tools.add_new_user(self.message)

        self.menu.select(self.menu.private_office)

    def _select_settings_menu(self):
        self.menu.select(self.menu.settings)

    def _select_collections_menu(self):
        self.menu.select(self.menu.collections)

    def _undefined_command(self):
        self._select_private_office_menu()


class CallbackQueryHandler:
    """Handle an incoming callback query
       from a callback button in an inline keyboard.

    Attributes:
        callback_query: An object containing
                        all information about the user's query.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        # Menu that will replace the current user menu.
        self.menu = None

        # User and request information.
        self.callback_query = callback_query
        self.data = None
        self.user_id = None

        # Information about the current session.
        self.session_header = None
        self.session_data = None

        self._session_initialization()

    def handler(self) -> None:
        """Handler delegates control to other processes or switches menu.
        """

        if self.session_header == "CaRSe":
            self._card_handler()

        elif self.session_header == "CoLSe":
            self._collection_handler()

        else: # "MnSe"
            self._menu_handler()

    def _menu_handler(self):
        self.menu = Menu()

        if self.session_data == "private_office":
            self._select_private_office_menu()

        elif self.session_data == "settings":
            self._select_settings_menu()

        elif "locale" in self.session_data:
            self._select_locale_settings_menu()

        else:
            self._undefined_menu()

        self.menu.edit(self.callback_query)

    def _session_initialization(self):
        self.data = self.callback_query["data"]
        self.user_id = self.callback_query["from"]["id"]

        session = Tools.define_session(self.data)
        self.session_header = session[0]
        self.session_data = session[1]

    def _card_handler(self):
        card = Card(callback_query=self.callback_query)
        card.handler()

    def _collection_handler(self):
        collection = Collection(callback_query=self.callback_query)
        collection.handler()

    def _select_private_office_menu(self):
        self.menu.select(self.menu.private_office)

    def _select_settings_menu(self):
        self.menu.select(self.menu.settings)

    def _select_locale_settings_menu(self):
        if self.session_data != "locale_settings":
            Tools.change_locale(self.user_id, self.session_data)

        self.menu.select(self.menu.locale_settings)

    def _undefined_menu(self):
        self._select_private_office_menu()


class SessionHandler:
    """User session handler.

    Attributes:
        message: An object containing all information
                 about the user's message.
    """

    def __init__(self, message: dict[str, Any]) -> None:
        self.message = message
        self.session_header = None
        self.session_action = None

        self._session_initialization()

    def handler(self) -> None:
        """Session defining handler.
        """

        if self.session_header:
            if self.session_header == "UsrCoLSe":
                self._collection_handler()

            elif self.session_header == "UsrCaRSe":
                self._card_handler()

    def _session_initialization(self):
        user_id = self.message["chat"]["id"]
        user_session = Tools.get_session(user_id)

        if user_session:
            session_data = Tools.define_session(user_session)
            self.session_header = session_data[0]

    def _collection_handler(self):
        collection = Collection(message=self.message)
        collection.handler()

    def _card_handler(self):
        card = Card(message=self.message)
        card.handler()
