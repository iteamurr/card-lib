"""
    Module with basic, non-changing user menus.
"""

from ..tools import API
from ..tools import Tools
from ..database import Select


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

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="collections", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="settings",
                    name="settings", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        keyboard = API.inline_keyboard(buttons)
        API.send_message(self.user_id, title, keyboard=keyboard)

    def settings(self) -> None:
        """Send a user's Settings menu.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="MnSe", data="locale_settings",
                    name="locale_settings", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="back",
                    name="private_office", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        keyboard = API.inline_keyboard(buttons)
        API.send_message(self.user_id, title, keyboard=keyboard)


class SwitchMenu:
    """User menu switching.
    """

    def __init__(self, callback_query):
        self.callback_id = callback_query["id"]
        self.user_id = callback_query["from"]["id"]
        self.message_id = callback_query["message"]["message_id"]

    def private_office(self) -> None:
        """Switch menu to the user's Private Office.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="collections", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="settings",
                    name="settings", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        keyboard = API.inline_keyboard(buttons)
        API.edit_message(
            self.user_id, self.message_id,
            title, keyboard=keyboard
        )
        API.answer_callback_query(self.callback_id)

    def settings(self) -> None:
        """Switch menu to the user's Settings.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        buttons = (
            (
                Tools.identified_button_template(
                    header="MnSe", data="locale_settings",
                    name="locale_settings", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="back",
                    name="private_office", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        keyboard = API.inline_keyboard(buttons)
        API.edit_message(
            self.user_id, self.message_id,
            title, keyboard=keyboard
        )
        API.answer_callback_query(self.callback_id)

    def locale_settings(self) -> None:
        """Switch menu to the user's Locale Settings.
        """

        with Select("bot_users") as select:
            locale = select.user_attribute(self.user_id, "locale")

        locale_list = {"en": "English", "ru": "Русский"}
        buttons = (
            (
                Tools.identified_button_template(
                    header="MnSe", data="change_language_to_en",
                    name="en_locale", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="change_language_to_ru",
                    name="ru_locale", locale=locale
                )
            ),
            (
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name="private_office", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="back",
                    name="settings", locale=locale
                )
            )
        )

        with Select("bot_messages") as select:
            title = select.bot_message("current_language", locale)

        title = title.format(locale_list[locale])
        keyboard = API.inline_keyboard(buttons)

        API.edit_message(
            self.user_id, self.message_id, title,
            keyboard=keyboard, parse_mode="MarkdownV2"
        )
        API.answer_callback_query(self.callback_id)
