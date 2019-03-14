import random


def getRandomClassName(db):
    sql = "select count(class) from dnd_5e.lu_class;"

    results = db.query(sql)
    result = results[0][0]

    if (result > 1):
        randNbr = random.randint(1, result)
    else:
        randNbr = 1
    sql = ("with tb as (select class, row_number() over (order by class) "
           f"as orderBy from dnd_5e.lu_class ) "
           f"select class, orderby from tb "
           f"where orderby = {randNbr};")
    results = db.query(sql)
    return results[0][0]


class PlayerCharacterClass(object):
    def __init__(self,
                 db,
                 classCandidate="Random",
                 characterAlteringClassOptions=None):
        self.name = ""
        self.subclass_of = ""
        # Strength = 0
        # Dexterity = 1
        # Constitution = 2
        # Intelligence = 3
        # Wisdom = 4
        # Charisma = 5
        self.ability_sort_str_array = ['Dexterity', 'Constitution',
                                       'Strength', 'Charisma', 'Wisdom',
                                       'Intelligence']
        self.archetype_label = 'None'
        self.ability_sort_array = [1, 2, 0, 5, 4, 3]
        self.hit_die = 4
        self.source_material = ""
        self.source_credit_url = ""
        self.ranged_weapon = None
        self.melee_weapon = "Club"
        self.ranged_ammunition_type = None
        self.ranged_ammunition_amt = 0
        self.armor = None
        self.shield = None
        self.CACF_option_candidate_array = characterAlteringClassOptions
        self.CACF_option_array = []

        if classCandidate == "Random":
            classCandidate = getRandomClassName(db)

        if self.validClassName(classCandidate, db):
            self.populateDetails(classCandidate, db)
        else:
            raise Exception(f'Could not find class: {classCandidate}')

        self.setCharacterAlteringClassFeatures(db)

    def setArmorWeapons(self):
        pass

    def validClassName(self, classCandidate, db):
        sql = (f"select count(class) from dnd_5e.lu_class where "
               f"lower(class) = lower('{classCandidate}');")
        results = db.query(sql)
        classCnt = results[0][0]
        if classCnt == 1:
            return True
        else:
            return False

    def populateDetails(self, classCandidate, db):
        sql = (f"SELECT class, hit_die, ability_pref_str, "
               f"source_material, source_credit_url, "
               f"source_credit_comment "
               f"FROM dnd_5e.lu_class where "
               f"lower(class) = lower('{classCandidate}');")
        results = db.query(sql)
        self.name = results[0][0] if results[0][0] else None
        self.hit_die = results[0][1] if results[0][1] else None
        tmp_ability_pref_str = results[0][2] if results[0][2] else None
        self.source_material = results[0][3] if results[0][3] else None
        self.source_credit_url = results[0][4] if results[0][4] else None
        self.source_credit_comment = results[0][5] if results[0][5] else None

        if tmp_ability_pref_str is not None:
            self.ability_sort_array = list(map(int,
                                           tmp_ability_pref_str.split(',')))
            for p in range(len(self.ability_sort_array)):
                if self.ability_sort_array[p] == 0:
                    self.ability_sort_str_array[p] = 'Strength'
                elif self.ability_sort_array[p] == 1:
                    self.ability_sort_str_array[p] = 'Dexterity'
                elif self.ability_sort_array[p] == 2:
                    self.ability_sort_str_array[p] = 'Constitution'
                elif self.ability_sort_array[p] == 3:
                    self.ability_sort_str_array[p] = 'Intelligence'
                elif self.ability_sort_array[p] == 4:
                    self.ability_sort_str_array[p] = 'Wisdom'
                else:
                    self.ability_sort_str_array[p] = 'Charisma'

        self.setArmorWeapons()

    def getClass(self):
        return self.name

    def getClassAbilitySortArray(self):
        return self.ability_sort_array

    def setCharacterAlteringClassFeatures(self, db):
        """ If an array of dictionaries was not passed as the
            characterAlteringClassOptions arg, randomly select the
            options for the character. """

        if self.CACF_option_candidate_array is None:
            sql = (f"with tb as (select feature_id, class, class_order_by, "
                   f"feature_order_by, option_order_by, feature_string, "
                   f"option_value, row_number() over ( "
                   f"partition by feature_string "
                   f"order by random() ) as random_feature "
                   f"from lu_character_altering_class_feature_option "
                   f"where class = '{self.name}' ) "
                   f"select feature_id, class, class_order_by, "
                   f"feature_order_by, option_order_by, "
                   f"feature_string, option_value "
                   f"from tb where random_feature = 1 "
                   f"order by feature_order_by")
            results = db.query(sql)
            ret_array = []
            if results is not None:
                for p in range(len(results)):
                    if results[p] is not None:
                        tmpDict = {
                            "class": results[p][1],
                            "feature_order_by": results[p][3],
                            "feature_string": results[p][5],
                            "option_value": results[p][6]
                        }
                        ret_array.append(tmpDict)
            self.CACF_option_array = ret_array
        else:
            self.CACF_option_array = self.CACF_option_candidate_array

    def getCharacterAlteringClassFeatures(self):
        return self.CACF_option_array

    def getClassLevelFeature(self, level, db):
        sql = (f"SELECT class, level, feature, label_1, value_1, "
               f"label_2, value_2, label_3, value_3, label_4, value_4 "
               f"from dnd_5e.lu_class_level_feature "
               f"where class = '{self.name}' "
               f"and (( level <= {level} "
               f"  and feature not in ('proficiency_bonus', "
               f"'Spellcasting')) or (level = {level} "
               f"and feature in ('proficiency_bonus', 'Spellcasting'))) "
               f"order by level desc, feature;")

        return db.query(sql)

    def __str__(self):
        outstr = (f'\nObject: {self.__class__.__name__}('
                  f'\n   class:                      {self.name},'
                  f'\n   archetype_label:            {self.archetype_label},'
                  f'\n   hit_die:                    {self.hit_die},'
                  f'\n   source_material:            '
                  f'{self.source_material}')
        if self.source_credit_url:
            outstr = (f'{outstr},\n   source_credit_url:          '
                      f'{self.source_credit_url}')
        if self.source_credit_comment:
            outstr = (f'{outstr},\n   source_credit_comment:      '
                      f'{self.source_credit_comment}')
        if self.melee_weapon is not None:
            outstr = (f'{outstr},\n   Melee Weapon:               '
                      f'{self.melee_weapon}')
        if self.ranged_weapon is not None:
            outstr = (f'{outstr},\n   Ranged Weapon:              '
                      f'{self.ranged_weapon}')
        if self.ranged_ammunition_amt is not None:
            outstr = (f'{outstr},\n   Ranged Ammo:                '
                      f'{self.ranged_ammunition_amt}')

        if self.ability_sort_array is not None:
            outstr = (f'{outstr},\n   ability_sort_array:         [')
            for p in range(len(self.ability_sort_array)):
                outstr = (f'{outstr}{self.ability_sort_array[p]}, ')

            outstr = (f'{outstr[:-2]}],\n   ability_sort_str_array      [')
            for p in range(len(self.ability_sort_str_array)):
                outstr = (f'{outstr}{self.ability_sort_str_array[p]}, ')
            outstr = (f'{outstr[:-2]}]')

        outstr = (f'{outstr}\n)\n')
        return outstr

