import json

class Settings:
    def __init__(self):
        types = []
        categories = []

        self.settings = {"types": types, "categories": categories}

        with open("settings.json", "r+") as fp:
            self.settings = json.load(fp)