# Project imports
import config


def response_creator(command, chat_id, text):
    '''Create a request wrapper.

    Parameters
    ----------
    command : str
        Command name from Telegram documentation.
    chat_id : str
        Unique user id.
    text : str
        The text to be wrapped.

    Returns
    -------
    url : str
        Link to send a message.
    JSON_response : dict
        Extending the message.
    '''

    url = config.URL.format(token=config.TOKEN, command=command)
    JSON_response = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2'
    }

    return url, JSON_response


def inline_keyboard_creator(*button_data):
    '''Inline keyboard creation.

    Parameters
    ----------
    *button_data
        Button data to wrap.

    Returns
    -------
    keyboard : dict
        Ready wrapped keyboard.
    '''

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
