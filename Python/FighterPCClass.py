from PlayerCharacterClass import PlayerCharacterClass


class FighterPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Fighter",
                                      characterAlteringClassOptions)
        self.archetype_label = "Martial Archetype"
        self.melee_weapon = "Glaive"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Chain mail"
