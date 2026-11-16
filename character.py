"""Character: everything we know about one character."""
from helpers import Table, Localization
from inventory import Inventory
from config import ROOT, SOUL_CANDIDATES

class CharacterError(Exception):
    """The name given doesn't lead to exactly one character."""

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

    FIELDS = ("name", "skald_name", "soul_id", "soul_name", "inventory_refs", "full_inventory")

    def __init__(self, user_given_name):
        self.user_given_name = user_given_name
        self.name = None
        self.skald_name = None      # char_NEKDO_CAPSLOCKEM without the _uiName part
        self.soul_id = None
        self.soul_name = None
        self.inventory_refs = None
        self.full_inventory = None
        self.soul_vip_class_id = None
        self.social_class = None
        self.properties = None #preferably pull everything from infobox into this, a dict that keeps the full soul entry
        #body type is in Tables/skald/skald_character

        # determining the char name
        self.loc = Localization().load(ROOT + "Localization/English_xml.pak/text_ui_soul.xml")
        matches = self.find_matches(self.loc)

        print("a total of", len(matches), "matches.")
        if len(matches) == 0:
            self.czloc = Localization().load(ROOT + "Localization/Czech_xml.pak/text_ui_soul.xml")
            print("I will try the Czech files.")
            czmatches = self.find_matches(self.czloc)
            if len(czmatches) == 0:
                raise CharacterError("Not found in Czech or English localization files.")
            else:
                for i in czmatches:
                    matches.append([i[0], self.loc.get(i[0], 1, "")])

        if len(matches) > 1:
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
        #some inventory presets are also stored in IPL_GameData.pak/Libs/Storm/equipment/quests/
        try:
            soul_context_stripped = self.soul.sources[0][-8:-4]
            self.inventory_preset = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/item/InventoryPreset__" + soul_context_stripped + ".xml")

            self.load_inventory_refs(self.inventory_preset)
            self.get_inventory_list()
        except (IndexError, FileNotFoundError):
            self.full_inventory = "I CAN'T REACH THE INVENTORY DO NOT ASK ME WHY"

        self.get_head()

    def find_matches(self, loc):
        """Localization keys that belong to a character (they contain "char_")
        and whose third-column text contains the name the user gave."""
        #getting their uiname from localization files: it's char_NEKDO_CAPSLOCKEM_uiName
        #unnamed characters have their soul directly in Loc:
        #<Row><Cell>soul_ui_name_townsman</Cell><Cell>Měšťan</Cell><Cell>Měšťan</Cell></Row>
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
            if probe.search(self.skald_name):             # any row mentions the name
                soul.append(path)                         # only files that matched go in
        return soul

    def get_social_class(self, id):
        social_class_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/social_class.xml")
        print(social_class_table[0])
        row = social_class_table.where(social_class_id = id)[0]
        return row["social_class_name"]

    def load_soul(self, soul):
        """Fill soul_id and soul_name from the first row of `soul` that is this character."""
        try:
            row = soul.where(skald_character_name=self.skald_name)[0]
            self.soul_id = row["soul_id"]
            self.soul_name = row["soul_name"]
            self.soul_vip_class_id = row["soul_vip_class_id"]
            try:
                self.social_class = self.get_social_class(row["social_class_id"])
            except KeyError:
                self.social_class = ""
            self.properties = row
        except IndexError:
            raise CharacterError("Soul file not found - check if it's not missing in config.py.")

    def load_inventory_refs(self, inventory_preset):
        """Fill the gear references from this character's entry in `inventory_preset`."""
        #some inventories will also hide in InventoryPreset__uniqueCharacters.xml
        try:
            inventory = inventory_preset.where(Name=("inventory_" + self.soul_name))[0]
        except IndexError:
            inventory = {}
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
            
    def get_head(self):
        soul_context_stripped = self.soul.sources[0][-8:-4]
        head_table = Table().load(ROOT + "/Data/IPL_GameData.pak/Libs/Storm/appearance/common/appearance_" + soul_context_stripped + ".xml")
        #can also hide in appearance_poustevnici, appearance_unique, a appearance_cin_universal
        row = head_table.search(self.soul_name)
        # je to takhle protože někdy to je "name" a někdy "Name" a je to fakt random
        try:
            entry = row[0]["operations"][0]["setHead"][0]
            self.head = entry.get("Name", entry.get("name"))
        except KeyError:
            pass 
        try:
            entry = row[0]["operations"][0]["setHair"][0]
            self.hair = entry.get("Name", entry.get("name"))
        except KeyError:
            pass
        try:
            entry = row[0]["operations"][0]["setBeard"][0]
            self.beard = entry.get("Name", entry.get("name"))
        except KeyError:
            pass
        try:
            entry = row[0]["operations"][0]["setBody"][0]
            self.body = entry.get("Name", entry.get("name"))
        except KeyError:
            pass
        
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
