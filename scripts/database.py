# -*- coding: utf-8 -*-
'''Module responsible for working with the database.
'''

# PostgreSQL
import psycopg2


class Create:
    '''Database creation.
    '''

    def __init__(self, user, password,
                 host='localhost', port=5432):
        '''Data required to initialize the database.

        Parameters
        ----------
        user : str
            Database user.
        password : str
            Database user password.
        host : str
            Host on which the database is hosted (default is 'localhost').
        port : int
            Database port (default is 5432).
        '''

        self.user = user
        self.password = password

        self.host = host
        self.port = port

    def bot_messages_db(self, name='bot_messages'):
        '''Creating a database with messages that the bot sends to users.

        Parameters
        ----------
        name : str
            Database name (default is 'bot_messages').
        '''

        connection = psycopg2.connect(
            dbname=name,
            user=self.user, password=self.password,
            host=self.host, port=self.port
        )

        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE messages
            (id serial PRIMARY KEY, locale text,
            data text, message text);''')

        connection.commit()
        cursor.close()
        connection.close()

    def users_db(self, name='bot_users'):
        '''Creating a database of bot users.

        Parameters
        ----------
        name : str
            Database name (default is 'bot_users').
        '''

        connection = psycopg2.connect(
            dbname=name,
            user=self.user, password=self.password,
            host=self.host, port=self.port
        )

        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE users
            (id serial PRIMARY KEY, user_id integer,
            username text, locale text,
            collections integer, cards integer,
            menu_id integer, session text);''')

        connection.commit()
        cursor.close()
        connection.close()


class Insert:
    '''Inserting to the database.
    '''

    # pylint: disable=too-many-arguments
    # All arguments are required
    # for the database to work correctly.
    def __init__(self, name, user, password,
                 host='localhost', port=5432):
        '''Data required to initialize the database.

        Parameters
        ----------
        name : str
            Database name.
        user : str
            Database user.
        password : str
            Database user password.
        host : str
            Host on which the database is hosted (default is 'localhost').
        port : int
            Database port (default is 5432).
        '''

        self.db_name = name

        self.db_user = user
        self.db_password = password

        self.db_host = host
        self.db_port = port

    def new_bot_message(self, data, message, locale='ru'):
        '''Inserting a new bot message to the database.

        Parameters
        ----------
        data : str
            A key unique to each message.
        message : str
            The message that the bot will send
            in response to the user.
        locale : str
            Language of the message (default is 'ru').
        '''

        connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user, password=self.db_password,
            host=self.db_host, port=self.db_port
        )

        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO messages (locale, data, message)
            VALUES (%s, %s, %s);''', (locale, data, message))

        connection.commit()
        cursor.close()
        connection.close()

    def new_user(self, user_id, username, locale, menu_id):
        '''Inserting a new user to the database.

        Parameters
        ----------
        user_id : int
            A unique ID for each user.
        username : str
            Short username in Telegram.
        locale : str
            Language of the message.
        menu_id : int
            Unique message ID of the user's
            private office menu.
        '''

        connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user, password=self.db_password,
            host=self.db_host, port=self.db_port
        )

        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, locale,
                               collections, cards,
                               menu_id, session)
            VALUES (%s, %s, %s,
                    %s, %s,
                    %s, %s);''',
            (user_id, username, locale,
            0, 0,
            menu_id, None))

        connection.commit()
        cursor.close()
        connection.close()


class Select:
    '''Selecting data from the database.
    '''

    # pylint: disable=too-many-arguments
    # All arguments are required
    # for the database to work correctly.
    def __init__(self, name, user, password,
                 host='localhost', port=5432):
        '''Data required to initialize the database.

        Parameters
        ----------
        name : str
            Database name.
        user : str
            Database user.
        password : str
            Database user password.
        host : str
            Host on which the database is hosted (default is 'localhost').
        port : int
            Database port (default is 5432).
        '''

        self.db_name = name

        self.db_user = user
        self.db_password = password

        self.db_host = host
        self.db_port = port

    def bot_message(self, data, locale='ru'):
        '''Getting a bot message from the database.

        Parameters
        ----------
        data : str
            A key unique to each message.
        locale : str
            Language of the message (default is 'ru').

        Returns
        -------
        message : str
            The message that the bot will send
            in response to the user.
        '''

        connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user, password=self.db_password,
            host=self.db_host, port=self.db_port
        )

        cursor = connection.cursor()
        cursor.execute('''
            SELECT message FROM messages
            WHERE locale=%s AND data=%s;''', (locale, data))
        message = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return message

    def user_attributes(self, user_id):
        '''Getting all user attributes.

        Parameters
        ----------
        user_id : int
            A unique ID for each user.

        Returns
        -------
        attributes : tuple
            All user attributes.
        '''

        connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user, password=self.db_password,
            host=self.db_host, port=self.db_port
        )

        cursor = connection.cursor()
        cursor.execute('''
            SELECT * FROM users
            WHERE user_id=%s;''', (user_id, ))
        attributes = cursor.fetchone()

        cursor.close()
        connection.close()

        return attributes
