from helpers import *
from character import Character, CharacterError

try:
    c = Character(input("Give me the name of the person:\n"))
except CharacterError as e:
    print(e)
    exit()

print(c)

print("Tech details for infobox:")
print("|character = ",c.skald_name)
print("|soul_name = ", c.soul_name)
print("|soul_id = ", c.soul_id)

