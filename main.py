from helpers import *
from character import Character, CharacterError

try:
    c = Character(input("Give me the name of the person:\n"))
except CharacterError as e:
    print(e)
    exit()

print(c)
