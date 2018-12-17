from PlayerCharacterClass import PlayerCharacterClass


class DruidPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Druid",
                                      characterAlteringClassOptions)
        self.archetype_label = "Druid Circle"
        self.melee_weapon = "Scimitar"
        self.armor = "Leather"
        self.shield = "Shield"
