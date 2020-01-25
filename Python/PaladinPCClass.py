from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class PaladinPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, classCandidate="Paladin",
                                      characterAlteringClassOptions=character_altering_class_options)
        self.archetype_label = "Sacred Oath"
        self.melee_weapon = "Greataxe"
        self.ranged_weapon = "Javelin"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 5
        self.armor = "Chain mail"
        self.background = "Noble"
