"""
    Module responsible for bot settings.
"""

import requests

from .database import Insert
from ..config import telegram


class SettingsPanel:
    """Bot settings panel.
    """

    @staticmethod
    def set_webhook(web: str) -> None:
        """Set bot webhook.

        Args:
            web: The address of the site where the bot is running.
        """

        url = telegram["url"].format(telegram["token"], "setWebhook")
        body = {"url": f"{web}/{telegram['token']}"}

        requests.post(url, data=body)

    @staticmethod
    def delete_webhook(web: str) -> None:
        """Delete bot webhook.

        Args:
            web: The address of the site where the bot is running.
        """

        url = telegram["url"].format(telegram["token"], "deleteWebhook")
        body = {"url": f"{web}/{telegram['token']}"}

        requests.post(url, data=body)

    @staticmethod
    def en_insert_messages() -> None:
        """Insert messages in English to the bot phrases database
        """

        with Insert("bot_messages") as ins:
            # Main
            ins.new_bot_message("private_office", "Private Office", "en")
            ins.new_bot_message("collections", "Collections", "en")
            ins.new_bot_message("settings", "Settings", "en")
            ins.new_bot_message("return_to_collection", "« Collection", "en")
            ins.new_bot_message("main", "« Private Office", "en")
            ins.new_bot_message("back", "‹ Back", "en")

            # Settings
            ins.new_bot_message("locale_settings", "Language Settings", "en")
            ins.new_bot_message("current_language",
                                "*Current language:* {}",
                                "en")
            ins.new_bot_message("change_language_to_en", "English", "en")
            ins.new_bot_message("change_language_to_ru", "Russian", "en")

            ins.new_bot_message("description_info",
                                "*Name:* {}\n*Description:* {}",
                                "en")
            ins.new_bot_message("edit_name", "Edit Name", "en")
            ins.new_bot_message("edit_description", "Edit Description", "en")

            # Collection
            ins.new_bot_message("add_collection", "+ Add Collection", "en")
            ins.new_bot_message("create_collection",
                                "Enter collection name:",
                                "en")
            ins.new_bot_message("new_collection",
                                "🎉 Your new collection has been created!" \
                                "\n\n🧠 You can already start learning, " \
                                "for this you need to create several cards " \
                                "in the 'Cards Editor' menu, and then go " \
                                "to the 'Start Learning' menu.\n\n🔑 The " \
                                "'Public Key' menu contains your " \
                                "collection key. It will help you when " \
                                "you want to share your collection with " \
                                "your friends.\n\n⚙️ In the 'Settings' " \
                                "menu of a collection, you can change its " \
                                "name and description. There is also a " \
                                "button for deleting a collection, be " \
                                "careful with it.\n\n📚 Happy learning!",
                                "en")

            # Collection Menu
            ins.new_bot_message("collection_info", "*Collection:* {}", "en")
            ins.new_bot_message("collection_learning", "Start Learning", "en")
            ins.new_bot_message("collection_cards", "Cards Editor", "en")
            ins.new_bot_message("public_key", "Public Key", "en")

            # Edit Collection
            ins.new_bot_message("edit_collection_name",
                                "Enter a new name for the collection:",
                                "en")
            ins.new_bot_message("edit_collection_description",
                                "Enter a new description for the collection:",
                                "en")
            ins.new_bot_message("collection_name_changed",
                                "Collection name changed",
                                "en")
            ins.new_bot_message("collection_description_changed",
                                "Collection description changed",
                                "en")

            ins.new_bot_message("delete_collection", "Delete collection", "en")
            ins.new_bot_message("delete_confirmation",
                                "Are you sure you want to " \
                                "delete the collection?",
                                "en")
            ins.new_bot_message("confirm_deletion", "Yes, delete", "en")
            ins.new_bot_message("undo_delete", "No, don't delete", "en")
            ins.new_bot_message("collection_deleted",
                                "The collection has been deleted." \
                                "You can go back to the list of collections:",
                                "en")

            ins.new_bot_message("public_key_text",
                                "This is the key of " \
                                "your collection:\n```{}```",
                                "en")
            ins.new_bot_message("does_not_exist",
                                "The collection no longer exists, " \
                                "bring up a new menu",
                                "en")

            # Card
            ins.new_bot_message("cards", "Collection '{}' cards:", "en")
            ins.new_bot_message("add_card", "+ Add Card", "en")
            ins.new_bot_message("create_card",
                                "Enter card name:",
                                "en")
            ins.new_bot_message("new_card",
                                "The new card has been created. " \
                                "You can already customize it:",
                                "en")

            # Edit Card
            ins.new_bot_message("edit_card_name",
                                "Enter a new name for the card:",
                                "en")
            ins.new_bot_message("edit_card_description",
                                "Enter a new description for the card:",
                                "en")
            ins.new_bot_message("card_name_changed",
                                "Card name changed",
                                "en")
            ins.new_bot_message("card_description_changed",
                                "Card description changed",
                                "en")

            ins.new_bot_message("delete_card", "Delete card", "en")
            ins.new_bot_message("card_delete_confirm",
                                "Are you sure you want to " \
                                "delete the card?",
                                "en")
            ins.new_bot_message("card_deleted",
                                "The card has been deleted. " \
                                "You can go back to the list of cards:",
                                "en")

    @staticmethod
    def ru_insert_messages() -> None:
        """Writing messages in Russian to the bot phrases database.
        """

        with Insert("bot_messages") as ins:
            # Main
            ins.new_bot_message("private_office", "Личный Кабинет", "ru")
            ins.new_bot_message("collections", "Коллекции", "ru")
            ins.new_bot_message("settings", "Настройки", "ru")
            ins.new_bot_message("return_to_collection", "« Коллекция", "ru")
            ins.new_bot_message("main", "« Личный Кабинет", "ru")
            ins.new_bot_message("back", "‹ Назад", "ru")

            # Settings
            ins.new_bot_message("locale_settings", "Настройки Языка", "ru")
            ins.new_bot_message("current_language", "*Текущий язык:* {}", "ru")
            ins.new_bot_message("change_language_to_en", "Английский", "ru")
            ins.new_bot_message("change_language_to_ru", "Русский", "ru")

            ins.new_bot_message("description_info",
                                "*Название:* {}\n*Описание:* {}",
                                "ru")
            ins.new_bot_message("edit_name", "Изменить Название","ru")
            ins.new_bot_message("edit_description", "Изменить Описание", "ru")

            # Collection
            ins.new_bot_message("add_collection", "+ Добавить Коллекцию", "ru")
            ins.new_bot_message("create_collection",
                                "Введите название коллекции:",
                                "ru")
            ins.new_bot_message("new_collection",
                                "🎉 Ваша новая коллекция создана!\n\n" \
                                "🧠 Вы уже можете начать обучение, для " \
                                "этого вам нужно создать несколько карт в " \
                                "меню «Редактор Карт», а затем перейти в " \
                                "меню «Начать Обучение».\n\n" \
                                "🔑 В меню «Публичный Ключ» находится ключ " \
                                "вашей коллекции. Он поможет вам, когда вы " \
                                "захотите поделиться коллекцией с друзьями." \
                                "\n\n⚙️ В меню «Настройки» коллекции вы " \
                                "можете изменить ее название и описание. " \
                                "Здесь же находится кнопка удаления " \
                                "коллекции, будьте осторожнее с ней. \n\n" \
                                "📚 Удачного обучения!",
                                "ru")

            # Collection Menu
            ins.new_bot_message("collection_info", "*Коллекция:* {}", "ru")
            ins.new_bot_message("collection_learning", "Начать Обучение", "ru")
            ins.new_bot_message("collection_cards", "Редактор Карт", "ru")
            ins.new_bot_message("public_key", "Публичный Ключ", "ru")

            # Edit Collection
            ins.new_bot_message("edit_collection_name",
                                "Введите новое название коллекции:",
                                "ru")
            ins.new_bot_message("edit_collection_description",
                                "Введите новое описание коллекции:",
                                "ru")
            ins.new_bot_message("collection_name_changed",
                                "Название коллекции изменено",
                                "ru")
            ins.new_bot_message("collection_description_changed",
                                "Описание коллекции изменено",
                                "ru")

            ins.new_bot_message("delete_collection", "Удалить коллекцию", "ru")
            ins.new_bot_message("delete_confirmation",
                                "Вы уверены, что хотите удалить коллекцию?",
                                "ru")
            ins.new_bot_message("confirm_deletion", "Да, удалить", "ru")
            ins.new_bot_message("undo_delete", "Нет, не удалять", "ru")
            ins.new_bot_message("collection_deleted",
                                "Коллекция удалена. " \
                                "Вы можете вернуться к списку коллекций:",
                                "ru")

            ins.new_bot_message("public_key_text",
                                "Это ключ вашей коллекции:\n```{}```",
                                "ru")
            ins.new_bot_message("does_not_exist",
                                "Коллекции больше не существует, " \
                                "вызовите новое меню",
                                "ru")

            # Card
            ins.new_bot_message("cards", "Карты коллекции «{}»:", "ru")
            ins.new_bot_message("add_card", "+ Добавить карту", "ru")
            ins.new_bot_message("create_card",
                                "Введите название карты:",
                                "ru")
            ins.new_bot_message("new_card",
                                "Новая карта создана. " \
                                "Вы уже можете настроить ее:",
                                "ru")

            # Edit Card
            ins.new_bot_message("edit_card_name",
                                "Введите новое название карты:",
                                "ru")
            ins.new_bot_message("edit_card_description",
                                "Введите новое описание карты:",
                                "ru")
            ins.new_bot_message("card_name_changed",
                                "Название карты изменено",
                                "ru")
            ins.new_bot_message("card_description_changed",
                                "Описание карты изменено",
                                "ru")

            ins.new_bot_message("delete_card", "Удалить карту", "ru")
            ins.new_bot_message("card_delete_confirm",
                                "Вы уверены, что хотите удалить карту?",
                                "ru")
            ins.new_bot_message("card_deleted",
                                "Карта удалена. " \
                                "Вы можете вернуться к списку карт:",
                                "ru")
