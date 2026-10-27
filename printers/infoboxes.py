from character import Character
from item import Item

class Infobox:
    def __init__(self, thing): 
    #"thing" is an NPC, item, codex entry, whatever. IDK how else to name it.
        head = None
        title = None
        image = None
        appearance = None

    def __repr__(self):
        pass

class KCD2_character_infobox(Infobox):

    def grab_social_class(self, character):
        pass

class KCD2_item_infobox(Infobox):

    def grab_weapon_class(self, item):
        pass