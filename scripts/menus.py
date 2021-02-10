"""
    Module with basic, non-changing user menus.
"""

from .tools import API
from .tools import Tools
from .database import Select


class SendMenu:
    """Sending basic user menus.
    """

    def __init__(self, user_id):
        self._user_id = user_id

    def private_office(self):
        """Send a user's Private Office.
        """

        template = [
            [
                ["collections", "CoLsSe/collections"],
                ["settings", "MnSe/settings"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)
        API.send_message(self._user_id, title, keyboard=keyboard)

    def settings(self):
        """Send a user's Settings menu.
        """

        template = [
            [
                ["locale_settings", "MnSe/locale_settings"]
            ],
            [
                ["back", "MnSe/private_office"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)
        API.send_message(self._user_id, title, keyboard=keyboard)


class SwitchMenu:
    """User menu switching.
    """

    def __init__(self, callback_query):
        self._callback_id = callback_query["id"]
        self._user_id = callback_query["from"]["id"]
        self._message_id = callback_query["message"]["message_id"]

    def private_office(self):
        """Switch menu to the user's Private Office.
        """

        template = [
            [
                ["collections", "CoLsSe/collections"],
                ["settings", "MnSe/settings"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("private_office", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def settings(self):
        """Switch menu to the user's Settings.
        """

        template = [
            [
                ["locale_settings", "MnSe/locale_settings"]
            ],
            [
                ["back", "MnSe/private_office"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("settings", locale)

        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id,
                         title, keyboard=keyboard)
        API.answer_callback_query(self._callback_id)

    def locale_settings(self):
        """Switch menu to the user's Locale Settings.
        """

        locale_list = {"en": "English", "ru": "Русский"}
        template = [
            [
                ["change_language_to_en", "MnSe/en_locale"],
                ["change_language_to_ru", "MnSe/ru_locale"]
            ],
            [
                ["main", "MnSe/private_office"],
                ["back", "MnSe/settings"]
            ]
        ]

        with Select("bot_users") as select:
            locale = select.user_attribute(self._user_id, "locale")

        with Select("bot_messages") as select:
            title = select.bot_message("current_language", locale)

        title = title.format(locale_list[locale])
        buttons = Tools.button_identifier(template, locale)
        keyboard = API.inline_keyboard(*buttons)

        API.edit_message(self._user_id, self._message_id, title,
                         keyboard=keyboard, parse_mode="MarkdownV2")
        API.answer_callback_query(self._callback_id)
