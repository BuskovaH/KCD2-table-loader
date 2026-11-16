from helpers import *
from character import Character, CharacterError
from item import Item
from printers import *

#investigate the error that generates when i searched for Gartered hose
#I'll handle references to files entirely in config.py in the next commit for */aesthetics/*
#Responsible garbage recycling - make sure the Localization and Item files are loaded as few times as possible.
#RNG pocket contents, money, and item quality - I don't know the shape of the distribution yet.
#Unnamed NPCs - honestly a lot of work with no reward

while True:
    switch = input('''
        What do you want to pull from the game files?
        'c' - character
        'i' - item
        'e' - exit program
        ''')
    match switch:
        case "c":
            try:
                c = Character(input("Give me the name of the person:\n"))
                infobox = Infobox.create(c)
                print(infobox)
            except CharacterError as e:
                print(e)
        case "i":
            items = Item.search(input("Give me the item name or id:\n"))
            if items == []:
                print("no item found")
            else:
                print(len(items), "item(s) found")
                for i in items:
                    print(i)
                wants_infobox_switch = input("Do you want to generate an infobox? y/n\n")
                if wants_infobox_switch == "y" and len(items) == 1:
                    index = 0
                    infobox = Infobox.create(items[index])
                    print(infobox)
                elif wants_infobox_switch == "y":
                    print("I found all of these items:")
                    for i, j in enumerate(items):
                        print(f"{i+1}: {j.properties["Name"]}")
                        #print(f"{i+1}: {j.properties["Name"]}")
                    index = int(input("Which one do you want to generate the infobox for? (number):\n")) - 1
                    infobox = Infobox.create(items[index])
                    print(infobox)
        case "e":
            break
        case _:
            print("idk what that means")
