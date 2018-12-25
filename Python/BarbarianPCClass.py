from PlayerCharacterClass import PlayerCharacterClass


class BarbarianPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Barbarian",
                                      characterAlteringClassOptions)
        self.archetype_label = "Primal Path"
        self.ranged_weapon = "Javelin"
        self.melee_weapon = "Greataxe"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 4
        self.armor = None
        self.shield = None
        self.background = "Outlander"
