"""
    Module with basic, non-changing user menus.
"""
# pylint: disable=unsubscriptable-object


from typing import Any
from typing import Optional

from ..tools import Bot
from ..tools import Tools
from ..database import Select
from ..shortcuts import MenuTemplates
from ..shortcuts import CollectionTemplates


class SendMenu:
    """Sending basic user menus.
    """

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

        self.locale = None
        self.title = None
        self.menu = None
        self.parse_mode = None

    @Bot.send_message
    def private_office(self) -> None:
        """Send a user's Private Office.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("private_office", self.locale)

        self.menu = MenuTemplates.private_office_template(self.locale)

    @Bot.send_message
    def settings(self) -> None:
        """Send a user's Settings menu.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("settings", self.locale)

        self.menu = MenuTemplates.settings_template(self.locale)

    @Bot.send_message
    def collections(self, per_page: Optional[int] = 8) -> None:
        """Send all user collections.

        Args:
            per_page: Number of collections per page.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")
            level = select.user_attribute(self.user_id, "page_level")

        with Select("bot_messages") as select:
            self.title = select.bot_message("collections", self.locale)

        with Select("bot_collections") as select:
            collections_list = select.user_collections(self.user_id)

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


class SwitchMenu:
    """User menu switching.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        self.callback_id = callback_query["id"]
        self.user_id = callback_query["from"]["id"]
        self.message_id = callback_query["message"]["message_id"]

        self.locale = None
        self.title = None
        self.menu = None
        self.parse_mode = None

    @Bot.edit_message
    @Bot.answer_callback_query
    def private_office(self) -> None:
        """Switch menu to the user's Private Office.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("private_office", self.locale)

        self.menu = MenuTemplates.private_office_template(self.locale)

    @Bot.edit_message
    @Bot.answer_callback_query
    def settings(self) -> None:
        """Switch menu to the user's Settings.
        """

        with Select("bot_users") as select:
            self.locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            self.title = select.bot_message("settings", self.locale)

        self.menu = MenuTemplates.settings_template(self.locale)

    @Bot.edit_message
    @Bot.answer_callback_query
    def locale_settings(self) -> None:
        """Switch menu to the user's Locale Settings.
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
