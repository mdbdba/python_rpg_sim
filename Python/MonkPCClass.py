from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator

class MonkPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx: Ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Monk",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Monastic Tradition"
        self.melee_weapon = "Shortsword"
        self.ranged_weapon = "Dart"
        self.ranged_ammunition_type = "Dart"
        self.ranged_ammunition_amt = 10
        self.background = "Hermit"
        self.feature_list = ['Key Points']
