from PlayerCharacterClass import PlayerCharacterClass


class PaladinPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Paladin",
                                      character_altering_class_options)
        self.archetype_label = "Sacred Oath"
        self.melee_weapon = "Greataxe"
        self.ranged_weapon = "Javelin"
        self.ranged_ammunition_type = "Javelin"
        self.ranged_ammunition_amt = 5
        self.armor = "Chain mail"
        self.background = "Noble"
