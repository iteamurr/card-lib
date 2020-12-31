# Project imports
import config


def response_creator(command, chat_id, text):
    url = config.URL.format(token=config.TOKEN, command=command)
    JSON_response = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2'
    }

    return url, JSON_response


def inline_keyboard_creator(*button_data):
    keyboard = {
        'reply_markup': 
            {
                'inline_keyboard': [[]]
            }
    }

    for button_text, callback_data in button_data:
        button = {'text': button_text, 'callback_data': callback_data}
        keyboard['reply_markup']['inline_keyboard'][0].append(button)

    return keyboard
