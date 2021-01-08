# -*- coding: utf-8 -*-
'''Module responsible for processing the user's message
and sending him a response.
'''

# Other imports
import json
import requests

# Project imports
import scripts.tools as tools
import scripts.database as db


class Handler:
    '''Determining the essence of the message.
    '''

    def handler(self, request):
        '''Checking a message for a request type.

        Parameters
        ----------
        request : JSON
            Object representing the message.
        '''

        if 'message' in request:
            message = request['message']
            self.message_handler(message)

        elif 'callback_query' in request:
            callback_query = request['callback_query']
            self.callback_query_handler(callback_query)

    def message_handler(self, message):
        '''Work with a simple message.

        Parameters
        ----------
        message : JSON
            Message content.
        '''

        chat_id = message['chat']['id']
        message_text = message['text']

        send_menu = Menu(chat_id)
        if 'entities' in message:
            message_entities = message['entities']

            if message_entities[0]['type'] == 'bot_command':
                if '/start' in message_text:
                    self._check_new_user(message)
                    send_menu.private_office()

    def callback_query_handler(self, callback_query):
        '''Work with inline message.

        Parameters
        ----------
        callback_query : JSON
            An object containing information
            about the pressed button.
        '''

        data = callback_query['data']
        chat_id = callback_query['from']['id']
        message_id = callback_query['message']['message_id']

        switch_menu = Menu(chat_id)
        if data == 'settings':
            switch_menu.settings(message_id)

    @staticmethod
    def _check_new_user(message):
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


class Menu:
    '''Create a message (send or edit) which I call "Menu".
    It contains buttons that the user can use to navigate the bot.
    '''

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def private_office(self):
        '''Sending a personal user menu.
        '''

        locale = self._get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # _get_menu_name will definitely return as many name
        # values as you passed data to it.
        menu, collections, settings = self._get_menu_name(
            locale, 'private_office', 'collections', 'settings')

        url, response = tools.response_creator(
            command='sendMessage', chat_id=self.chat_id, text=menu)

        keyboard = tools.inline_keyboard_creator(
            [
                [collections, 'collections'],
                [settings, 'settings']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)

    def settings(self, message_id):
        '''Changing the current menu to the settings menu.

        Parameters
        ----------
        message_id : int
            Unique message id.
        '''

        locale = self._get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # _get_menu_name will definitely return as many name
        # values as you passed data to it.
        menu, locale_settings, back = self._get_menu_name(
            locale, 'settings', 'locale_settings', 'back')

        url, response = tools.response_creator(
            command='editMessageText',
            chat_id=self.chat_id, text=menu,
            message_id=message_id)

        keyboard = tools.inline_keyboard_creator(
            [
                [locale_settings, 'locale_settings']
            ],
            [
                [back, 'private_office']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)

    @staticmethod
    def _get_user_locale(chat_id):
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
    def _get_menu_name(locale, *menu_list):
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
            db_name = config['database']['db'][1]
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
