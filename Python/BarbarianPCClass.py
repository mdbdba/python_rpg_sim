from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator

class BarbarianPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, classCandidate="Barbarian",
                                      characterAlteringClassOptions=character_altering_class_options)
        self.archetype_label = "Primal Path"
        self.ranged_weapon = "Javelin"
        self.melee_weapon = "Greataxe"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 4
        self.armor = None
        self.shield = None
        self.background = "Outlander"
