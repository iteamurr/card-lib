# -*- coding: utf-8 -*-
'''Module with auxiliary tools for creating some structures.
'''

# Other imports
import json

with open('config.json') as config_json:
    config = json.load(config_json)
    token = config['telegram']['token']
    telegram_url = config['telegram']['url']


def response_creator(command, chat_id, text,
        message_id=None, parse_mode='MarkdownV2'):
    '''Create a request wrapper.

    Parameters
    ----------
    command : str
        Command name from Telegram documentation.
    chat_id : int
        Unique user id.
    text : str
        The text to be wrapped.
    message_id : int, optional
        Unique message id.
    parse_mode : str, optional
        Way to format text (default is 'MarkdownV2').

    Returns
    -------
    url : str
        Link to send a message.
    json_response : JSON
        Extending the message.
    '''

    url = telegram_url.format(token=token, command=command)

    if message_id:
        json_response = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode
        }
    else:
        json_response = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

    return url, json_response


def inline_keyboard_creator(*button_data_list):
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
