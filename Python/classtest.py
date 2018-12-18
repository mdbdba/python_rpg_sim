from InvokePSQL import InvokePSQL
# from PlayerCharacterClass import PlayerCharacterClass
from PaladinPCClass import PaladinPCClass

db = InvokePSQL()

a = PaladinPCClass(db)
print(a)
print(a.getCharacterAlteringClassFeatures())
