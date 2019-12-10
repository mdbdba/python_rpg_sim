from PlayerCharacterClass import PlayerCharacterClass


class WarlockPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Warlock",
                                      character_altering_class_options)
        self.archetype_label = "Otherworldly Patron"
        self.melee_weapon = "Dagger"
        self.melee_weapon_offhand = "Dagger"
        self.ranged_weapon = "Crossbow, light"
        self.ranged_ammunition_type = "Bolt"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.background = "Charlatan"

