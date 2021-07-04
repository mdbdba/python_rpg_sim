from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class DruidPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Druid",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Druid Circle"
        self.melee_weapon = "Club"
        self.armor = "Leather"
        self.shield = "Shield"
        self.background = "Hermit"
        self.feature_list = ['Spellcasting', 'Wild Shape']
