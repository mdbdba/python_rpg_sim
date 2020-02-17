from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class SorcererPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Sorcerer",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Sorcerous Origin"
        self.melee_weapon = "Dagger"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.background = "Hermit"
