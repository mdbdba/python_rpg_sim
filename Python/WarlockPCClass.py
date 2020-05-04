from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class WarlockPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Warlock",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Otherworldly Patron"
        self.melee_weapon = "Dagger"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.background = "Charlatan"
        self.feature_list = ['Spellcasting', 'Eldritch Invocations']

