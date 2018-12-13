from InvokePSQL import InvokePSQL
# from PlayerCharacterClass import PlayerCharacterClass
from PlayerCharacterClass import BardClass


db = InvokePSQL()
a = BardClass(db)
print(a)
