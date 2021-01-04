# PostgreSQL
import psycopg2


class Create:
    def __init__(self, user, password,
                 host='localhost', port='5432'):
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
        cursor.execute(f'''CREATE TABLE messages
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
        cursor.execute(f'''CREATE TABLE users
            (id serial PRIMARY KEY, user_id integer,
            username text, menu_id integer,
            action integer, session text, 
            collections integer, cards integer);''')

        connection.commit()
        cursor.close()
        connection.close()


class Insert:
    def __init__(self, user, password, name,
                 host='localhost', port='5432'):
        self.db_user = user
        self.db_password = password

        self.db_name = name

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
        cursor.execute(f'''INSERT INTO messages (locale, data, message)
            VALUES (%s, %s, $s);''', (locale, data, message))

        connection.commit()
        cursor.close()
        connection.close()


class Select:
    def __init__(self, user, password, name,
                 host='localhost', port='5432'):
        self.db_user = user
        self.db_password = password

        self.db_name = name

        self.db_host = host
        self.db_port = port

    def get_bot_message(self, data, locale='ru'):
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
        cursor.execute(f'''SELECT message FROM messages
            WHERE locale=%s AND data=%s;''', (locale, data))
        message = cursor.fetchone()

        cursor.close()
        connection.close()

        return message[0]
