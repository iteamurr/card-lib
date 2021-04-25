"""
    Implementation of tools for working with the ``Menu`` object.
"""

from typing import Any
from typing import Callable

from ..tools.helpers import Bot
from ..tools.helpers import Tools
from ..tools.database import Select
from ..tools.database import Update
from ..shortcuts import MenuTemplates
from ..shortcuts import CollectionTemplates
from ..config import bot_settings


class Menu:
    """Class defining the ``Menu`` object.
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

        # Menu options.
        self.locale = None
        self.parse_mode = None

        # Send/Edit menu options.
        self.message_menu = None
        self.text = None
        self.disable_web_page_preview = False

        # Edit menu options.
        self.menu = None
        self.title = None

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
        self.message_menu = self.menu

    @Bot.edit_message
    @Bot.answer_callback_query
    def edit(self, callback_query: dict[str, Any]) -> None:
        """Change the current menu to the menu with the selected template.

        Args:
            callback_query: An object containing
                            all information about the user's query.
        """

        self.callback_query = callback_query
        self._callback_query_init()
        self.selected_menu()
        self.title = self.text

    def private_office(self) -> None:
        """User private office template.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("private_office", self.locale)

        self.menu = MenuTemplates.private_office_template(self.locale)

    def start(self) -> None:
        """User start text template.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("start", self.locale)

        self.parse_mode = "Markdown"
        self.disable_web_page_preview = True

        self.menu = MenuTemplates.private_office_template(self.locale)

    def settings(self) -> None:
        """User settings template.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("settings", self.locale)

        self.menu = MenuTemplates.settings_template(self.locale)

    def locale_settings(self) -> None:
        """User locale settings template.
        """

        locale_list = {"en": "English", "ru": "Русский"}

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message(
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
            self.text = select.bot_message("collections", self.locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self.user_id)

        per_page = bot_settings["collections_per_page"]
        navigation = Tools.navigation_creator(
            header="CoLsSe",
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

    def cancel(self) -> None:
        """Cancel current operation.
        """

        with Update("bot_users") as update:
            update.user_attribute(self.user_id, "session", None)

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.text = select.bot_message("cancel", self.locale)

    def _callback_query_init(self):
        self.callback_id = self.callback_query["id"]
        self.user_id = self.callback_query["from"]["id"]
        self.message_id = self.callback_query["message"]["message_id"]
