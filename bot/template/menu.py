"""
    Module with basic, non-changing user menus.
"""

from typing import Any
from typing import Callable

from ..tools.helpers import Bot
from ..tools.helpers import Tools
from ..tools.database import Select
from ..shortcuts import MenuTemplates
from ..shortcuts import CollectionTemplates
from ..config import bot_settings


# pylint: disable=too-many-instance-attributes
class Menu:
    """A class representing the user menu object.
    """

    def __init__(self) -> None:
        # Variables responsible for callback query.
        self.callback_query = None
        self.message_id = None
        self.callback_id = None

        self.callback_query_text = None
        self.show_alert = None

        # Variables needed to work with the menu.
        self.user_id = None
        self.selected_menu = self.private_office

        # Send/Edit menu options.
        self.menu = None
        self.locale = None
        self.title = None
        self.parse_mode = None

    def select(self, menu: Callable) -> None:
        """Select a menu to send/edit.

        Args:
            menu: Menu to be used as template.
        """

        self.selected_menu = menu

    @Bot.send_message
    def send(self, user_id: int) -> None:
        """Send message with selected menu template.

        Args:
            user_id: Unique identifier of the target user.
        """

        self.user_id = user_id
        self.selected_menu()

    @Bot.edit_message(answer_callback=True)
    def edit(self, callback_query: dict[str, Any]) -> None:
        """Change the current menu to the menu with the selected template.

        Args:
            callback_query
        """

        self.callback_query = callback_query
        self._callback_query_init()
        self.selected_menu()

    def private_office(self) -> None:
        """User private office template.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("private_office", self.locale)

        self.menu = MenuTemplates.private_office_template(self.locale)

    def settings(self) -> None:
        """User settings template.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("settings", self.locale)

        self.menu = MenuTemplates.settings_template(self.locale)

    def locale_settings(self) -> None:
        """User locale settings template.
        """

        locale_list = {"en": "English", "ru": "Русский"}

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message(
                "current_language", self.locale
            ).format(locale_list[self.locale])

        self.menu = MenuTemplates.locale_settings_template(self.locale)
        self.parse_mode = "MarkdownV2"

    def collections(self) -> None:
        """User collections template.
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
            "CoLsSe",
            len(collections_list),
            level=level,
            per_page=per_page
        )
        collection_buttons = Tools.button_list_creator(
            "collection",
            "CoLSe",
            "info",
            collections_list[per_page*level:per_page*(level + 1)]
        )
        buttons = CollectionTemplates.collections_template(self.locale)
        self.menu = (navigation + collection_buttons + buttons)

    def _callback_query_init(self):
        self.callback_id = self.callback_query["id"]
        self.user_id = self.callback_query["from"]["id"]
        self.message_id = self.callback_query["message"]["message_id"]