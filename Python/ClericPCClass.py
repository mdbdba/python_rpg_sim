from PlayerCharacterClass import PlayerCharacterClass


class ClericPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Cleric",
                                      character_altering_class_options)
        self.archetype_label = "Divine Domain"
        self.ranged_weapon = "Crossbow, light"
        self.melee_weapon = "Warhammer"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Scale mail"
        self.shield = "Shield"
        self.background = "Acolyte"
