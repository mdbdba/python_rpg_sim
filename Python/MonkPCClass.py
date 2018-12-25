from PlayerCharacterClass import PlayerCharacterClass


class MonkPCClass(PlayerCharacterClass):
    def __init__(self, db,
                 characterAlteringClassOptions=None):
        PlayerCharacterClass.__init__(self, db, "Monk",
                                      characterAlteringClassOptions)
        self.archetype_label = "Monastic Tradition"
        self.melee_weapon = "Shortsword"
        self.ranged_weapon = "Dart"
        self.ranged_ammunition_type = "Dart"
        self.ranged_ammunition_amt = 10
        self.background = "Hermit"
