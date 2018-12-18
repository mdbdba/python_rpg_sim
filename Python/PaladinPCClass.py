from PlayerCharacterClass import PlayerCharacterClass


class PaladinPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Paladin",
                                      characterAlteringClassOptions)
        self.archetype_label = "Sacred Oath"
        self.melee_weapon = "Greataxe"
        self.ranged_weapon = "Javelin"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 5
        self.armor = "Chain mail"
