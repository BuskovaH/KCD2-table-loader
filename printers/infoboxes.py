from character import Character
from item import Item
from helpers import Table
from config import ROOT, SOCIAL_CLASS, LOCATIONS, COMBAT_LEVEL
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

    def location(self, source):
        #a dictionary search
        locations = LOCATIONS
        pass

    def get_social_class(self, id):
        social_class_table = Table().load(ROOT + SOCIAL_CLASS)
        row = social_class_table.where(social_class_id = id)[0]
        return row["social_class_name"].capitalize()

    def get_mortality(self, id):
        #vip_class_table = Table().load(ROOT + "/Data/Tables.pak/Libs/Tables/rpg/soul_vip_class.xml")
        if int(id) in (0, 1, 8, 16):
            return "mortal"
        else:
            return "immortal"

    def get_gender(self, id):
        if id == "0":
            return "Male"
        if id == "1":
            return "Female"
        else:
            return ""
    
    def get_combat(self, level):
        # conbat level name is stored in Tables/rpg/soul_combat_level.xml
        combat_level_table = Table().load(ROOT + COMBAT_LEVEL)
        combat_level = combat_level_table.search(level[:3])
        return level + " (" + combat_level[0]["soul_combat_level_name"][6:] + ")"

    def body(self, character):
        lines = []
        lines.append(f"{{{{KCD2 Character Infobox")
        #for key, value in character.properties.items():
        #    param_list.append(f"|{key} = {value}")
        #add gender - stored as soul archetype
        lines.append(f"|name        = {character.name}")
        try:
            lines.append(f"|station     = {self.get_social_class(character.properties["social_class_id"])}")
        except KeyError:
            pass
        lines.append(f"|gender      = {self.get_gender(character.properties["soul_archetype_id"])}")
        try:
            lines.append(f"|combat      = {self.get_combat(character.properties["combat_level"])}")
        except KeyError:
            pass
        try:
            lines.append(f"|head_id     = {character.head}")
            lines.append(f"|hair        = {character.hair}")
        except AttributeError:
            pass
        lines.append(f"|character   = {character.properties["skald_character_name"]}")
        lines.append(f"|soul_name   = {character.properties["soul_name"]}")
        lines.append(f"|soul_id     = {character.properties["soul_id"]}")
        lines.append(f"|Affiliation = {character.properties["factionName"]}")
        lines.append(f"|mortality   = {self.get_mortality(character.properties["soul_vip_class_id"])}")
        lines.append(f"|games       = KCD2")
        return lines


class KCD2_item_infobox(Infobox):
    #weapon class hides in... weapon_class.xml. same with weapon_sub_class.

    def body_weapon(self, item):
        lines = []
        lines.append(f"|str/agi     = {item.properties["StrReq"]}/{item.properties["AgiReq"]}")
        lines.append(f"|defence     = {item.properties["Defense"]}")
        lines.append(f"|charisma    = {item.properties["Charisma"]}")
        lines.append(f"|durability  = {item.properties["MaxStatus"]}")
        return lines

    def body_food(self, item):
        lines = []
        lines.append(f"|nourishment = {item.properties["NutritionBenefit"]}")
        lines.append(f"|energy      = {item.properties["RefreshBenefit"]}")
        lines.append(f"|health      = {item.properties["HealthBenefit"]}")
        lines.append(f"|alcohol     = {item.properties["AlcoholContent"]}")
        lines.append(f"|durability  = {int(item.properties["DecayTime"])/24} days")
        return lines
    
    def body_clothing(self, item):
        lines = []
        lines.append(f"|charisma    = {item.properties["Charisma"]}")
        lines.append(f"|noise       = {float(item.properties["Noise"])*100:.0f}")
        lines.append(f"|durability  = {item.properties["MaxStatus"]}")
        lines.append(f"|visibility  = {float(item.properties["Visibility"])*50+50:.0f}")
        lines.append(f"|conspic     = {float(item.properties["Conspicuousness"])*50+50:.0f}")
        lines.append(f"|stab        = {item.properties["DefenseStab"]}")
        lines.append(f"|slash       = {item.properties["DefenseSlash"]}")
        lines.append(f"|blunt       = {item.properties["DefenseSmash"]}")
        return lines

    def body_document(self,item):
        lines = []
        lines.append(f"|length      =")
        return lines

    def body_alias(self, item):
        same_item = Item.search(item.properties["SourceItemId"])
        for i in same_item:
            if i.properties["_tag"] != "ItemAlias":
                return i

    def body(self, item):
        lines = []
        lines.append(f"{{{{KCD2 Item Infobox")
        lines.append(f"|name        = {item.name}")
        lines.append(f"|image       = {item.properties["IconId"]}_icon.png")
        lines.append(f"|type        = {item.category}")
        lines.append(f"|code1       = {item.properties["UIName"]}")
        lines.append(f"|code2       = {item.properties["Id"]}")
        if item.category == "ItemAlias":
            item = self.body_alias(self.thing)
            self.thing = item
            print("You chose an item which is an alias. The infobox will use its UID and UUID.")
        if item.category == "MeleeWeapon":
            lines.extend(self.body_weapon(self.thing))
        if item.category == "Armor":
            lines.extend(self.body_clothing(self.thing))
        if item.category == "Food":
            lines.extend(self.body_food(self.thing))
        lines.append(f"|weight      = {item.properties["Weight"]}")
        lines.append(f"|price       = {int(item.properties["Price"])/10}")
        return lines

        # maxStatus = durability

        '''
        | name          = 
        | image         = 
        | classification = <!-- what main category it falls under in inventory. Also helps set labels for fields -->
        | type          = 
        | subtype       = <!-- for ones that are a sub-type of a main type -->
        no point in implementing potions now; KCD2 is complete and KCS might have different mechanics
        '''