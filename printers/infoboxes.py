from character import Character
from item import Item
from helpers import Table
from config import ROOT
import textwrap

class Infobox:
    def __init__(self, thing): 
    #"thing" is an NPC, item, codex entry, whatever.
        self.thing = thing
        self.title = thing.name
        self.image = None

    @classmethod
    def create(cls, thing):
        if isinstance(thing, Character):
            return KCD2_character_infobox(thing)
        elif isinstance(thing, Item):
            return KCD2_item_infobox(thing)
        else:
            raise TypeError(f"no infobox for {type(thing).__name__}")

    def __repr__(self):
        lines = ["{{Infobox",
            f"|name = {self.title}",
            ]
        lines.extend(self.body(self.thing))
        lines.append("}}")
        return "\n".join(lines)

class KCD2_character_infobox(Infobox):

    def get_social_class(self, id):
        #social class hides in Libs/Tables/rpg/social_class.xml
        social_class_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/social_class.xml")
        print(social_class_table[0])
        row = social_class_table.where(social_class_id = id)[0]
        return row["social_class_name"].capitalize()

    def get_mortality(self, id):
        vip_class_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/soul_vip_class.xml")
        if int(id) in (0, 1, 8, 16):
            return "mortal"
        else:
            return "immortal"

    def body(self, character):
        param_list = []
        #for key, value in character.properties.items():
        #    param_list.append(f"|{key} = {value}")
        #add gender - stored as soul archetype
        param_list.append(f"|station     = {self.get_social_class(character.properties["social_class_id"])}")
        param_list.append(f"|character   = {character.properties["skald_character_name"]}")
        param_list.append(f"|soul_name   = {character.properties["soul_name"]}")
        param_list.append(f"|soul_id     = {character.properties["soul_id"]}")
        param_list.append(f"|mortality   = {self.get_mortality(character.properties["soul_vip_class_id"])}")
        try:
            param_list.append(f"|combat      = {character.properties["combat_level"]}")
        except KeyError:
            pass
        return param_list

        '''
        {{Infobox
        |name = Grozav of Borumlaca
        |brain_id = 4b914d1c-724a-a92d-3e6b-d183d35b8b98
        |combat_level = 0.9
        |digestion_multiplier = 0
        |factionName = kutnohorsko_settlements_zikmundovo_nobility_grozav
        |initial_clothing_dirt = 0
        |skald_character_name = char_GROZAV_Z_BORUMLACA_VELITEL_ZOLDAKU_ZIKMUNDOVO
        |social_class_id = 14
        |soul_archetype_id = 0
        |soul_id = 055c8d3b-36b9-49b9-a575-7fb545df6807
        |soul_name = kzik_grozav
        |soul_vip_class_id = 0
        |xp_multiplier = 0
        }}
        '''

        '''{{KCD2 Character Infobox
        |name        = 
        |image       = (will stay empty)
        |category    = 
        |category1   = 
        <!-- Basic Information -->
        |alias       = 
        |born        = 
        |nationality = 
        |region      = 
        |residence   = 
        |station     = 
        |coa         = 
        <!-- Physical Information -->
        |hair        = (will stay empty)
        |eyes        =  (will stay empty)
        |gender      = 
        <!-- Personal Information -->
        |titles      = 
        |occupation  = 
        |cause of death  =
        |rank        = 
        |affiliation = 
        |skills      = 
        <!-- Technical Information -->
        |games       = 
        |character   = 
        |soul_name   = 
        |soul_id     = 
        |combat      = 
        |mortality   = 
        |age         = 
        |body_type   = 
        }}
        '''

class KCD2_item_infobox(Infobox):

    def grab_weapon_class(self, item):
        pass

    def body(self, item):
        return [
        "|an enormous = [[Item]]",
        "|wall of = somethin",
        "|text. = hello",
        "|you have successfully called the item infobox."
        ]
        #print(type(c))

        # visibility: visibility*50 + 50
        # conspic: conspicuousness*50 + 50
        # noise = noise*100
        # maxStatus = durability
        # Price: Price/10
        # idk what visibilitycoef does
