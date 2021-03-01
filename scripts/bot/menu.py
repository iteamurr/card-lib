"""
    Module with basic, non-changing user menus.
"""

from typing import Any

from ..tools import API
from ..database import Select
from ..shortcuts import MenuTemplates


class SendMenu:
    """Sending basic user menus.
    """

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def private_office(self) -> None:
        """Send a user's Private Office.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        menu = MenuTemplates.private_office_template(locale)
        API.send_message(
            self.user_id, title, keyboard=API.inline_keyboard(menu)
        )

    def settings(self) -> None:
        """Send a user's Settings menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        menu = MenuTemplates.settings_template(locale)
        API.send_message(
            self.user_id, title, keyboard=API.inline_keyboard(menu)
        )


class SwitchMenu:
    """User menu switching.
    """

    def __init__(self, callback_query: dict[str, Any]) -> None:
        self.callback_id = callback_query["id"]
        self.user_id = callback_query["from"]["id"]
        self.message_id = callback_query["message"]["message_id"]

    def private_office(self) -> None:
        """Switch menu to the user's Private Office.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        menu = MenuTemplates.private_office_template(locale)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def settings(self) -> None:
        """Switch menu to the user's Settings.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        menu = MenuTemplates.settings_template(locale)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu)
        )
        API.answer_callback_query(self.callback_id)

    def locale_settings(self) -> None:
        """Switch menu to the user's Locale Settings.
        """

        locale_list = {"en": "English", "ru": "Русский"}

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message(
                "current_language", locale
            ).format(locale_list[locale])

        menu = MenuTemplates.locale_settings_template(locale)
        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=API.inline_keyboard(menu), parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)
