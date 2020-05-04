from InvokePSQL import InvokePSQL
# from PlayerCharacterClass import PlayerCharacterClass
from WizardPCClass import WizardPCClass

db = InvokePSQL()

a = WizardPCClass(db)
print(a)
print(a.get_character_altering_class_features())
