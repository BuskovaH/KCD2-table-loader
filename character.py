"""Character: everything we know about one character."""
from helpers import Table, Localization
from inventory import Inventory
from config import ROOT, SOUL_CANDIDATES

class CharacterError(Exception):
    """The name given doesn't lead to exactly one character."""

def row_contains(row, phrase):
    """True if any value in the row, including nested sub-items, contains the phrase."""
    for value in row.values():
        if isinstance(value, list):
            if any(row_contains(sub, phrase) for sub in value):
                return True
        elif phrase.casefold() in value.casefold():
            return True
    return False

class Character:
    """Everything we know about one character. Replaces the dictionary `c`:
    c["skald_name"] is now c.skald_name, and so on.

    Character(name, root) does the whole lookup straight away: it finds the
    character in the localization files, loads their soul and their gear
    references. `root` is the game folder, ending with a slash. Raises
    CharacterError if the name matches no character, or more than one.

    The tables it loads along the way stay available as attributes:
    loc, soul, inventory_preset, weapons, clothing, pockets, item_names.
    """

    # the fields that used to be the keys of the dictionary c
    FIELDS = ("name", "skald_name", "soul_id", "soul_name", "soul_vip_class_id", 
            "social_class", "inventory_refs", "full_inventory")

    def __init__(self, user_given_name):
        self.user_given_name = user_given_name
        self.name = None
        self.skald_name = None      # char_NEKDO_CAPSLOCKEM without the _uiName part
        self.soul_id = None
        self.soul_name = None
        self.inventory_refs = None
        self.full_inventory = None
        self.soul_vip_class_id = None
        #vip class in Libs/Tables/rpg/soul_vip_class.xml, prescribes who can't be killed and looted.
        self.social_class = None
        self.properties = None #preferably pull everything from infobox into this, a dict that keeps the full soul entry

        # determining the char name
        self.loc = Localization().load(ROOT + "Localization/English_xml.pak/text_ui_soul.xml")
        matches = self.find_matches(self.loc)

        print("a total of", len(matches), "matches.")
        if len(matches) == 0:
            raise CharacterError("no match found, come back when you have more sense")
        elif len(matches) > 1:
            index = int(input("I only deal with one character at once. \nGive me their number from the list above:\n"))-1
            matches = matches[index]
            print("continuing search.")
            if "soul_ui" in matches[0]:
                raise CharacterError("I can't deal with generic NPCs yet.")            
            self.skald_name = matches[0][:-7]                 # cut off "_uiName"
            self.name = matches[1]            
            print(self.skald_name)
            print(self.name)
        else:
            matches = matches[0]
            print("continuing search.")
            if "soul_ui" in matches[0]:
                raise CharacterError("I can't deal with generic NPCs yet.")
            self.skald_name = matches[0][:-7]                 # cut off "_uiName"
            self.name = matches[1]

        self.soul = self.find_soul_table(SOUL_CANDIDATES)
        print(self.soul.sources)                              # which files made it

        self.load_soul(self.soul)

        #InventoryPreset pull
        #fails at quest inventory presets and at special characters inventory presets
        try:
            soul_context_stripped = self.soul.sources[0][-8:-4]
            self.inventory_preset = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/item/InventoryPreset__" + soul_context_stripped + ".xml")

            self.load_inventory_refs(self.inventory_preset)
            self.get_inventory_list()
        except IndexError:
            self.full_inventory = "I CAN'T REACH THE INVENTORY DO NOT ASK ME WHY"

    def find_matches(self, loc):
        """Localization keys that belong to a character (they contain "char_")
        and whose third-column text contains the name the user gave."""
        #getting their uiname from localization files: it's char_NEKDO_CAPSLOCKEM_uiName
        #unnamed characters have their soul directly in Loc:
        #<Row><Cell>soul_ui_name_townsman</Cell><Cell>Měšťan</Cell><Cell>Měšťan</Cell></Row>
        #you can't make me do list comprehension
        matches = []
        number = 1
        for key in loc:
            text = loc.get(key, 1, "")                    # that key's third-column text
            if self.user_given_name.casefold() in text.casefold() and (("char_" in key) or ("soul_ui_name" in key)):
                matches.append([key, text])
                print(number, key, text)
                number += 1
        return matches

    def find_soul_table(self, candidates):
        """Table made of only those files in `candidates` that mention skald_name.
        The explicit list allows for priority when only the first entry is taken."""
        soul = Table()
        for path in candidates:
            probe = Table().load(path)                    # parse the file on its own first
            for row in probe:
                if row_contains(row, self.skald_name):
                    soul.append(path)                     # only files that matched go in
                    break
        return soul
    
    def get_social_class(self, id):
        #social class hides in Libs/Tables/rpg/social_class.xml
        social_class_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/social_class.xml")
        print(social_class_table[0])
        row = social_class_table.where(social_class_id = id)[0]
        return row["social_class_name"]

    def load_soul(self, soul):
        """Fill soul_id and soul_name from the first row of `soul` that is this character."""
        #blatant oversight: if char is in more than one soul file, only the first is taken
        try:
            row = soul.where(skald_character_name=self.skald_name)[0]
            self.soul_id = row["soul_id"]
            self.soul_name = row["soul_name"]
            self.soul_vip_class_id = row["soul_vip_class_id"]
            self.social_class = self.get_social_class(row["social_class_id"])
            self.properties = row
        except IndexError:
            print("SOUL FILE NOT FOUND - CHECK IF IT'S NOT MISSING IN CONFIG.PY", self)

    def load_inventory_refs(self, inventory_preset):
        """Fill the gear references from this character's entry in `inventory_preset`."""
        #some inventories will also hide in InventoryPreset__uniqueCharacters.xml
        try:
            inventory = inventory_preset.where(Name=("inventory_" + self.soul_name))[0]
        except IndexError:
            print("NO INVENTORY FOUND. IT'S POSSIBLE THE CHARACTER IS ONLY ACTIVE DURING A QUEST. I CAN'T DEAL WITH THESE YET.")
            return
        self.inventory_refs = {}
        try:
            self.inventory_refs["weapons"] = inventory["WeaponPresetRef"][0]["Name"]
        except KeyError:
            self.inventory_refs["weapons"] = None
        try:
            self.inventory_refs["clothing"] = inventory["ClothingPresetRef"][0]["Name"]
        except KeyError:
            self.inventory_refs["clothing"] = None
        try:
            self.inventory_refs["pockets"] = inventory["InventoryPresetRef"][0]["Name"]
        except KeyError:
            self.inventory_refs["pockets"] = None
        
    def get_inventory_list(self):
        if self.inventory_refs == None:
            return
        else:
            self.full_inventory = Inventory(self.inventory_refs)
        
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
        return "Character(\n" + ",\n".join(parts) + "\n)"  
