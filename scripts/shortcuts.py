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
                    header="CoLSe", data=f"collection_learning/{key}",
                    name="collection_learning", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRsSe", data=f"collection_cards/{key}",
                    name="collection_cards", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data=f"public_key/{key}",
                    name="public_key", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data=f"edit_collection/{key}",
                    name="settings", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="private_office",
                    name="main", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="back", locale=locale
                )
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
                    header="CoLSe", data=f"info/{key}",
                    name="back", locale=locale
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
                    header="CoLSe", data=f"edit_name/{key}",
                    name="edit_name", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data=f"edit_desc/{key}",
                    name="edit_description", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data=f"delete_collection/{key}",
                    name="delete_collection", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data=f"private_office/{key}",
                    name="main", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data=f"info/{key}",
                    name="back", locale=locale
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
                    header="CoLSe", data=f"confirm_delete/{key}",
                    name="confirm_deletion", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data=f"edit_collection/{key}",
                    name="undo_delete", locale=locale
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
                    header="CaRSe", data=f"edit_name/{key}/{card_key}",
                    name="edit_name", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRSe", data=f"edit_desc/{key}/{card_key}",
                    name="edit_description", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CaRSe", data=f"delete_card/{key}/{card_key}",
                    name="delete_card", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLSe", data=f"info/{key}",
                    name="return_to_collection", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRsSe", data=f"collection_cards/{key}",
                    name="back", locale=locale
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
                    header="CaRsSe", data=f"add_card/{key}",
                    name="add_card", locale=locale
                ),
                Tools.identified_button_template(
                    header="CoLSe", data=f"info/{key}",
                    name="back", locale=locale
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

    @staticmethod
    def delete_menu_template(
        locale: str,
        key: str,
        card_key:str
    ) -> MenuTemplate:
        """Delete Menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.
            card_key: Unique identifier for the card.

        Returns:
            template: Delete Menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CaRSe", data=f"confirm_delete/{key}/{card_key}",
                    name="confirm_deletion", locale=locale
                ),
                Tools.identified_button_template(
                    header="CaRSe", data=f"info/{key}/{card_key}",
                    name="undo_delete", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def delete_confirmation_template(locale: str, key: str) -> MenuTemplate:
        """Delete Confirmation menu template.

        Args:
            locale: A variable defining the user's language and
                any special preferences that the user wants to see in
                their user interface.
            key: Unique identifier for the collection.

        Returns:
            template: Delete Confirmation menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CaRsSe", data=f"collection_cards/{key}",
                    name="return_to_collection", locale=locale
                )
            )
        )

        return template


class MenuTemplates:
    """Main menu templates
    """

    @staticmethod
    def private_office_template(locale: str) -> MenuTemplate:
        """Private Office menu template.

        Args:
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
        Returns:
            template: Private Office menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="CoLsSe", data="collections",
                    name="collections", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="settings",
                    name="settings", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def settings_template(locale: str) -> MenuTemplate:
        """Settings menu template.

        Args:
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
        Returns:
            template: Settings menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="locale_settings",
                    name="locale_settings", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="private_office",
                    name="back", locale=locale
                )
            )
        )

        return template

    @staticmethod
    def locale_settings_template(locale: str) -> MenuTemplate:
        """Locale Settings menu template.

        Args:
            locale: A variable defining the user's language and
                    any special preferences that the user wants to see in
                    their user interface.
        Returns:
            template: Locale Settings menu template.
        """

        template = Tools.menu_template(
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="en_locale",
                    name="change_language_to_en", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="ru_locale",
                    name="change_language_to_ru", locale=locale
                )
            ),
            Tools.layer_template(
                Tools.identified_button_template(
                    header="MnSe", data="private_office",
                    name="main", locale=locale
                ),
                Tools.identified_button_template(
                    header="MnSe", data="settings",
                    name="back", locale=locale
                )
            )
        )

        return template
