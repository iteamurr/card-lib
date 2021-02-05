"""
    Module with additional tools for working with a bot.
"""

import re
import random
import string
from math import ceil
import requests

from .config import telegram
from .database import Select
from .database import Insert


class API:
    """Working with the Telegram API.
    """

    @staticmethod
    def send_message(chat_id, text, keyboard=None, parse_mode=None):
        """Send a text message with additional options.

        Parameters
        ----------
        chat_id : int
            Unique identifier for the target chat.
        text : str
            Text of the message to be sent.
        keyboard : dict, optional
            Additional message interface in the form of buttons.
        parse_mode : str, optional
            Mode for parsing entities in the message text.
        """

        url = telegram["url"].format(telegram["token"], "sendMessage")

        body = {"chat_id": chat_id, "text": text}
        if parse_mode:
            body["parse_mode"] = parse_mode
        if keyboard:
            body = {**body, **keyboard}

        requests.post(url, json=body)

    @staticmethod
    def edit_message(chat_id, message_id, text,
                     keyboard=None, parse_mode=None):
        """Edit bot message, to change the message text or the current menu.

        Parameters
        ----------
        chat_id : int
            Unique identifier for the target chat.
        message_id : int
            Unique message identifier.
        text : str
            Text of the message to be sent.
        keyboard : dict, optional
            Additional message interface in the form of buttons.
        parse_mode : str, optional
            Mode for parsing entities in the message text.
        """

        url = telegram["url"].format(telegram["token"], "editMessageText")

        body = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if parse_mode:
            body["parse_mode"] = parse_mode
        if keyboard:
            body = {**body, **keyboard}

        requests.post(url, json=body)

    @staticmethod
    def answer_callback_query(callback_query_id, text=None, show_alert=False):
        """Send a response to a callback request
        sent from the inline keyboard.

        Parameters
        ----------
        callback_query_id : int
            Unique identifier for the query to be answered.
        text : str, optional
            Text of the message to be sent.
        show_alert : bool, optional
            If true, then show a notification with text.
        """

        url = telegram["url"].format(telegram["token"], "answerCallbackQuery")

        body = {"callback_query_id": callback_query_id}
        if text:
            body["text"] = text
            body["show_alert"] = show_alert

        if callback_query_id:
            requests.post(url, json=body)

    @staticmethod
    def inline_keyboard(*button_data_list):
        """Create an inline keyboard wrapper.

        Parameters
        ----------
        *button_data_list
            Button of an inline keyboard.

        Returns
        -------
        keyboard : dict
            Inline keyboard wrapper.
        """

        keyboard = {
            "reply_markup":{
                "inline_keyboard":[
                ]
            }
        }

        inline_keyboard = keyboard["reply_markup"]["inline_keyboard"]
        for index, button_data in enumerate(button_data_list):
            inline_keyboard.append([])

            for button_text, callback_data in button_data:
                button = {"text": button_text, "callback_data": callback_data}
                inline_keyboard[index].append(button)

        return keyboard


class Tools:
    """Additional tools for working with a bot.
    """

    @staticmethod
    def check_new_user(message):
        """Add a user to the database if he is not already there.

        Parameters
        ----------
        message : dict
            An object containing all information about the user.
        """

        chat_id = message["chat"]["id"]

        with Select("bot_users") as select:
            user_existence = select.user_attribute(chat_id, "locale")

        if not user_existence:
            menu_id = message["message_id"]
            username = message["from"]["username"]
            locale = message["from"]["language_code"]
            user_locale = locale if locale in ["en", "ru"] else "en"

            with Insert("bot_users") as insert:
                insert.new_user(chat_id, username, user_locale, menu_id)

    @staticmethod
    def new_collection_key():
        """Generate a random collection key.

        Returns
        -------
        key : str
            Unique identifier for the collection.
        """

        first_part = random.randrange(100000000, 1000000000)
        second_part = random.randrange(1000000000, 10000000000)
        third_part = random.choice(string.ascii_letters)

        key = f"K-{first_part}-{second_part}-{third_part}-00000-CL"
        return key

    @staticmethod
    def new_card_key():
        """
        """

        first_part = random.randrange(1000000000, 10000000000)
        second_part = random.randrange(10000000000, 100000000000)
        third_part = random.choice(string.ascii_letters)

        key = f"K-{first_part}-{second_part}-{third_part}-00000-CR"
        return key

    @staticmethod
    def get_key_from_string(text):
        """
        """

        key = re.findall(r"(K-\d+-\d+-\w-\d+-\w\w)", text)
        return key

    @staticmethod
    def button_identifier(buttons, locale="en"):
        """Get the name of buttons from the database.

        Parameters
        ----------
        buttons : dict
            A dict of buttons that need to define a name.
        locale : str, optional
            A variable defining the user's language
            and any special preferences
            that the user wants to see in their user interface.

        Returns
        -------
        buttons : dict
            List of buttons with identified names.
        """

        with Select("bot_messages") as select:
            for button in buttons:
                for data in button:
                    data[0] = select.bot_message(data[0], locale)

        return buttons

    @staticmethod
    def button_list_creator(list_of_items, buttons_in_layer=2):
        """Create a list of buttons for specific items.

        Parameters
        ----------
        list_of_items : list
            List of items from which to create a list of buttons.
        buttons_in_layer : int, optional
            Variable responsible for the number of buttons in one layer.

        Returns
        -------
        buttons : list
            List of buttons.
        """

        buttons = []
        item_list_size = len(list_of_items)
        layers = ceil(item_list_size/buttons_in_layer)

        for layer in range(layers):
            buttons.append([])
            left_border = buttons_in_layer*layer
            right_border = buttons_in_layer*(layer+1)

            for item in list_of_items[left_border:right_border]:
                data = item[2]
                name = item[3]
                button_data = [name, data]

                buttons[layer].append(button_data)

        return buttons

    @staticmethod
    def navigation_creator(number_of_items, level=0,
                           items_in_page=8, number_of_navigation_buttons=5):
        """Creating menu navigation.

        Parameters
        ----------
        number_of_items : int
            Total number of items being navigated.
        level : int, optional
            The level (page) the user is on.
        items_in_page : int, optional
            Number of items per page.
        number_of_navigation_buttons : int, optional
            Number of navigation buttons.

        Returns
        -------
        buttons : list
            List of navigation buttons.
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
