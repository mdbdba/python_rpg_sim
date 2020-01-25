from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class FighterPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, classCandidate="Fighter",
                                      characterAlteringClassOptions=character_altering_class_options)
        self.archetype_label = "Martial Archetype"
        self.melee_weapon = "Glaive"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Chain mail"
        self.background = "Soldier"
