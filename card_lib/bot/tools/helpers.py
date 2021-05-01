"""
    Implementation of tools to help the bot work.
"""
import re
import random
import string
from math import ceil
from typing import Any, Union, Optional, Callable
from datetime import datetime
import requests

from ..config import (TELEGRAM_TOKEN, TELEGRAM_URL, USERS_DATABASE,
                      COLLECTIONS_DATABASE, MESSAGES_DATABASE)
from ..tools.database import Select, Insert, Update


# Variable defining the type of button template.
ButtonTemplate = list[str, str]

# Variable defining the type of layer template.
LayerTemplate = list[ButtonTemplate, ...]

# Variable defining the type of menu template.
MenuTemplate = list[LayerTemplate, ...]


class Bot:
    """Bot action decorators.
    """
    @staticmethod
    def send_message(func: Callable) -> Callable:
        """Decorator responsible for sending the message.

        Note:
            For the decorator to work, the method must have variables:
            - `self.user_id`,
            - `self.text`,
            - `self.parse_mode`,
            - `self.message_menu`,
            - `self.disable_web_page_preview`
        """
        def _send_message(self, *args, **kwargs):
            func(self, *args, **kwargs)

            if self.message_menu:
                keyboard = API.inline_keyboard(self.message_menu)
            else:
                keyboard = None

            API.send_message(
                chat_id=self.user_id,
                text=self.text,
                keyboard=keyboard,
                parse_mode=self.parse_mode,
                disable_web_page_preview=self.disable_web_page_preview
            )
        return _send_message

    @staticmethod
    def edit_message(func: Callable) -> Callable:
        """Decorator responsible for changing the message.

        Note:
            For the decorator to work, the method must have variables:
            - `self.user_id`,
            - `self.menu`,
            - `self.title`,
            - `self.message_id`,
            - `self.parse_mode`
        """
        def _edit_message(self, *args, **kwargs):
            func(self, *args, **kwargs)

            keyboard = API.inline_keyboard(self.menu) if self.menu else None

            API.edit_message(
                chat_id=self.user_id,
                message_id=self.message_id,
                text=self.title,
                keyboard=keyboard,
                parse_mode=self.parse_mode
            )
        return _edit_message

    @staticmethod
    def answer_callback_query(func: Callable) -> Callable:
        """Decorator responsible for the answer callback query.

        Note:
            For the decorator to work, the method must have variables:
            - `self.callback_id`,
            - `self.callback_query_text`,
            - `self.show_alert`
        """
        def _answer_callback_query(self, *args, **kwargs):
            func(self, *args, **kwargs)

            API.answer_callback_query(
                callback_query_id=self.callback_id,
                text=self.callback_query_text,
                show_alert=self.show_alert
            )
        return _answer_callback_query


class API:
    """Working with the Telegram API.
    """
    @staticmethod
    def send_message(
        chat_id: int,
        text: str,
        keyboard: Optional[dict[str, Any]] = None,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: Optional[bool] = False
    ) -> None:
        """Send a text message with additional options.

        Args:
            chat_id: Unique identifier for the target chat.
            text: Text of the message to be sent.
            keyboard: Additional message interface in the form of buttons.
                      Defaults to None.
            parse_mode: Mode for parsing entities in the message text.
                        Defaults to None.
            disable_web_page_preview: Disables link previews
                                      for links in this message.
        """
        url = TELEGRAM_URL.format(TELEGRAM_TOKEN, "sendMessage")
        body = {"chat_id": chat_id, "text": text}

        if parse_mode:
            body["parse_mode"] = parse_mode

        if disable_web_page_preview:
            body["disable_web_page_preview"] = disable_web_page_preview

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
        url = TELEGRAM_URL.format(TELEGRAM_TOKEN, "editMessageText")
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
        url = TELEGRAM_URL.format(TELEGRAM_TOKEN, "answerCallbackQuery")
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
        with Select(USERS_DATABASE) as select:
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

        with Insert(USERS_DATABASE) as insert:
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
        with Select(USERS_DATABASE) as select:
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
        with Select(MESSAGES_DATABASE) as select:
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
        with Update(USERS_DATABASE) as update:
            update.user_attribute(user_id, "locale", data[:2])

    @staticmethod
    def new_collection_key() -> str:
        """Generate a random collection key.

        Returns:
            key: Unique identifier for the collection.
        """
        hex_part = hex(
            int(datetime.now().timestamp())*random.randrange(10, 20)
        )[2:]
        string_part = random.choice(string.ascii_letters)

        key = f"K-{hex_part}-{string_part}-CL"
        return key

    @staticmethod
    def new_card_key() -> str:
        """Generate a random card key.

        Returns:
            card_key: Unique identifier for the card.
        """
        hex_part = hex(
            int(datetime.now().timestamp())*random.randrange(10, 20)
        )[2:]
        string_part = random.choice(string.ascii_letters)

        card_key = f"K-{hex_part}-{string_part}-CR"
        return card_key

    @staticmethod
    def collection_search(key: str) -> bool:
        """Check the existence of a collection without binding to the user.

        Args:
            key: Unique identifier for the collection.

        Returns:
            True for success, False otherwise.
        """
        with Select(COLLECTIONS_DATABASE) as select:
            is_exists = select.collection_without_user_binding(key)
        return bool(is_exists)

    @staticmethod
    def check_collection_existence(user_id: int, key: str) -> bool:
        """Check for the existence of a collection with a specific key.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.

        Returns:
            True for success, False otherwise.
        """
        with Select(COLLECTIONS_DATABASE) as select:
            is_exists = select.collection_attribute(user_id, key, "name")
        return bool(is_exists)

    @staticmethod
    def check_card_existence(user_id: int, key: str, card_key: int) -> bool:
        """Check for the existence of a card in a specific collection.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.

        Returns:
            True for success, False otherwise.
        """
        with Select(COLLECTIONS_DATABASE) as select:
            is_exists = select.card_attribute(user_id, key, card_key, "name")
        return bool(is_exists)

    @staticmethod
    def text_appearance(text: str) -> str:
        """Replace invalid characters.

        Args:
            text: Text to be corrected.

        Returns:
            modified_text: Corrected text.
        """
        modified_text = (
            text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[")
            .replace("]", "\\]").replace("(", "\\(").replace(")", "\\)")
            .replace("~", "\\~").replace("`", "\\`").replace(">", "\\>")
            .replace("#", "\\#").replace("+", "\\+").replace("-", "\\-")
            .replace("=", "\\=").replace("|", "\\|").replace("{", "\\{")
            .replace("}", "\\}").replace(".", "\\.").replace("!", "\\!")
        )

        return modified_text

    @staticmethod
    def button_list_creator(
        obj: str,
        header: str,
        data: str,
        list_of_items: list[Any],
        buttons_in_layer: Optional[int] = 2
    ) -> LayerTemplate:
        """Create a list of buttons for specific items.

        Args:
            obj: Session identifier for creating a list of buttons.
            header: The section the button belongs to.
            data: Data associated with the callback button.
            list_of_items: List of items from which to create a
                           list of buttons.
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
                button_data = f"{header}/{data}/{item[2]}"
                if obj == "collection":
                    button_name = item[3]
                else: # obj == "card"
                    button_name = item[4]
                    button_data += f"/{item[3]}"

                buttons[layer].append([button_name, button_data])

        return buttons

    @staticmethod
    def memorization_algorithm(
        repetition: int,
        difficulty: int,
        easy_factor: float
    ) -> tuple[int, float]:
        """Memorization algorithm based on constant repetition.

        Note:
            Based on SuperMemo 2 algorithm and Tsune repository. More details:
            1. https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
            2. https://github.com/DummyDivision/Tsune

        Args:
            repetition: Number of repetitions until now.
            difficulty: Difficulty rating for the item in question.
                        From 0 (hardest) to 4 (easiest).
            easy_factor: An factor for calculating the next.

        Returns
            interval: Seconds until next practice.
            easy_factor: New easiness factor.
        """
        if difficulty < 3:
            return 60, easy_factor

        if difficulty == 3:
            return 1800, easy_factor

        repetition, easy_factor = Tools.calculate_easy_factor(
            repetition=repetition,
            difficulty=difficulty,
            old_easy_factor=easy_factor
        )
        interval = 86400*Tools.calculate_interval(
            repetition=repetition,
            difficulty=difficulty,
            easy_factor=easy_factor
        )
        return interval, easy_factor

    @staticmethod
    def calculate_easy_factor(
        repetition: int,
        difficulty: int,
        old_easy_factor: float
    ) -> tuple[int, float]:
        """Calculate new easy factor from old factor and rating.

        Args:
            repetition: Number of repetitions until now.
            difficulty: Difficulty rating for the item in question.
                        From 0 (hardest) to 4 (easiest).
            old_easy_factor: An factor for calculating
                             the next repetition interval.

        Returns
            repetition: Number of repetitions.
            new_easy_factor: New easiness factor.
        """
        if difficulty < 2:
            repetition = 1

        new_easy_factor = (old_easy_factor - 0.8
                           + difficulty*(0.28 - 0.02*difficulty))

        if new_easy_factor < 1.3:
            new_easy_factor = 1.3

        return repetition, new_easy_factor

    @staticmethod
    def calculate_interval(
        repetition: int,
        difficulty: int,
        easy_factor: float
    ) -> int:
        """Calculate the inter-repetition interval.

        Args:
            repetition: Number of repetitions until now.
            difficulty: Difficulty rating for the item in question.
                        From 0 (hardest) to 4 (easiest).
            easy_factor: An factor for calculating the next.

        Returns:
            interval: Days until next practice.
        """
        if repetition < 3:
            return difficulty/2

        if repetition == 3:
            return difficulty

        interval = easy_factor*Tools.calculate_interval(
            repetition=repetition - 1,
            difficulty=difficulty,
            easy_factor=easy_factor
        )
        return interval

    @staticmethod
    def navigation_creator(
        header: str,
        number_of_items: int,
        level: Optional[int] = 0,
        key: Optional[str] = None,
        per_page: Optional[int] = 8,
        number_of_navigation_buttons: Optional[int] = 5
    ) -> LayerTemplate:
        """Creating menu navigation.

        Args:
            header: The section the button belongs to.
            number_of_items: Total number of items being navigated.
            level: The level (page) the user is on. Defaults to 0.
            key: Unique identifier for the collection. Defaults to None.
            per_page: Number of items per page. Defaults to 8.
            number_of_navigation_buttons: Number of navigation buttons.
                                          Defaults to 5.

        Returns:
            buttons: List of navigation buttons.
        """
        pages = (number_of_items//per_page + bool(number_of_items%per_page))

        if number_of_items < per_page + 1:
            return [[]]

        if number_of_items < number_of_navigation_buttons*per_page + 1:
            buttons = Tools.small_navigation_menu(
                header=header,
                pages=pages,
                level=level,
                key=key
            )

        else:
            buttons = Tools.full_navigation_menu(
                header=header,
                pages=pages,
                level=level,
                key=key,
                number_of_navigation_buttons=number_of_navigation_buttons
            )

        return buttons

    @staticmethod
    def small_navigation_menu(
        header: str,
        pages: int,
        level: int,
        key: Optional[str] = None
    ) -> LayerTemplate:
        """Create a navigation menu without unnecessary buttons.

        Args:
            header: The section the button belongs to.
            pages: Number of pages containing collections.
            level: The level (page) the user is on.
            key: Unique identifier for the collection. Defaults to None.

        Returns:
            buttons: List of navigation buttons.
        """
        buttons = [[]]
        for button in range(pages):
            page_state = ["• {} •", "{}"][button != level]

            button_name = page_state.format(button + 1)
            button_data = f"{header}/level_{'0'*(1 - button//10)}{button}"
            if key:
                button_data += f"/{key}"

            buttons[0].append([button_name, button_data])

        return buttons

    @staticmethod
    def full_navigation_menu(
        header: str,
        pages: int,
        level: int,
        key: Optional[str] = None,
        number_of_navigation_buttons: Optional[int] = 5
    ) -> LayerTemplate:
        """Create a navigation menu with the ability
        to switch between a large number of pages.

        Args:
            header: The section the button belongs to.
            pages: Number of pages containing collections.
            level: The level (page) the user is on.
            key: Unique identifier for the collection. Defaults to None.
            number_of_navigation_buttons: Number of navigation buttons.
                                          Defaults to 5.

        Returns:
            buttons: List of navigation buttons.
        """
        buttons = [[]]
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

            button_data = f"{header}/level_{'0'*(1 - data//10)}{data - 1}"
            if key:
                button_data += f"/{key}"

            button_name = navigation[button].format(data)
            buttons[0].append([button_name, button_data])

        return buttons


class Errors:
    """Error handling class.
    """
    @staticmethod
    def empty_collection(callback_id: int, locale: str) -> None:
        """Check for training on empty collection.

        Args:
            callback_id: Unique identifier for the query to be answered.
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
        """
        with Select(MESSAGES_DATABASE) as select:
            text = select.bot_message("empty_collection", locale)

        API.answer_callback_query(callback_id, text, True)

    @staticmethod
    def collection_existence_check(func: Callable) -> Callable:
        """Check the existence of the collection.

        Note:
            For the decorator to work, the method must have variables:
            - `self.user_id`,
            - `self.key`,
            - `self.callback_id`
        """
        def _collection_existence_check(self, *args, **kwargs):
            is_exists = Tools.check_collection_existence(
                user_id=self.user_id,
                key=self.key
            )

            if is_exists:
                func(self, *args, **kwargs)
            else:
                with Select(USERS_DATABASE) as select:
                    locale = select.user_attribute(self.user_id, "locale")

                with Select(MESSAGES_DATABASE) as select:
                    title = select.bot_message("does_not_exist", locale)

                API.answer_callback_query(
                    callback_query_id=self.callback_id,
                    text=title,
                    show_alert=True
                )
        return _collection_existence_check

    @staticmethod
    def card_and_collection_existence_check(func: Callable) -> Callable:
        """Check the existence of the card and collection.

        Note:
            For the decorator to work, the method must have variables:
            - `self.user_id`,
            - `self.key`,
            - `self.card_key`,
            - `self.callback_id`
        """
        def _card_and_collection_existence_check(self, *args, **kwargs):
            card_exists = Tools.check_card_existence(
                user_id=self.user_id,
                key=self.key,
                card_key=self.card_key
            )

            collection_exists = Tools.check_collection_existence(
                user_id=self.user_id,
                key=self.key
            )

            if collection_exists and card_exists:
                func(self, *args, **kwargs)
            else:
                with Select(USERS_DATABASE) as select:
                    locale = select.user_attribute(self.user_id, "locale")

                with Select(MESSAGES_DATABASE) as select:
                    title = select.bot_message("does_not_exist", locale)

                API.answer_callback_query(
                    callback_query_id=self.callback_id,
                    text=title,
                    show_alert=True
                )
        return _card_and_collection_existence_check
