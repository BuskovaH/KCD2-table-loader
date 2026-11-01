from helpers import Table, Localization
from config import ROOT

class Item:
    """One item: one row of item.xml plus its English name and description.

    this is only to be used when dealing with an item separately,
    not as part of a character's inventory.
    why? because I like my SSD that's why.

    Don't call Item(...) yourself. Use Item.search(query), which returns a
    list with one Item for every row that matches:

        for i in Item.search("sword"):
            print(i)
    """

    FIELDS = ("name", "description", "properties")

    # The two tables are loaded once, the first time they're needed, and
    # shared by every Item and every search, so 20 hits don't mean 20 loads.
    full_item_table = None
    localization_table = None

    @classmethod
    def load_tables(cls):
        if cls.full_item_table is None:
            cls.full_item_table = Table().load(ROOT + "Data/Tables.pak/Libs/Tables/item/item.xml")
            cls.localization_table = Localization().load(ROOT + "Localization/English_xml.pak/text_ui_items.xml")

    @classmethod
    def search(cls, query):
        """List of Items, one per matching row (empty list if nothing matches)."""
        cls.load_tables()
        items = []
        for row in cls.table_search(query):
            items.append(cls(row))
        return items

    def __init__(self, row):
        """`row` is one row (a dict) of item.xml, as found by table_search."""
        self.load_tables()
        self.properties = row
        self.name = self.localization_table.get(row.get('UIName'), 1, default="Mystery bag")
        self.description = self.localization_table.get(row.get('UIInfo'), 1)

    @classmethod
    def table_search(cls, query):
        result = cls.full_item_table.search(query)
        if result == []:
            localization_query = []
            for key in cls.localization_table:
                text = cls.localization_table.get(key, 1, "")
                if query.casefold() in text.casefold() and "ui_nm_" in key:
                    localization_query.append(key[6:])
            for name in localization_query:
                for row in cls.full_item_table.search(name):
                    if row not in result:                 # no row twice
                        result.append(row)
        return result

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