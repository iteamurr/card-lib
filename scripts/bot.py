# Other imports
import requests

# Project imports
import tools
import config
import database as db


class MessageHandler:
    def __init__(self, JSON):
        self.JSON = JSON

    def handler(self):
        '''Checking a message for a request type.
        '''

        message = self.JSON['message']
        message_text = message['text']
        chat_id = message['chat']['id']

        send_menu = SendMenu(chat_id)
        if 'entities' in message:
            message_entities = message['entities']

            if message_entities[0]['type'] == 'bot_command':
                if '/start' in message_text:
                    self.check_new_user()
                    send_menu.private_office()


    def check_new_user(self):
        '''Checking for the presence of a user in the database.
        If there is no user, write it to the database.
        '''

        message = self.JSON['message']
        chat_id = message['chat']['id']

        db_select = db.Select(
            name='bot_users',
            user=config.DB_USER, password=config.DB_PASSWORD,
            host=config.HOST, port=config.PORT)

        user_existence = db_select.get_user_attributes(chat_id)

        if not user_existence:
            user_menu_id = message['message_id']
            username = message['from']['username']
            locale = message['from']['language_code']
            user_locale = locale if locale in ['en', 'ru'] else 'en'

            db_insert = db.Insert(
                name='bot_users',
                user=config.DB_USER, password=config.DB_PASSWORD,
                host=config.HOST, port=config.PORT)

            db_insert.new_user(
                user_id=chat_id, username=username,
                locale=user_locale, menu_id=user_menu_id)


class SendMenu:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def private_office(self):
        '''Sending a personal user menu.
        '''

        db_select_user_locale = db.Select(
            name='bot_users',
            user=config.DB_USER, password=config.DB_PASSWORD,
            host=config.HOST, port=config.PORT)

        locale = db_select_user_locale.get_user_attributes(self.chat_id)[3]

        db_select_message = db.Select(
            name='bot_messages',
            user=config.DB_USER, password=config.DB_PASSWORD,
            host=config.HOST, port=config.PORT)

        menu_text = db_select_message.get_bot_message(
            data='private_office', locale=locale)

        settings_menu_name = db_select_message.get_bot_message(
            data='settings', locale=locale)

        collections_menu_name = db_select_message.get_bot_message(
            data='collections', locale=locale)

        url, response = tools.response_creator(
            command='sendMessage', chat_id=self.chat_id, text=menu_text)

        keyboard = tools.inline_keyboard_creator(
            (collections_menu_name, 'collections'),
            (settings_menu_name, 'settings')
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)
