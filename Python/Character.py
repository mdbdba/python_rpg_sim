from InvokePSQL import InvokePSQL
from CommonFunctions import stringToArray
from AbilityArray import AbilityArray
from Die import Die

import random


class Character(object):
    def __init__(self,
                 db,
                 genderCandidate="Random",
                 abilityArrayStr="Common",
                 level=1,
                 debugInd=0):

        self.db = db
        level = int(level)
        if level < 1 or level > 20:
            raise ValueError('Level should be between 1 and 20.')
        else:
            self.level = level

        self.TTA = self.assignTaliesinTempermentArchitype()
        self.name = None
        self.ability_array_str = abilityArrayStr
        self.ability_base_array = [6, 6, 6, 6, 6, 6]
        self.ability_sort_array = [5, 3, 2, 4, 1, 0]
        self.ability_array = [6, 6, 6, 6, 6, 6]
        self.ability_modifier_array = [0, 0, 0, 0, 0, 0]
        self.damage_taken = dict(Acid=0, Bludgeoning=0, Cold=0,
                                 Fire=0, Force=0, Ligtning=0,
                                 Necrotic=0, Piercing=0, Poison=0,
                                 Psychic=0, Radiant=0, Slashing=0,
                                 Thunder=0, Total=0, Unknown=0)
        self.damage_dealt = dict(Acid=0, Bludgeoning=0, Cold=0,
                                 Fire=0, Force=0, Ligtning=0,
                                 Necrotic=0, Piercing=0, Poison=0,
                                 Psychic=0, Radiant=0, Slashing=0,
                                 Thunder=0, Total=0, Unknown=0)
        self.damage_adj = dict(Acid="", Bludgeoning="", Cold="", Fire="",
                               Force="", Ligtning="", Necrotic="", Piercing="",
                               Poison="", Psychic="", Radiant="", Slashing="",
                               Thunder="")
        self.healing_received = 0
        self.alive = True
        self.stabilized = True
        self.level = level
        self.hit_points = None
        self.temp_hit_points = None
        self.cur_hit_points = None
        self.height = None
        self.weight = None
        self.cur_movement = None

        self.proficiency_bonus = None
        self.armor_class = 0
        self.death_save_passed_cnt = 0
        self.death_save_failed_cnt = 0
        self.debugInd = debugInd
        self.debugStr = ''
        self.lastMethodLog = ''
        if genderCandidate == "Random":
            self.gender = self.assignGender(db)
        else:
            self.gender = genderCandidate

        self.ranged_weapon = None
        self.melee_weapon = None
        self.ranged_ammunition_type = None
        self.ranged_ammunition_amt = None
        self.armor = None
        self.shield = None

    def assignGender(self, db):
        self.lastMethodLog = (f'assignGender(db)')
        d = Die(100)
        a = d.roll()
        if a <= 40:
            result = "M"
        elif a > 40 and a <= 90:
            result = "F"
        else:
            result = "U"
        return result

    def getGender(self):
        return self.gender

    def assignAbilityArray(self, sortArray=None):
        self.lastMethodLog = (f'assignAbilityArray('
                              f'{self.ability_array_str})')
        # if the string doesn't begin and end with a number, then it must
        # be a type that the ability array wants
        tmp = self.ability_array_str
        if (tmp[1].isdigit() and tmp[-1].isdigit()):
            tmp_array = stringToArray(tmp)
            self.ability_array_obj = AbilityArray(array_type="Predefined",
                                                  raw_array=tmp_array,
                                                  pref_array=sortArray)
            self.rawAbilityArray = self.ability_array_obj.getArray()
        else:
            self.ability_array_obj = AbilityArray(array_type=tmp,
                                                  pref_array=sortArray)
            self.rawAbilityArray = self.ability_array_obj.getArray()

    def getRawAbilityArray(self):
        return self.ability_array_obj.getRawArray()

    def getAbilityPrefArray(self):
        return self.ability_array_obj.getPrefArray()

    def getSortedAbilityArray(self):
        return self.ability_array_obj.getArray()

    def assignTaliesinTempermentArchitype(self):
        self.lastMethodLog = (f'assignTaliesinTempermentArchitype()')
        alignArray = ['Bashful', 'Doc', 'Grumpy', 'Happy', 'Sneezy',
                      'Sleepy', 'Dopey']
        alignType = alignArray[(random.randint(0, 6))]
        perArray = ['High', 'Mid', 'Low']
        perType = perArray[(random.randint(0, 2))]

        return (f"{alignType}/{perType}")

    def getTTA(self):
        return self.TTA

    def getMovement(self):
        return 15

    def zeroMovement(self):
        self.lastMethodLog = (f'zeroMovement()')
        self.cur_movement = 0

    def halfMovement(self):
        self.lastMethodLog = (f'halfMovement()')
        self.cur_movement = self.cur_movement // 2

    def doubleMovement(self):
        self.lastMethodLog = (f'doubleMovement()')
        self.cur_movement = self.getBaseMovement() * 2

    def resetMovement(self):
        self.lastMethodLog = (f'resetMovement()')
        self.cur_movement = self.getBaseMovement()

    def changeExhaustionLevel(self, amount):
        self.lastMethodLog = (f'changeExhaustionLevel({amount})')
        orig_level = self.exhaustion_level
        self.exhaustion_level += amount

        # 1   Disadvantage on Ability Checks
        # 2   Speed halved
        # 3   Disadvantage on Attack rolls and Saving Throws
        # 4   Hit point maximum halved
        # 5   Speed reduced to 0
        # 6   Death

        if self.exhaustion_level >= 2:
            self.halfMovement()
        elif (orig_level > self.exhaustion_level
              and self.exhaustion_level < 2):  # recovery
            self.resetMovement()

        if self.exhaustion_level >= 5:
            self.zeroMovement()
        elif (orig_level > self.exhaustion_level
              and self.exhaustion_level < 5):  # recovery
            self.halfMovement()

        if self.exhaustion_leve >= 6:
            self.alive = False

    def getAbilityModifier(self, ability):
        self.lastMethodLog = (f'getAbilityModifier('
                              f'{ability})')
        res = 0
        if (ability == 'Strength'):
            res = self.ability_modifier_array[0]
        if (ability == 'Dexterity'):
            res = self.ability_modifier_array[1]
        if (ability == 'Constitution'):
            res = self.ability_modifier_array[2]
        if (ability == 'Intelligence'):
            res = self.ability_modifier_array[3]
        if (ability == 'Wisdom'):
            res = self.ability_modifier_array[4]
        if (ability == 'Charisma'):
            res = self.ability_modifier_array[5]

        return res

    def assignHitPoints(self, level, hit_die, modifier):
        self.lastMethodLog = (f'assignHitPoints( '
                              f'{level}, '
                              f'{hit_die}, '
                              f'{modifier})')
        return ((level * hit_die) + (level * modifier))

    def setArmorClass(self):
        self.lastMethodLog = (f'setArmorClass()')
        dexMod = -99
        baseAC = 10
        if self.armor is not None and self.armor != 'None':
            sql = (f"select ac_base from dnd_5e.lu_armor "
                   f"where name = '{self.armor}';")

            res = self.db.query(sql)
            baseAC = res[0][0]

            sql = (f"select ac_use_dex_mod, ac_dex_mod_max "
                   f"from dnd_5e.lu_armor "
                   f"where name = '{self.armor}';")

            res = self.db.query(sql)
            if (res[0][0] is False):
                dexMod = 0
            elif (res[0][1] != -1):
                dexMod = res[0][1]
            else:
                dexMod = -99

        if (dexMod == -99):
            dexMod = self.getAbilityModifier('Dexterity')

        if self.shield is not None and self.shield != 'None':
            sql = (f"select ac_base from dnd_5e.lu_armor "
                   f"where name = '{self.shield}';")

            res = self.db.query(sql)
            shieldBonus = res[0][0]
        else:
            shieldBonus = 0

        self.armor_class = baseAC + shieldBonus + dexMod


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = Character(db)
    a1.assignAbilityArray()
    a1.setArmorClass()
    print(a1.getGender())
    print(a1.rawAbilityArray)
    a2 = Character(db=db, abilityArrayStr='10,11,12,13,14,15')
    a2.assignAbilityArray()
    a2.setArmorClass()
    print(a2.getRawAbilityArray())
    print(a2.getAbilityPrefArray())
    print(a2.getSortedAbilityArray())
    a2.ability_array_obj.setPreferenceArray(prefArray=stringToArray(
                                            '5,0,2,1,4,3'
                                            ))
    print(a2.getRawAbilityArray())
    print(a2.getAbilityPrefArray())
    print(a2.getSortedAbilityArray())
    print(a2.armor_class)
    print(a2.getGender())

    # a3 = Character(db, level=43)
