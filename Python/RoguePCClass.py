from PlayerCharacterClass import PlayerCharacterClass


class RoguePCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Rogue",
                                      characterAlteringClassOptions)
        self.archetype_label = "Roguish Archetype"
        self.melee_weapon = "Rapier"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Shortbow"
        self.ranged_ammunition_type = "Arrow"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.background = "Charlatan"
