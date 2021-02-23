"""
    Module with additional tools for working with a bot.
"""

import re
import random
import string
from math import ceil
from typing import Any
from typing import Union
from typing import Optional
import requests

from .config import telegram
from .database import Select
from .database import Insert
from .database import Update


# Variable defining the type of button template.
ButtonTemplate = list[str, str]

# Variable defining the type of layer template.
LayerTemplate = list[ButtonTemplate, ...]

# Variable defining the type of menu template.
MenuTemplate = list[LayerTemplate, ...]


# pylint: disable=unsubscriptable-object
class API:
    """Working with the Telegram API.
    """

    @staticmethod
    def send_message(
        chat_id: int,
        text: str,
        keyboard: Optional[dict[str, Any]] = None,
        parse_mode: Optional[str] = None
    ) -> None:
        """Send a text message with additional options.

        Args:
            chat_id: Unique identifier for the target chat.
            text: Text of the message to be sent.
            keyboard: Additional message interface in the form of buttons.
                Defaults to None.
            parse_mode: Mode for parsing entities in the message text.
                Defaults to None.
        """

        url = telegram["url"].format(telegram["token"], "sendMessage")
        body = {"chat_id": chat_id, "text": text}

        if parse_mode:
            body["parse_mode"] = parse_mode

        if keyboard:
            body = {**body, **keyboard}

        requests.post(url, json=body)

    @staticmethod
    def edit_message(
        chat_id: int,
        message_id: int,
        text: str,
        keyboard: Optional[dict[str, Any]] = None,
        parse_mode: Optional[str] = None
    ) -> None:
        """Edit bot message, to change the message text or the current menu.

        Args:
            chat_id: Unique identifier for the target chat.
            message_id: Unique message identifier.
            text: Text of the message to be sent.
            keyboard: Additional message interface in the form of buttons.
                Defaults to None.
            parse_mode: Mode for parsing entities in the message text.
                Defaults to None.
        """

        url = telegram["url"].format(telegram["token"], "editMessageText")
        body = {"chat_id": chat_id, "message_id": message_id, "text": text}

        if parse_mode:
            body["parse_mode"] = parse_mode

        if keyboard:
            body = {**body, **keyboard}

        requests.post(url, json=body)

    @staticmethod
    def answer_callback_query(
        callback_query_id: int,
        text: Optional[str] = None,
        show_alert: Optional[bool] = False
    ) -> None:
        """Send a response to a callback request
           sent from the inline keyboard.

        Args:
            callback_query_id: Unique identifier for the query to be answered.
            text: Text of the message to be sent. Defaults to None.
            show_alert: If true, then show a notification with text.
                Defaults to False.
        """

        url = telegram["url"].format(telegram["token"], "answerCallbackQuery")
        body = {"callback_query_id": callback_query_id}

        if text:
            body["text"] = text
            body["show_alert"] = show_alert

        requests.post(url, json=body)

    @staticmethod
    def inline_keyboard(menu_template: MenuTemplate) -> dict[str, Any]:
        """Create an inline keyboard wrapper.

        Args:
            menu_template: Button of an inline keyboard.

        Returns:
            keyboard: Inline keyboard wrapper.
        """

        keyboard = {
            "reply_markup": {
                "inline_keyboard": [
                ]
            }
        }

        inline_keyboard = keyboard["reply_markup"]["inline_keyboard"]
        for index, button_data in enumerate(menu_template):
            inline_keyboard.append([])

            for button_text, callback_data in button_data:
                button = {"text": button_text, "callback_data": callback_data}
                inline_keyboard[index].append(button)

        return keyboard


class Tools:
    """Additional tools for working with a bot.
    """

    @staticmethod
    def check_user_existence(user_id: int) -> bool:
        """Check if a user is in the database.

        Args:
            user_id: Unique identifier of the target user.

        Returns:
            True for success, False otherwise.
        """

        with Select("bot_users") as select:
            user_existence = select.user_attribute(user_id, "locale")
        return bool(user_existence)

    @staticmethod
    def add_new_user(message: dict[str, Any]) -> None:
        """Insert new user to database.

        Args:
            message: An object containing all information
                about the user's message.
        """

        user_id = message["chat"]["id"]
        menu_id = message["message_id"]
        username = message["from"]["username"]
        locale = Tools.define_locale(message["from"]["language_code"])

        with Insert("bot_users") as insert:
            insert.new_user(user_id, username, locale, menu_id)

    @staticmethod
    def define_locale(locale: str) -> str:
        """Define the user's locale.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.

        Returns:
            Locale for success, "en" otherwise.
        """

        locales = ["en", "ru"]
        return locale if locale in locales else "en"

    @staticmethod
    def define_session(data: str) -> list[str]:
        """Get all session details.

        Args:
            data: String containing information about the session.

        Returns:
            session: Session details list.
        """

        session = re.findall(r"([^/]+)", data)
        return session

    @staticmethod
    def get_session(user_id: int) -> Union[str, None]:
        """Get current user session.

        Args:
            user_id: Unique identifier of the target user.

        Returns:
            session: User session.
        """

        with Select("bot_users") as select:
            session = select.user_attribute(user_id, "session")
        return session

    @staticmethod
    def identified_button_template(
        header: str,
        data: str,
        name: str,
        locale: Optional[str] = "en"
    ) -> ButtonTemplate:
        """Define a name and create a button from a template.

        Args:
            header: The section the button belongs to.
            data: Data associated with the callback button.
            name: Button name.
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface. Defaults to "en".

        Returns:
            template: Identified button template.
        """

        with Select("bot_messages") as select:
            identified_name = select.bot_message(name, locale)

        template = [f"{identified_name}", f"{header}/{data}"]
        return template

    @staticmethod
    def button_template(header: str, data: str, name: str) -> ButtonTemplate:
        """Create a button from a template.

        Args:
            header: The section the button belongs to.
            data: Data associated with the callback button.
            name: Button name.

        Returns:
            template: Identified button template.
        """

        template = [f"{name}", f"{header}/{data}"]
        return template

    @staticmethod
    def layer_template(*button_templates: ButtonTemplate) -> LayerTemplate:
        """Create button layer.

        Args:
            *button_templates: The buttons from which
                the layer will be created.

        Returns:
            layer: Layer containing buttons.
        """

        layer = [*button_templates]
        return layer

    @staticmethod
    def menu_template(*layers: LayerTemplate) -> MenuTemplate:
        """Create menu from layers.

        Args:
            *layers: Layers from which the menu will be created.

        Returns:
            menu: Menu containing layers.
        """

        menu = [*layers]
        return menu

    @staticmethod
    def change_locale(user_id: int, data: str) -> None:
        """Change user locale.

        Args:
            user_id: Unique identifier of the target user.
            data: user session information.
        """

        with Update("bot_users") as update:
            update.user_attribute(user_id, "locale", data[:2])

    @staticmethod
    def change_level(user_id: int, data: str) -> None:
        """Change the page number (level) of a user.

        Args:
            user_id: Unique identifier of the target user.
            data: user session information.
        """

        with Update("bot_users") as update:
            update.user_attribute(user_id, "page_level", int(data[-2:]))

    @staticmethod
    def new_collection_key() -> str:
        """Generate a random collection key.

        Returns:
            key: Unique identifier for the collection.
        """

        first_part = random.randrange(1000, 10000)
        second_part = random.randrange(1000, 10000)
        third_part = random.choice(string.ascii_letters)

        key = f"K-{first_part}-{second_part}-{third_part}-000-CL"
        return key

    @staticmethod
    def new_card_key() -> str:
        """Generate a random card key.

        Returns:
            card_key: Unique identifier for the card.
        """

        first_part = random.randrange(1000, 10000)
        second_part = random.randrange(1000, 10000)
        third_part = random.choice(string.ascii_letters)

        card_key = f"K-{first_part}-{second_part}-{third_part}-000-CR"
        return card_key

    @staticmethod
    def button_list_creator(
        obj: str,
        list_of_items: list[Any],
        header: str,
        data: str,
        buttons_in_layer: Optional[int] = 2
    ) -> LayerTemplate:
        """Create a list of buttons for specific items.

        Args:
            obj: Session identifier for creating a list of buttons.
            list_of_items: List of items from which to create a
                list of buttons.
            header: The section the button belongs to.
            data: Data associated with the callback button.
            buttons_in_layer: Variable responsible for the number of
                buttons in one layer. Defaults to 2.

        Returns:
            buttons: List of buttons.
        """

        buttons = []
        item_list_size = len(list_of_items)
        layers = ceil(item_list_size/buttons_in_layer)

        for layer in range(layers):
            buttons.append([])
            left_border = buttons_in_layer*layer
            right_border = buttons_in_layer*(layer+1)

            for item in list_of_items[left_border:right_border]:
                if obj == "collection":
                    button_name = item[3]
                    button_data = f"{header}/{data}/{item[2]}"
                else: # obj == "card"
                    button_name = item[4]
                    button_data = f"{header}/{data}/{item[2]}/{item[3]}"

                buttons[layer].append([button_name, button_data])

        return buttons

    @staticmethod
    def navigation_creator(
        number_of_items: int,
        level: Optional[int] = 0,
        items_in_page: Optional[int] = 8,
        number_of_navigation_buttons: Optional[int] = 5
    ) -> LayerTemplate:
        """Creating menu navigation.

        Args:
            number_of_items: Total number of items being navigated.
            level: The level (page) the user is on. Defaults to 0.
            items_in_page: Number of items per page. Defaults to 8.
            number_of_navigation_buttons: Number of navigation buttons.
                Defaults to 5.

        Returns:
            buttons: List of navigation buttons.
        """

        pages = (number_of_items//items_in_page
                 + bool(number_of_items%items_in_page))

        buttons = [[]]
        if number_of_items < number_of_navigation_buttons*items_in_page + 1:
            for button in range(pages):
                page_state = ["• {} •", "{}"][button != level]

                button_name = page_state.format(button + 1)
                button_data = f"level_{'0'*(1 - button//10)}{button}"
                buttons[0].append([button_name, button_data])

        else:
            for button in range(number_of_navigation_buttons):
                if level in (0, 1):
                    navigation = ["{}", "{}", "{}", "{} ›", "{} »"]
                    navigation[level] = "• {} •"

                    data = pages if button == 4 else button + 1

                elif level in (pages - 1, pages - 2):
                    navigation = ["« {}", "‹ {}", "{}", "{}", "{}"]
                    navigation[level - pages + 5] = "• {} •"

                    if button:
                        data = pages + button - 4
                    else:
                        data = button + 1

                else:
                    navigation = ["« {}", "‹ {}", "• {} •", "{} ›", "{} »"]

                    if button:
                        if button == 4:
                            data = pages
                        else:
                            data = button + level - 1
                    else:
                        data = 1

                button_name = navigation[button].format(data)
                button_data = f"level_{'0'*(1 - data//10)}{data - 1}"
                buttons[0].append([button_name, button_data])

        return buttons
