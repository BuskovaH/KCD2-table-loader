from helpers import Table, Localization
from config import ROOT

def row_contains(row, phrase):
    """True if any value in the row, including nested sub-items, contains the phrase."""
    for value in row.values():
        if isinstance(value, list):
            if any(row_contains(sub, phrase) for sub in value):
                return True
        elif phrase.casefold() in value.casefold():
            return True
    return False

class Item:
    """this is only to be used when dealing with an item separately, 
    not as part of a character's inventory.
    why? because I like my SSD that's why.
    Returns as array of things... I think.
    """

    FIELDS = ("name", "description", "properties")

    def __init__(self, query):
        name = None
        properties = {}

        self.full_item_table = Table().load(ROOT + "Data/Tables.pak/Libs/Tables/item/item.xml")
        self.localization_table = Localization().load(ROOT + "Localization/English_xml.pak/text_ui_items.xml")

        self.properties = self.table_search(query)
        self.name = self.get_name()
        self.description = self.get_description()

    def table_search(self, query):

        result = []
        for row in self.full_item_table:
            if row_contains(row, query):
                result.append(row)
        if result == []:
            localization_query = []
            for key in self.localization_table:
                text = self.localization_table.get(key, 1, "")
                if query.casefold() in text.casefold() and "ui_nm_" in key:
                    localization_query.append(key[6:])
            for name in localization_query:
                for row in self.full_item_table:
                    if row_contains(row, name):
                        result.append(row)
        return result

    def get_name(self):
        for i in self.properties:
            english_name = self.localization_table.get(i['UIName'], 1, default = "Mystery item")       
            i['EnglishName'] = english_name

    def get_description(self):
        for i in self.properties:
            english_description = self.localization_table.get(i['UIInfo'], 1)
            i['EnglishDescription'] = english_description

    def to_dict(self):
        """The same dictionary `c` used to be."""
        d = {}
        for key in self.FIELDS:
            value = getattr(self, key)
            if value is not None:
                d[key] = value
        return d

    def __repr__(self):
        parts = []
        for key, value in self.to_dict().items():
            parts.append(f"    {key}={value!r}")
        return "Item(\n" + ",\n".join(parts) + "\n)"