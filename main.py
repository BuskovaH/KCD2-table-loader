from helpers import *
from character import Character, CharacterError
from item import Item

while True:
    switch = input('''
        What do you want to pull from the game files?
        'c' - character
        'i' - item
        'exit' - exit program
        ''')
    match switch:
        case "c":
            try:
                c = Character(input("Give me the name of the person:\n"))
                print(c)

                print("Tech details for infobox:")
                print("|character = ",c.skald_name)
                print("|soul_name = ", c.soul_name)
                print("|soul_id = ", c.soul_id)

            except CharacterError as e:
                print(e)

        case "i":
            i = Item(input("Give me the item name or id:\n"))
            print(i)

        case "exit":
            break

        case _:
            print("idk what that means")
