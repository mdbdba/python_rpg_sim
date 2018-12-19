from InvokePSQL import InvokePSQL
# from PlayerCharacterClass import PlayerCharacterClass
from RangerPCClass import RangerPCClass

db = InvokePSQL()

a = RangerPCClass(db)
print(a)
print(a.getCharacterAlteringClassFeatures())
