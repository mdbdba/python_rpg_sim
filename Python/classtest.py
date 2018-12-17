from InvokePSQL import InvokePSQL
# from PlayerCharacterClass import PlayerCharacterClass
from DruidPCClass import DruidPCClass

db = InvokePSQL()

a = DruidPCClass(db)
print(a)
print(a.getCharacterAlteringClassFeatures())
