from PlayerCharacterClass import PlayerCharacterClass


class SorcererPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Sorcerer",
                                      characterAlteringClassOptions)
        self.archetype_label = "Sorcerous Origin"
        self.melee_weapon = "Dagger"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.background = "Hermit"
