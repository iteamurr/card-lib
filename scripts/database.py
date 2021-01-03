# PostgreSQL
import psycopg2


class Create:
    def __init__(self, host='localhost', port='5432'):
        self.host = host
        self.port = port


    def bot_messages_db(self, name='bot_messages', table='messages',
                        user='user', password='12345'):
        '''Creating a database with messages that the bot sends to users.

        Parameters
        ----------
        name : str
            Database name (default is 'bot_messages').
        table : str
            Database table (default is 'messages').
        user : str
            Database user (default is 'user').
        password : str
            Database password (default is '12345').
        '''

        connection = psycopg2.connect(
            dbname=name,
            user=user,
            password=password,
            host=self.host,
            port=self.port
        )

        cursor = connection.cursor()
        cursor.execute(f'''CREATE TABLE {table}
            (id serial PRIMARY KEY,
            locale varchar,
            data varchar,
            message varchar);''')
        
        connection.commit()
        cursor.close()
        connection.close()
