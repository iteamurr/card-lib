"""
    Module with menu templates and frequently used functions.
"""

from .tools import Tools
from .tools import MenuTemplate


class CollectionTemplates:
    """Collection menu templates.
    """

    @staticmethod
    def info_template(locale: str, key: str) -> MenuTemplate:
        """Info menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Info menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="collection_learning",
                    name=f"collection_learning/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRsSe", data="collection_cards",
                    name=f"collection_cards/{key}", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="public_key",
                    name=f"public_key/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="settings",
                    name=f"edit_collection/{key}", locale=locale
                ),
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name="private_office", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLsSe", data="back",
                    name="collections", locale=locale
                ),
            )
        )

        return template

    @staticmethod
    def collections_template(locale: str) -> MenuTemplate:
        """Collections menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.

        Returns:
            template: Collections menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLsSe", data="add_collection",
                    name="add_collection", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="private_office",
                    name="back", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def public_key_template(locale: str, key: str) -> MenuTemplate:
        """Public Key menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Public Key menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{key}", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def edit_menu_template(locale: str, key: str) -> MenuTemplate:
        """Edit Menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Edit Menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="edit_name",
                    name=f"edit_name/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="edit_description",
                    name=f"edit_description/{key}", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="delete_collection",
                    name=f"delete_collection/{key}", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name=f"private_office/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{key}", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def delete_menu_template(locale: str, key: str) -> MenuTemplate:
        """Delete Menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Delete Menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data="confirm_deletion",
                    name=f"confirm_delete/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="undo_delete",
                    name=f"edit_collection/{key}", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def delete_confirmation_template(locale: str) -> MenuTemplate:
        """Delete Confirmation menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.

        Returns:
            template: Delete Confirmation menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="collections", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def new_collection_template(key: str, name: str) -> MenuTemplate:
        """New Collection message template.

        Args:
            key: Unique identifier for the collection.
            name: Collection name.

        Returns:
            template: New Collection message template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.button_template(
                    header="CoLSe", data=f"info/{key}", name=name
                )
            )
        )

        return template


class CardTemplates:
    """Card menu templates.
    """

    @staticmethod
    def info_template(locale: str, key: str, card_key: str) -> MenuTemplate:
        """Card info menu template.

        Args:
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.

        Returns:
            template: Card info menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CaRSe", data="edit_name",
                    name=f"edit_name/{key}/{card_key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRSe", data="edit_description",
                    name=f"edit_description/{key}/{card_key}", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="main",
                    name=f"private_office/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{key}", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def cards_template(locale: str, key: str) -> MenuTemplate:
        """Cards menu template.

        Args:
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Cards menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CaRsSe", data="add_card",
                    name=f"add_card/{key}", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data="back",
                    name=f"info/{key}", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def new_card_template(key: str, card_key: str, name: str) -> MenuTemplate:
        """New Card menu template.

        Args:
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.
            name: Card name.

        Returns:
            template: New Card menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.button_template(
                    header="CaRSe", data=f"info/{key}/{card_key}", name=name
                )
            )
        )

        return template
