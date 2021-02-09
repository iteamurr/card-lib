"""
    Module that determines bot's response to a user action.
"""

from .tools import Tools
from .database import Select
from .menus import SendMenu
from .menus import SwitchMenu
from .collection import Collection
from .collection import Collections
from .collection import CollectionSession
from .card import Card
from .card import Cards
from .card import CardSession


class CommandHandler:
    """Bot command handler.
    """

    def __init__(self, message):
        self.message = message
        self._user_id = message["chat"]["id"]
        self._message_text = message["text"]
        self._message_entities = message["entities"][0]["type"]

        self._send_menu = None

    def handler(self):
        """Handler defines the command and sends the menu.
        """

        if self._message_entities == "bot_command":
            self._send_menu = SendMenu(self._user_id)

            if "/start" in self._message_text:
                self._private_office_menu()

            elif "/settings" in self._message_text:
                self._settings_menu()

            # TODO: command nonexistence warning
            else:
                pass

    def _private_office_menu(self):
        Tools.check_new_user(self.message)

        self._send_menu.private_office()

    def _settings_menu(self):
        self._send_menu.settings()


class CallbackQueryHandler:
    """Handle an incoming callback query
       from a callback button in an inline keyboard.
    """

    def __init__(self, callback_query):
        self.callback_query = callback_query
        self._user_id = callback_query["from"]["id"]

        session = Tools.get_session(callback_query["data"])
        self._session_header = session[0]
        self._session_data = session[1]

        self._switch_menu = None

    def handler(self):
        """Handler delegates control to other processes or switches menu.
        """

        if self._session_header == "CaRSe":
            self._card_handler()

        elif self._session_header == "CaRsSe":
            self._cards_handler()

        elif self._session_header == "CoLSe":
            self._collection_handler()

        elif self._session_header == "CoLsSe":
            self._collections_handler()

        else: # "MnSe"
            self._switch_menu = SwitchMenu(self.callback_query)

            if self._session_data == "private_office":
                self._private_office_menu()

            elif self._session_data == "settings":
                self._settings_menu()

            elif "locale" in self._session_data:
                self._locale_settings_menu()

            elif "level" in self._session_data:
                self._level_menu()

            # TODO: handling an unrecognized menu
            else:
                pass

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
        self._switch_menu.private_office()

    def _settings_menu(self):
        self._switch_menu.settings()

    def _locale_settings_menu(self):
        if self._session_data != "locale_settings":
            Tools.change_locale(self._user_id, self._session_data)

        self._switch_menu.locale_settings()

    def _level_menu(self):
        Tools.change_level(self._user_id, self._session_data)

        self._collections_handler()


class SessionHandler:
    """User session handler.
    """

    def __init__(self, message):
        self._message_text = message["text"]
        self._user_id = message["chat"]["id"]

        with Select("bot_users") as select:
            user_session = select.user_attribute(self._user_id, "session")

        self._session = None
        if user_session:
            session_data = Tools.get_session(user_session)

            if len(session_data) > 1:
                self._session = session_data[0]
                self._action = session_data[1]

    def handler(self):
        """Session defining handler.
        """

        if self._session:
            if self._session == "UsrCoLSe":
                self._collection_session_handler()

            elif self._session == "UsrCaRSe":
                self._card_session_handler()

    def _collection_session_handler(self):
        collection_session = CollectionSession(self._user_id,
                                               self._message_text)
        collection_session.handler(self._action)

    def _card_session_handler(self):
        card_session = CardSession(self._user_id, self._message_text)
        card_session.handler(self._action)
