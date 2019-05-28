import json

class Settings:
    def __init__(self, db):
        self.db = db

    def load(self):
        types = []
        categories = []

        self.settings = {"types": types, "categories": categories, "typeColors": {}}

        cursor = self.db.cursor()

        cursor.execute("SELECT name, color FROM types")
        types = cursor.fetchall()
        self.settings["types"] = [ x[0] for x in types ]

        cursor.execute("SELECT name FROM categories")
        categories = cursor.fetchall()
        self.settings["categories"] = [ x[0] for x in categories ]

        for x in types:
            self.settings["typeColors"][str(x[0])] = x[1]