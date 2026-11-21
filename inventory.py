from helpers import Table, Localization
from config import *

class Inventory:
    
    FIELDS = ("weapons", "clothing", "pockets")
    
    def __init__(self, inventory_refs, rng=False):
        self.weapons_ref = inventory_refs["weapons"]
        self.clothing_ref = inventory_refs["clothing"]
        self.pockets_ref = inventory_refs["pockets"]
        
        #I'm doing this here instead of inside a method because I don't want to load a single table ten times. That's just wasteful.        
        self.item_names = Table().load(ROOT + ITEM) #IconId, UIInfo, UIName, Id, Name
        self.item_localization = Localization().load(ROOT + LOCALIZATION_ITEMS)   #only with uiname. uiinfo > desciption.
        
        self.weapons = self.get_weapons(self.weapons_ref)
        self.clothing = self.get_clothing(self.weapons_ref)
        self.pockets = self.get_pockets(self.weapons_ref, rng)
        self.rng = rng #determines if we randomly roll or if we just ignore the random things
        
    def get_name(self, item_id):       
        row = self.item_names.where(Id=item_id)
        try:
            english_name = self.item_localization.get(row[0]["UIName"], 1)
            return {"Name" : row[0]["Name"], "English name" : english_name}
        except IndexError:
            return {"Id": item_id}

    def get_weapons(self,weapons_ref):
        if weapons_ref == None:
            return None    
        weapons_dict_raw = Table().load(ROOT + WEAPON_PRESET).where(weapon_preset_name = self.weapons_ref)[0]
        weapons_id_list = []
        for i in weapons_dict_raw["weapon_preset_item"]:
            weapons_id_list.append(i["item_class_id"])
        weapons_list = []
        for i in weapons_id_list:
            weapons_list.append(self.get_name(i))
        return weapons_list
        
    def get_clothing(self,clothing_ref):
        clothing_dict_raw = Table().load(ROOT + CLOTHING_PRESET).where(clothing_preset_name = self.clothing_ref)[0]["Items"][0]["Guid"]
        clothing_id_list = []
        for i in clothing_dict_raw:
            clothing_id_list.append(i["_text"])
        clothing_list = []
        for i in clothing_id_list:
            clothing_list.append(self.get_name(i))
        return clothing_list
        
    def get_pockets(self,pockets_ref, rng):
        #pockets_fulltable = Table().load(ROOT + POCKETS_PRESET)
        pass
        
    def to_dict(self):
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
        return "Inventory(\n" + ",\n".join(parts) + "\n)"  
              