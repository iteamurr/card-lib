# Other imports
import requests

# Project imports
import config
import tools


def message_handler(JSON):
    message_chat_id = JSON['message']['chat']['id']
    message_text = JSON['message']['text']

    if 'entities' in JSON['message']:
        if JSON['message']['entities'][0]['type'] == 'bot_command':
            if '/start' in message_text:
                send_profile(message_chat_id, 'Личный кабинет')


def send_profile(chat_id, text):
    url, response = tools.response_creator('sendMessage', chat_id, text)
    keyboard = tools.inline_keyboard_creator(('Коллекции', 'collections'),
                                             ('Настройки', 'settings'))
    data = {**response, **keyboard}

    requests.post(url, json=data)
