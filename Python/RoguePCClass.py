from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class RoguePCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Rogue",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Roguish Archetype"
        self.melee_weapon = "Rapier"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Shortbow"
        self.ranged_ammunition_type = "Arrow"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.background = "Charlatan"
