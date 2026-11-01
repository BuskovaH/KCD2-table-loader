from config import ROOT
from helpers import Table, Localization

#this one just resolves any rng from pockets. Most characters only have explicitly defined attire and weapons, and then use rng to determine what they're carrying.
#InventoryPreset__stashes stores chests, nests, stuff like that
#Health="0.09" HealthVariation="0.05" in InventoryPreset could potentially mean the state of the items?????
# - no it doesn't, all pocketed items are at 100%
#Scour InventoryPreset__pockets.xml
#Scour InventoryPreset__modules.xml
#Mode="OneChild" gives one item of the list
#Tables/rpg/social_class.xml obsahuje wealth

               ''' <InventoryPreset Name="inventory_birdNest" Mode="OneChild">
                        <InventoryPresetRef Name="inventory_singleRandomBsmtComoponentCheap" Weight="0.2"/>
                        <InventoryPresetRef Name="inventory_singleRandomBsmtComoponentMid" Weight="0.1"/>
                        <InventoryPresetRef Name="inventory_singleRandomBsmtComoponentRare" Weight="0.05"/>
                        <InventoryPresetRef Name="inventory_singleRandomJewelNoGold" Weight="0.05"/>
                        <InventoryPresetRef Name="inventory_smallAmountOfEggs" Weight="2"/>
                        <PresetItem Name="player_lockpick" Weight="0.6"/>
                        <PresetItem Name="Spectacles01_m01" Weight="0.25"/>
                        <InventoryPresetRef Name="inventory_singleRandomDieBadgeLowStarter" Weight="0.2"/>
                        <InventoryPresetRef Name="inventory_singleRandomDieBadgeMidStarter" Weight="0.01"/>
                        <InventoryPresetRef Name="inventory_singleRandomDieBadgeHighStarter" Weight="0.001"/>
                        <InventoryPresetRef Name="inventory_singleRandomDieLow" Weight="0.1"/>     
                        <InventoryPresetRef Name="inventory_singleRandomDieMid" Weight="0.01"/>
                        <InventoryPresetRef Name="inventory_singleRandomDieHigh" Weight="0.001"/>
                        <InventoryPresetRef Name="inventory_smallAmountQillFeathers" Weight="2"/>     
                </InventoryPreset>'''

class Pockets:
    pockets_table = Table.load(ROOT + "/Data/Tables.pak/Libs/Tables/item/InventoryPreset__pockets.xml")
    module_table = Table.load(ROOT + "/Data/Tables.pak/Libs/Tables/item/InventoryPreset__modules.xml")

    def __init__(self, name):
        pass
