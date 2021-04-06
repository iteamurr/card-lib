"""
    Bot configuration module.
"""

telegram = {
    "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    "url": "https://api.telegram.org/bot{}/{}"
}

database = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "passwd": "postgres"
}

bot_settings = {
    "collections_per_page": 8,
    "cards_per_page": 8,
    "performance_rating": 0.6
}
