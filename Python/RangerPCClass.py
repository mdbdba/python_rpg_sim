from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class RangerPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, classCandidate="Ranger",
                                      characterAlteringClassOptions=character_altering_class_options)
        self.archetype_label = "Ranger Archetype"
        self.ranged_weapon = "Longbow"
        self.melee_weapon = "Shortsword"
        self.melee_weapon_offhand = "Shortsword"
        self.ranged_ammunition_type = "Arrow"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.shield = None
        self.background = "Outlander"
