from PlayerCharacterClass import PlayerCharacterClass


class RangerPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Ranger",
                                      character_altering_class_options)
        self.archetype_label = "Ranger Archetype"
        self.ranged_weapon = "Longbow"
        self.melee_weapon = "Shortsword"
        self.melee_weapon_offhand = "Shortsword"
        self.ranged_ammunition_type = "Arrow"
        self.ranged_ammunition_amt = 20
        self.armor = "Leather"
        self.shield = None
        self.background = "Outlander"
