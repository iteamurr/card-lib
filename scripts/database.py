"""
    Database module.
"""

from __future__ import annotations
from typing import Type
from typing import Union
from typing import Optional
from types import TracebackType
import psycopg2
from psycopg2 import sql

from .config import database


# pylint: disable=unsubscriptable-object
class CreateTable:
    """Class responsible for creating tables in the database.

    Attributes:
        db_name: Name of the database to connect to.
    """

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

        self._connection = None
        self._cursor = None

    def __enter__(self) -> CreateTable:
        self._connection = psycopg2.connect(
            dbname=self.db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> CreateTable:
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def bot_messages(self) -> None:
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

    def bot_users(self) -> None:
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

    def bot_collections(self) -> None:
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

    def bot_cards(self) -> None:
        """create a bot user card table.
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

    Attributes:
        db_name: Name of the database to connect to.
    """

    def __init__(self, db_name) -> None:
        self._db_name = db_name

        self._connection = None
        self._cursor = None

    def __enter__(self) -> Insert:
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def new_bot_message(
        self,
        data: str,
        message: str,
        locale: Optional[str] = "en"
    ) -> None:
        """Insert a new bot message.

        Args:
            data: Unique message identifier.
            message: Message text.
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface. Defaults to "en".
        """

        self._cursor.execute(
            """INSERT INTO messages (locale, data, message)
               VALUES (%s, %s, %s);
            """, (locale, data, message)
        )

    def new_user(
        self,
        user_id: int,
        username: str,
        locale: str,
        menu_id: int
    ) -> None:
        """Register new user.

        Args:
            user_id: Unique identifier of the target user.
            username: User's username.
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
            menu_id: Unique menu identifier.
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

    def new_collection(self, user_id: int, key: str, name: str) -> None:
        """Insert a new collection.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            name: Collection name.
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
            """, (user_id, key, name, "🚫", 0, 0)
        )

    def new_card(
        self,
        user_id: int,
        key: str,
        card_key: str,
        name: str
    ) -> None:
        """Insert a new card.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.
            name: Card name.
        """

        self._cursor.execute(
            """INSERT INTO cards (
               user_id,
               key,
               card_key,
               name,
               description
            ) VALUES (%s, %s, %s, %s, %s);
            """, (user_id, key, card_key, name, "🚫")
        )


class Select:
    """Class responsible for retrieving information from the database.

    Attributes:
        db_name: Name of the database to connect to.
    """

    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

        self._connection = None
        self._cursor = None

    def __enter__(self) -> Select:
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def bot_message(
        self,
        data: str,
        locale: Optional[str] = "en"
    ) -> Union[str, None]:
        """Get bot message.

        Args:
            data: Unique message identifier.
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface. Defaults to "en".

        Returns:
            message: Bot message if successful, None otherwise.
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

    def user_attribute(
        self,
        user_id: int,
        attribute: str
    ) -> Union[str, int, None]:
        """Get user attribute.

        Args:
            user_id: Unique identifier of the target user.
            attribute: The name of the attribute whose value you want to get.

        Returns:
            attribute_value: Attribute value if successful, None otherwise.
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

    def collection_attribute(
        self,
        user_id: int,
        key: str,
        attribute: str
    ) -> Union[str, int, None]:
        """Get collection attribute.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            attribute: The name of the attribute whose value you want to get.

        Returns:
            attribute_value: Attribute value if successful, None otherwise.
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

    def card_attribute(
        self,
        user_id: int,
        key: str,
        card_key: int,
        attribute: str
    ) -> Union[str, int, None]:
        """Get card attribute.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.
            attribute: The name of the attribute whose value you want to get.

        Returns:
            attribute_value: Attribute value if successful, None otherwise.
        """

        self._cursor.execute(
            sql.SQL(
                """SELECT {} FROM cards
                   WHERE user_id=%s AND
                         key=%s AND
                         card_key=%s;"""
            ).format(sql.Identifier(attribute)), (user_id, key, card_key)
        )

        attribute_value = self._cursor.fetchone()
        if attribute_value:
            return attribute_value[0]
        return None

    def user_collections(
        self,
        user_id: int
    ) -> Union(list[tuple[str, ...], ...], None):
        """Get all user collections.

        Args:
            user_id: Unique identifier of the target user.

        Returns:
            collections: All user collections.
        """

        self._cursor.execute(
            """SELECT * FROM collections WHERE user_id=%s;
            """, (user_id,)
        )

        collections = self._cursor.fetchall()
        return collections

    def collection_cards(
        self,
        user_id: int,
        key: str
    ) -> Union[list[tuple[str, ...], ...], None]:
        """Get user collection cards.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.

        Returns:
            cards: All collection cards.
        """

        self._cursor.execute(
            """SELECT * FROM cards WHERE user_id=%s and key=%s;
            """, (user_id, key)
        )

        cards = self._cursor.fetchall()
        return cards


class Update:
    """Class responsible for updating data in the database.

    Attributes:
        db_name: Name of the database to connect to.
    """

    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

        self._connection = None
        self._cursor = None

    def __enter__(self) -> Update:
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def user_attribute(
        self,
        user_id: int,
        attribute: str,
        value: Union[str, int]
    ) -> None:
        """Update user attribute value.

        Args:
            user_id: Unique identifier of the target user.
            attribute: The name of the attribute whose
                value you want to update.
            value: New attribute value.
        """

        self._cursor.execute(
            sql.SQL(
                "UPDATE users SET {}=%s WHERE user_id=%s;"
            ).format(sql.Identifier(attribute)), (value, user_id)
        )

    def collection_attribute(
        self,
        user_id: int,
        key: str,
        attribute: str,
        value: Union[str, int]
    ) -> None:
        """Update collection attribute value.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            attribute: The name of the attribute whose
                value you want to update.
            value: New attribute value.
        """

        self._cursor.execute(
            sql.SQL(
                "UPDATE collections SET {}=%s WHERE user_id=%s AND key=%s;"
            ).format(sql.Identifier(attribute)), (value, user_id, key)
        )

    def card_attribute(
        self,
        user_id: int,
        key: str,
        card_key: str,
        attribute: str,
        value: Union[str, int]
    ) -> None:
        """Update card attribute value.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.
            attribute: The name of the attribute whose
                value you want to update.
            value: New attribute value.
        """

        self._cursor.execute(
            sql.SQL(
                """UPDATE cards SET {}=%s
                   WHERE user_id=%s AND
                         key=%s AND
                         card_key=%s;"""
            ).format(sql.Identifier(attribute)), (value, user_id, key, card_key)
        )


class Delete:
    """Class responsible for deleting data from the database.

    Attributes:
        db_name: Name of the database to connect to.
    """

    def __init__(self, db_name: str) -> None:
        self._db_name = db_name

        self._connection = None
        self._cursor = None

    def __enter__(self) -> Delete:
        self._connection = psycopg2.connect(
            dbname=self._db_name,
            user=database["user"], password=database["passwd"],
            host=database["host"], port=database["port"]
        )
        self._cursor = self._connection.cursor()

        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()

        self._cursor.close()
        self._connection.close()

    def collection(self, user_id: int, key: str) -> None:
        """Delete user collection.

        Args:
            user_id: Unique identifier of the target user.
            key: Unique identifier for the collection.
        """

        self._cursor.execute(
            """DELETE FROM collections
               WHERE user_id=%s AND
                     key=%s;
            """, (user_id, key)
        )
