from PlayerCharacterClass import PlayerCharacterClass


class MonkPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 character_altering_class_options=None):
        PlayerCharacterClass.__init__(self, db, "Monk",
                                      character_altering_class_options)
        self.archetype_label = "Monastic Tradition"
        self.melee_weapon = "Shortsword"
        self.ranged_weapon = "Dart"
        self.ranged_ammunition_type = "Dart"
        self.ranged_ammunition_amt = 10
        self.background = "Hermit"
