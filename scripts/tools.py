# -*- coding: utf-8 -*-
'''Module containing tools
that are used in work of bot.
'''

# Other imports
import json

# Project imports
# pylint: disable=import-error
import database as db


class API:
    '''Working with Telegram API.
    '''

    @staticmethod
    def send_message(chat_id, text, parse_mode='MarkdownV2'):
        '''Creating a link and link content to send message.

        Parameters
        ----------
        chat_id : int
            Unique user id.
        text : str
            The text to be wrapped.
        parse_mode : str, optional
            Way to format text (default is 'MarkdownV2').

        Returns
        -------
        api_url : str
            Link to send a message.
        json_response : dict
            Extending the message.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            token = config['telegram']['token']
            telegram_url = config['telegram']['url']

        api_url = telegram_url.format(token=token, command='sendMessage')
        json_response = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

        return api_url, json_response

    @staticmethod
    def edit_message(chat_id, message_id, text, parse_mode='MarkdownV2'):
        '''Create link and link content to edit message.

        Parameters
        ----------
        chat_id : int
            Unique user id.
        message_id : int
            Unique message id.
        text : str
            The text to be wrapped.
        parse_mode : str, optional
            Way to format text (default is 'MarkdownV2').

        Returns
        -------
        api_url : str
            Link to send a message.
        json_response : dict
            Extending the message.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            token = config['telegram']['token']
            telegram_url = config['telegram']['url']

        api_url = telegram_url.format(token=token, command='editMessageText')
        json_response = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode
        }

        return api_url, json_response

    @staticmethod
    def answer_callback_query(callback_query_id, text=None, show_alert=False):
        '''Response to callback request sent from inline keyboard.

        Parameters
        ----------
        callback_query_id : int
            Unique identifier for the query to be answered.
        text : str, optional
            Text of the notification.
        show_alert : bool, optional
            Show notification to user (default is False).

        Returns
        -------
        api_url : str
            Link to send a message.
        json_response : dict
            Extending the message.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            token = config['telegram']['token']
            telegram_url = config['telegram']['url']

        api_url = telegram_url.format(
            token=token, command='answerCallbackQuery')

        if not text:
            json_response = {
                'callback_query_id': callback_query_id
            }
        else:
            json_response = {
                'callback_query_id': callback_query_id,
                'text': text,
                'show_alert': show_alert
            }

        return api_url, json_response

    @staticmethod
    def inline_keyboard(*button_data_list):
        '''Inline keyboard creation.

        Parameters
        ----------
        *button_data_list
            List of button data to wrap.

        Returns
        -------
        keyboard : JSON
            Ready wrapped keyboard.
        '''

        keyboard = {
            "reply_markup":{
                "inline_keyboard":[
                ]
            }
        }

        button_index = 0
        inline_keyboard = keyboard['reply_markup']['inline_keyboard']
        for button_data in button_data_list:
            inline_keyboard.append([])

            for button_text, callback_data in button_data:
                button = {'text': button_text, 'callback_data': callback_data}
                inline_keyboard[button_index].append(button)

            button_index += 1

        return keyboard


class BotTools:
    '''Tools used by bot during message processing.
    '''

    # pylint: disable=too-many-locals
    @staticmethod
    def check_new_user(message):
        '''Checking for the presence of a user in the database.
        If there is no user, write it to the database.

        Parameters
        ----------
        message : JSON
            Message content.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            db_name = config['database']['db'][1]
            db_user = config['database']['user']
            db_password = config['database']['passwd']
            db_host = config['database']['host']
            db_port = config['database']['port']

        db_select = db.Select(
            name=db_name,
            user=db_user, password=db_password,
            host=db_host, port=db_port)

        chat_id = message['chat']['id']
        user_existence = db_select.user_attributes(chat_id)

        if not user_existence:
            user_menu_id = message['message_id']
            username = message['from']['username']
            locale = message['from']['language_code']
            user_locale = locale if locale in ['en', 'ru'] else 'en'

            db_insert = db.Insert(
                name=db_name,
                user=db_user, password=db_password,
                host=db_host, port=db_port)

            db_insert.new_user(
                user_id=chat_id, username=username,
                locale=user_locale, menu_id=user_menu_id)

    @staticmethod
    def get_user_locale(chat_id):
        '''Getting user language settings.

        Returns
        -------
        chat_id : int
            Unique user id.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            db_name = config['database']['db'][1]
            db_user = config['database']['user']
            db_password = config['database']['passwd']
            db_host = config['database']['host']
            db_port = config['database']['port']

        db_select_user_locale = db.Select(
            name=db_name,
            user=db_user, password=db_password,
            host=db_host, port=db_port)

        locale = db_select_user_locale.user_attributes(chat_id)[3]

        return locale

    @staticmethod
    def get_menu_name(locale, *menu_list):
        '''Retrieving menu names from the database.

        Parameters
        ----------
        locale : str
            A key unique to each message.
        *menu_list
            List of menus to get names.

        Returns
        -------
        menu_names : list
            List of menu names.
        '''

        with open('config.json') as config_json:
            config = json.load(config_json)
            db_name = config['database']['db'][0]
            db_user = config['database']['user']
            db_password = config['database']['passwd']
            db_host = config['database']['host']
            db_port = config['database']['port']

        db_select_message = db.Select(
            name=db_name,
            user=db_user, password=db_password,
            host=db_host, port=db_port)

        menu_names = []
        for data in menu_list:
            menu_name = db_select_message.bot_message(data, locale)
            menu_names.append(menu_name)

        return menu_names
