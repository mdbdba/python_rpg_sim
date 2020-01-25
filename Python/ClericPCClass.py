from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class ClericPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, classCandidate="Cleric",
                                      characterAlteringClassOptions=character_altering_class_options)
        self.archetype_label = "Divine Domain"
        self.ranged_weapon = "Crossbow, light"
        self.melee_weapon = "Warhammer"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Scale mail"
        self.shield = "Shield"
        self.background = "Acolyte"
