from PlayerCharacterClass import PlayerCharacterClass


class WizardPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Wizard",
                                      character_altering_class_options)
        self.archetype_label = "Arcane Tradition"
        self.melee_weapon = "Dagger"
        self.background = "Sage"
