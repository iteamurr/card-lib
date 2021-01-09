# -*- coding: utf-8 -*-
'''Module responsible for processing the user's message
and sending him a response.
'''

# Other imports
import requests

# Project imports
# pylint: disable=import-error
from tools import API, BotTools


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
            self._message_handler(message)

        elif 'callback_query' in request:
            callback_query = request['callback_query']
            self._callback_query_handler(callback_query)

    @staticmethod
    def _message_handler(message):
        '''Work with a simple message.

        Parameters
        ----------
        message : JSON
            Message content.
        '''

        chat_id = message['chat']['id']
        message_text = message['text']

        send_menu = SendMenu(chat_id)
        if 'entities' in message:
            message_entities = message['entities']

            if message_entities[0]['type'] == 'bot_command':
                if '/start' in message_text:
                    BotTools.check_new_user(message)
                    send_menu.private_office()
                elif '/settings' in message_text:
                    send_menu.settings()

    @staticmethod
    def _callback_query_handler(callback_query):
        '''Work with inline message.

        Parameters
        ----------
        callback_query : JSON
            An object containing information
            about the pressed button.
        '''

        data = callback_query['data']
        callback_id = callback_query['id']

        chat_id = callback_query['from']['id']
        message_id = callback_query['message']['message_id']

        switch_menu = SwitchMenu(chat_id, message_id, callback_id)
        if data == 'settings':
            switch_menu.settings()
        elif data == 'private_office':
            switch_menu.private_office()
        elif data == 'locale_settings':
            switch_menu.locale_settings()


class SendMenu:
    '''Send the user a menu used for navigation.
    '''

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def private_office(self):
        '''Sending personal user menu.
        '''

        locale = BotTools.get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # BotTools.get_menu_name will definitely return
        # as many name values as you passed data to it.
        menu, collections, settings = BotTools.get_menu_name(
            locale, 'private_office', 'collections', 'settings')

        url, response = API.send_message(self.chat_id, menu)
        keyboard = API.inline_keyboard(
            [
                [collections, 'collections'],
                [settings, 'settings']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)

    def settings(self):
        '''Sending settings menu.
        '''

        locale = BotTools.get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # BotTools.get_menu_name will definitely return
        # as many name values as you passed data to it.
        menu, locale_settings, back = BotTools.get_menu_name(
            locale, 'settings', 'locale_settings', 'back')

        url, response = API.send_message(self.chat_id, menu)
        keyboard = API.inline_keyboard(
            [
                [locale_settings, 'locale_settings']
            ],
            [
                [back, 'private_office']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)


class SwitchMenu:
    '''Changing the current menu to a new one.
    '''

    def __init__(self, chat_id, message_id, callback_id):
        self.chat_id = chat_id
        self.message_id = message_id
        self.callback_id = callback_id

    def private_office(self):
        '''Changing the current menu to user menu.
        '''

        locale = BotTools.get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # BotTools.get_menu_name will definitely return
        # as many name values as you passed data to it.
        menu, collections, settings = BotTools.get_menu_name(
            locale, 'private_office', 'collections', 'settings')

        url, response = API.edit_message(self.chat_id, self.message_id, menu)
        callback_url, answer = API.answer_callback_query(self.callback_id)
        keyboard = API.inline_keyboard(
            [
                [collections, 'collections'],
                [settings, 'settings']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)
        requests.post(callback_url, json=answer)

    def settings(self):
        '''Changing the current menu to settings menu.
        '''

        locale = BotTools.get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # BotTools.get_menu_name will definitely return
        # as many name values as you passed data to it.
        menu, locale_settings, back = BotTools.get_menu_name(
            locale, 'settings', 'locale_settings', 'back')

        url, response = API.edit_message(self.chat_id, self.message_id, menu)
        callback_url, answer = API.answer_callback_query(self.callback_id)
        keyboard = API.inline_keyboard(
            [
                [locale_settings, 'locale_settings']
            ],
            [
                [back, 'private_office']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)
        requests.post(callback_url, json=answer)

    def locale_settings(self):
        '''Changing the current menu to language settings menu.
        '''

        locale = BotTools.get_user_locale(self.chat_id)

        # pylint: disable=unbalanced-tuple-unpacking
        # BotTools.get_menu_name will definitely return
        # as many name values as you passed data to it.
        menu, en_locale, ru_locale, main, back = BotTools.get_menu_name(
            locale,
            'current_language',
            'change_language_to_en',
            'change_language_to_ru',
            'main',
            'back'
        )

        menu = menu.format({'en': 'English', 'ru': 'Russian'}[locale])
        url, response = API.edit_message(self.chat_id, self.message_id, menu)
        callback_url, answer = API.answer_callback_query(self.callback_id)
        keyboard = API.inline_keyboard(
            [
                [en_locale, 'change_language_to_en'],
                [ru_locale, 'change_language_to_ru']
            ],
            [
                [main, 'private_office'],
                [back, 'settings']
            ]
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)
        requests.post(callback_url, json=answer)
