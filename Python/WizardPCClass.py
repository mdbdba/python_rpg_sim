from PlayerCharacterClass import PlayerCharacterClass


class WizardPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Wizard",
                                      characterAlteringClassOptions)
        self.archetype_label = "Arcane Tradition"
        self.melee_weapon = "Dagger"
        self.background = "Sage"
