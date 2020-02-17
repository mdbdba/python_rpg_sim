from PlayerCharacterClass import PlayerCharacterClass
from Ctx import Ctx
from Ctx import ctx_decorator


class WizardPCClass(PlayerCharacterClass):
    @ctx_decorator
    def __init__(self, db, ctx,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db=db, ctx=ctx, class_candidate="Wizard",
                                      character_altering_class_options=character_altering_class_options)
        self.archetype_label = "Arcane Tradition"
        self.melee_weapon = "Dagger"
        self.background = "Sage"
