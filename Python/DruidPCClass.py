from PlayerCharacterClass import PlayerCharacterClass


class DruidPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Druid",
                                      character_altering_class_options)
        self.archetype_label = "Druid Circle"
        self.melee_weapon = "Scimitar"
        self.armor = "Leather"
        self.shield = "Shield"
        self.background = "Hermit"
