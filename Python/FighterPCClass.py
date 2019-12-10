from PlayerCharacterClass import PlayerCharacterClass


class FighterPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Fighter",
                                      character_altering_class_options)
        self.archetype_label = "Martial Archetype"
        self.melee_weapon = "Glaive"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Chain mail"
        self.background = "Soldier"
