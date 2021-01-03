# Other imports
import requests

# Project imports
import config
import tools


def message_handler(JSON):
    message = JSON['message']
    message_text = message['text']
    message_chat_id = message['chat']['id']

    if 'entities' in message:
        message_entities = message['entities']

        if message_entities[0]['type'] == 'bot_command':
            if '/start' in message_text:
                send_profile(message_chat_id, 'Личный кабинет')


def send_profile(chat_id, text):
    url, response = tools.response_creator('sendMessage', chat_id, text)
    keyboard = tools.inline_keyboard_creator(
        ('Коллекции', 'collections'),
        ('Настройки', 'settings')
    )
    data = {**response, **keyboard}

    requests.post(url, json=data)
