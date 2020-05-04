from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class PaladinPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Paladin",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Sacred Oath"
        self.melee_weapon = "Greataxe"
        self.ranged_weapon = "Javelin"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 5
        self.armor = "Chain mail"
        self.background = "Noble"
        self.feature_list = ['Lay on Hands','Divine Smite', 'Spellcasting', 'Channel Divinity']
