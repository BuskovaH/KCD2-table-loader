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
        lines = []
        lines.extend(self.body(self.thing))
        lines.append("}}")
        return "\n".join(lines)

class KCD2_character_infobox(Infobox):

    def region(self, source):
        #a dictionary search taking the first letter of soul_context_stripped = self.soul.sources[0][-8:-4]
        pass

    def get_social_class(self, id):
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

    def get_gender(self, id):
        print("This function got called with id", id, type(id), "0" == id)
        if id == "0":
            return "Male"
        if id == "1":
            return "Female"
        else:
            return ""
    
    def get_combat(self, level):
        # conbat level name is stored in Tables/rpg/soul_combat_level.xml
        combat_level_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/soul_combat_level.xml")
        combat_level = combat_level_table.search(level)
        return level + " (" + combat_level[0]["soul_combat_level_name"][6:] + ")"

    def body(self, character):
        lines = []
        lines.append(f"{{{{KCD2 Character Infobox")
        #for key, value in character.properties.items():
        #    param_list.append(f"|{key} = {value}")
        #add gender - stored as soul archetype
        lines.append(f"|name        = {character.name}")
        lines.append(f"|station     = {self.get_social_class(character.properties["social_class_id"])}")
        lines.append(f"|gender      = {self.get_gender(character.properties["soul_archetype_id"])}")
        try:
            lines.append(f"|combat      = {self.get_combat(character.properties["combat_level"])}")
        except KeyError:
            pass
        lines.append(f"|character   = {character.properties["skald_character_name"]}")
        lines.append(f"|soul_name   = {character.properties["soul_name"]}")
        lines.append(f"|soul_id     = {character.properties["soul_id"]}")
        lines.append(f"|mortality   = {self.get_mortality(character.properties["soul_vip_class_id"])}")
        return lines

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

    def get_item_type(self, item):
        pass

    def body(self, item):
        lines = []
        lines.append(f"{{{{KCD2 Item Infobox")
        lines.append(f"|name        = {item.name}")
        lines.append(f"image        = {item.properties["IconId"]}_icon.png")
        return lines

        # visibility: visibility*50 + 50
        # conspic: conspicuousness*50 + 50
        # noise = noise*100
        # maxStatus = durability
        # Price: Price/10
        # idk what visibilitycoef does

        '''
        | name          = 
        | image         = 
        | classification = <!-- what main category it falls under in inventory. Also helps set labels for fields -->
        | type          = 
        | subtype       = <!-- for ones that are a sub-type of a main type -->
        | min_str       = 
        | min_agi       = 
        | stab          = 
        | slash         = 
        | blunt         = 
        | power         = 
        | defence       = 
        | conspic       = 
        | noise         = 
        | visibility    = 
        | charisma      = 
        | slots         = <!-- for belts or pouches. Label header will auto change as long as subtype is set correctly -->
        | nourishment   = 
        | energy        = 
        | health        = 
        | alcohol       = 
        | durability    = 
        | length        = <!-- for books -->
        | weight        = 
        | price         = 
        <!--weak-->
        | potion_name1         = 
        | potion_desc1         = 
        | potion_nourishment1  = 
        | potion_energy1       = 
        | potion_health1       = 
        | potion_alcohol1      = 
        | potion_weight1       = 
        | potion_durability1   = 
        | potion_price1        = 
        <!--normal-->
        | potion_name2         = 
        | potion_desc2         = 
        | potion_nourishment2  = 
        | potion_energy2       = 
        | potion_health2       = 
        | potion_alcohol2      = 
        | potion_durability2   = 
        | potion_weight2       = 
        | potion_price2        = 
        <!--strong-->
        | potion_name3         = 
        | potion_desc3         = 
        | potion_nourishment3  = 
        | potion_energy3       = 
        | potion_health3       = 
        | potion_alcohol3      = 
        | potion_durability3   = 
        | potion_weight3       = 
        | potion_price3        = 
        <!--henry's-->
        | potion_name4         = 
        | potion_desc4         = 
        | potion_nourishment4  = 
        | potion_energy4       = 
        | potion_health4       = 
        | potion_alcohol4      = 
        | potion_durability4   = 
        | potion_weight4       = 
        | potion_price4        = 
        <!--recipe-->
        | recipe        = 
        | recipe_mats   = 
        | code          = 
        '''
