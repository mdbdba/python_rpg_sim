from PlayerCharacterClass import PlayerCharacterClass


class BardPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Bard",
                                      characterAlteringClassOptions)
        self.archetype_label = "Bard College"
        self.ranged_weapon = "Dagger"
        self.melee_weapon = "Rapier"
        self.ranged_ammunition_type = "Dagger"
        self.ranged_ammunition_amt = 1
        self.armor = "Leather"
        self.shield = None
        self.background = "Entertainer"
