from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class BardPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Bard",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Bard College"
        self.ranged_weapon = "Dagger"
        self.melee_weapon = "Rapier"
        self.ranged_ammunition_type = "Dagger"
        self.ranged_ammunition_amt = 1
        self.armor = "Leather"
        self.shield = None
        self.background = "Entertainer"
