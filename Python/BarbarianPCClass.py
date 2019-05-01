from PlayerCharacterClass import PlayerCharacterClass


class BarbarianPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Barbarian",
                                      character_altering_class_options)
        self.archetype_label = "Primal Path"
        self.ranged_weapon = "Javelin"
        self.melee_weapon = "Greataxe"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 4
        self.armor = None
        self.shield = None
        self.background = "Outlander"
