# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
import psycopg2
from psycopg2 import sql


class CreateTable:
    def __init__(self, db_name):
        self.db_name = db_name
        self._connection = None
        self._cursor = None

        with open("config.json") as config_json:
            config = json.load(config_json)

            self._user = config["database"]["user"]
            self._passwd = config["database"]["passwd"]

            self._host = config["database"]["host"]
            self._port = config["database"]["port"]

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self.db_name,
            user=self._user, password=self._passwd,
            host=self._host, port=self._port
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def bot_messages(self):
        self._cursor.execute(
            """CREATE TABLE messages (
               id serial PRIMARY KEY,
               locale text,
               data text,
               message text
            );"""
        )

    def bot_users(self):
        self._cursor.execute(
            """CREATE TABLE users (
               id serial PRIMARY KEY,
               user_id integer,
               username text,
               locale text,
               collections integer,
               cards integer,
               menu_id integer,
               session text
            );"""
        )


class Insert:
    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

        with open("config.json") as config_json:
            config = json.load(config_json)

            self._user = config["database"]["user"]
            self._passwd = config["database"]["passwd"]

            self._host = config["database"]["host"]
            self._port = config["database"]["port"]

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=self._user, password=self._passwd,
            host=self._host, port=self._port
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def new_bot_message(self, data, message, locale="ru"):
        self._cursor.execute(
            """INSERT INTO messages (locale, data, message)
               VALUES (%s, %s, %s);
            """, (locale, data, message)
        )

    def new_user(self, user_id, username, locale, menu_id):
        self._cursor.execute(
            """INSERT INTO users (
               user_id,
               username,
               locale,
               collections,
               cards,
               menu_id,
               session
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (user_id, username, locale, 0, 0, menu_id, None)
        )


class Select:
    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

        with open("config.json") as config_json:
            config = json.load(config_json)

            self._user = config["database"]["user"]
            self._passwd = config["database"]["passwd"]

            self._host = config["database"]["host"]
            self._port = config["database"]["port"]

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=self._user, password=self._passwd,
            host=self._host, port=self._port
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def bot_message(self, data, locale="ru"):
        self._cursor.execute(
            """SELECT message FROM messages
               WHERE locale=%s AND
                     data=%s;
            """, (locale, data)
        )

        message = self._cursor.fetchone()[0]
        return message

    def user_attributes(self, user_id):
        self._cursor.execute(
            """SELECT * FROM users
               WHERE user_id=%s;
            """, (user_id,)
        )

        attributes = self._cursor.fetchone()
        return attributes


class Update:
    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

        with open("config.json") as config_json:
            config = json.load(config_json)

            self._user = config["database"]["user"]
            self._passwd = config["database"]["passwd"]

            self._host = config["database"]["host"]
            self._port = config["database"]["port"]

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=self._user, password=self._passwd,
            host=self._host, port=self._port
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def user_attribute(self, user_id, attribute, value):
        self._cursor.execute(
            sql.SQL(
                "UPDATE users SET {}=%s WHERE user_id=%s"
            ).format(sql.Identifier(attribute)), (value, user_id)
        )
