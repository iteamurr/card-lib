# Other imports
import requests

# Project imports
import tools
import config
import database as db


def message_handler(JSON):
    '''Checking a message for a request type.

    Parameters
    ----------
    JSON : dict
        A key unique to each message.
    '''

    message = JSON['message']
    message_text = message['text']
    chat_id = message['chat']['id']

    send_menu = SendMenu(chat_id)
    if 'entities' in message:
        message_entities = message['entities']

        if message_entities[0]['type'] == 'bot_command':
            if '/start' in message_text:
                send_menu.private_office()


class SendMenu:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def private_office(self):
        '''Sending a personal user menu.
        '''

        db_select = db.Select(
            user=config.DB_USER, password=config.DB_PASSWORD,
            name='bot_messages')
        menu_text = db_select.get_bot_message('private_office', 'en')
        settings_menu_name = db_select.get_bot_message('settings', 'en')
        collections_menu_name = db_select.get_bot_message('collections', 'en')

        url, response = tools.response_creator(
            command='sendMessage', chat_id=self.chat_id, text=menu_text)
        keyboard = tools.inline_keyboard_creator(
            (collections_menu_name, 'collections'),
            (settings_menu_name, 'settings')
        )

        data = {**response, **keyboard}
        requests.post(url, json=data)
