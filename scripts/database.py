"""
    Database module.
"""

import psycopg2
from psycopg2 import sql

from .config import database


class CreateTable:
    """Class responsible for creating tables in the database.
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self.db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
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
        """Create a bot message table.
        """

        self._cursor.execute(
            """CREATE TABLE messages (
               id serial PRIMARY KEY,
               locale text,
               data text,
               message text
            );
            """
        )

    def bot_users(self):
        """Create a bot users table.
        """

        self._cursor.execute(
            """CREATE TABLE users (
               id serial PRIMARY KEY,
               user_id integer,
               username text,
               locale text,
               collections integer,
               cards integer,
               menu_id integer,
               page_level integer,
               session text
            );
            """
        )

    def bot_collections(self):
        """Create a bot user collections table.
        """

        self._cursor.execute(
            """CREATE TABLE collections (
               id serial PRIMARY KEY,
               user_id integer,
               key text,
               name text,
               description text,
               cards integer,
               page_level integer
            );
            """
        )

    def bot_cards(self):
        """
        """

        self._cursor.execute(
            """CREATE TABLE cards (
               id serial PRIMARY KEY,
               user_id integer,
               key text,
               card_key text,
               name text,
               description text
            );
            """
        )


class Insert:
    """Class responsible for writing new data to the database.
    """

    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
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

    def new_bot_message(self, data, message, locale="en"):
        """Insert a new bot message.

        Parameters
        ----------
        data : str
            Unique message identifier.
        message : str
            Message text.
        locale : str, optional
            A variable defining the user's language
            and any special preferences
            that the user wants to see in their user interface.
        """

        self._cursor.execute(
            """INSERT INTO messages (locale, data, message)
               VALUES (%s, %s, %s);
            """, (locale, data, message)
        )

    def new_user(self, user_id, username, locale, menu_id):
        """Register new user.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        username : str
            User's username.
        locale : str
            A variable defining the user's language
            and any special preferences
            that the user wants to see in their user interface.
        menu_id : int
            Unique menu identifier.
        """

        self._cursor.execute(
            """INSERT INTO users (
               user_id,
               username,
               locale,
               collections,
               cards,
               menu_id,
               page_level,
               session
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (user_id, username, locale, 0, 0, menu_id, 0, None)
        )

    def new_collection(self, user_id, key, name):
        """Insert a new collection.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        key : str
            Unique identifier for the collection.
        name : str
            Collection name.
        """

        self._cursor.execute(
            """INSERT INTO collections (
               user_id,
               key,
               name,
               description,
               cards,
               page_level
            ) VALUES (%s, %s, %s, %s, %s, %s);
            """, (user_id, key, name, None, 0, 0)
        )

    def new_card(self, user_id, key, card_key, name):
        """
        """

        self._cursor.execute(
            """INSERT INTO cards (
               user_id,
               key,
               card_key,
               name,
               description
            ) VALUES (%s, %s, %s, %s, %s);
            """, (user_id, key, card_key, name, None)
        )


class Select:
    """Class responsible for retrieving information from the database.
    """

    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
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

    def bot_message(self, data, locale="en"):
        """Get bot message.

        Parameters
        ----------
        data : str
            Unique message identifier.
        locale : str, optional
            A variable defining the user's language
            and any special preferences
            that the user wants to see in their user interface.

        Returns
        -------
        message : str
            Bot message if successful, None otherwise.
        """

        self._cursor.execute(
            """SELECT message FROM messages
               WHERE locale=%s AND
                     data=%s;
            """, (locale, data)
        )

        message = self._cursor.fetchone()
        if message:
            return message[0]
        return None

    def user_attribute(self, user_id, attribute):
        """Get user attribute.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        attribute : str
            The name of the attribute whose value you want to get.

        Returns
        -------
        attribute_value : str or int
            Attribute value if successful, None otherwise.
        """

        self._cursor.execute(
            sql.SQL(
                "SELECT {} FROM users WHERE user_id=%s;"
            ).format(sql.Identifier(attribute)), (user_id,)
        )

        attribute_value = self._cursor.fetchone()
        if attribute_value:
            return attribute_value[0]
        return None

    def collection_attribute(self, user_id, key, attribute):
        """Get collection attribute.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        key : str
            Unique identifier for the collection.
        attribute : str
            The name of the attribute whose value you want to get.

        Returns
        -------
        attribute_value : str or int
            Attribute value if successful, None otherwise.
        """

        self._cursor.execute(
            sql.SQL(
                "SELECT {} FROM collections WHERE user_id=%s AND key=%s;"
            ).format(sql.Identifier(attribute)), (user_id, key)
        )

        attribute_value = self._cursor.fetchone()
        if attribute_value:
            return attribute_value[0]
        return None

    def user_collections(self, user_id):
        """Get all user collections.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.

        Returns
        -------
        collections : list
            All user collections.
        """

        self._cursor.execute(
            """SELECT * FROM collections WHERE user_id=%s;
            """, (user_id,)
        )

        collections = self._cursor.fetchall()
        return collections

    def collection_cards(self, user_id, key):
        """
        """

        self._cursor.execute(
            """SELECT * FROM cards WHERE user_id=%s and key=%s;
            """, (user_id, key)
        )

        cards = self._cursor.fetchall()
        return cards


class Update:
    """Class responsible for updating data in the database.
    """

    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
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
        """Update user attribute value.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        attribute : str
            The name of the attribute whose value you want to update.
        value : str or int
            New attribute value.
        """

        self._cursor.execute(
            sql.SQL(
                "UPDATE users SET {}=%s WHERE user_id=%s;"
            ).format(sql.Identifier(attribute)), (value, user_id)
        )

    def collection_attribute(self, user_id, key, attribute, value):
        """Update collection attribute value.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        key : str
            Unique identifier for the collection.
        attribute : str
            The name of the attribute whose value you want to update.
        value : str or int
            New attribute value.
        """

        self._cursor.execute(
            sql.SQL(
                "UPDATE collections SET {}=%s WHERE user_id=%s AND key=%s;"
            ).format(sql.Identifier(attribute)), (value, user_id, key)
        )


class Delete:
    """Class responsible for deleting data from the database.
    """

    def __init__(self, db_name):
        self._db_name = db_name
        self._connection = None
        self._cursor = None

    def __enter__(self):
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
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

    def collection(self, user_id, key):
        """Delete user collection.

        Parameters
        ----------
        user_id : int
            Unique identifier of the target user.
        key : str
            Unique identifier for the collection.
        """

        self._cursor.execute(
            """DELETE FROM collections
               WHERE user_id=%s AND
                     key=%s;
            """, (user_id, key)
        )
