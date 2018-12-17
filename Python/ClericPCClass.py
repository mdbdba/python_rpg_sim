from PlayerCharacterClass import PlayerCharacterClass


class ClericPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Cleric",
                                      characterAlteringClassOptions)
        self.archetype_label = "Divine Domain"
        self.ranged_weapon = "Crossbow, light"
        self.melee_weapon = "Warhammer"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Scale mail"
        self.shield = "Shield"
