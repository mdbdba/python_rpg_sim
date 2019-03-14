from InvokePSQL import InvokePSQL
from CommonFunctions import stringToArray
from AbilityArray import AbilityArray
from Attack import Attack
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
        self.classEval = []
        self.ability_array_str = abilityArrayStr
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

        self.blinded_ind = False
        self.charmed_ind = False
        self.deafend_ind = False
        self.fatigued_ind = False
        self.frightened_ind = False
        self.grappled_ind = False
        self.incapacitated_ind = False
        self.invisible_ind = False
        self.paralyzed_ind = False
        self.petrified_ind = False
        self.poisoned_ind = False
        self.prone_ind = False
        self.stunned_ind = False
        self.unconcious_ind = False
        self.ranged_weapon = None
        self.melee_weapon = None
        self.ranged_ammunition_type = None
        self.ranged_ammunition_amt = None
        self.armor = None
        self.shield = None

        self.exhaustion_level = 0
        # 1   Disadvantage on Ability Checks
        # 2   Speed halved
        # 3   Disadvantage on Attack rolls and Saving Throws
        # 4   Hit point maximum halved
        # 5   Speed reduced to 0
        # 6   Death

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

        if self.debugInd:
            self.classEval[-1]["Gender"] = result

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
                                                  pref_array=sortArray,
                                                  debugInd=self.debugInd)
        else:
            self.ability_array_obj = AbilityArray(array_type=tmp,
                                                  pref_array=sortArray,
                                                  debugInd=self.debugInd)

    def getClassEval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.classEval

    def getRawAbilityArray(self):
        return self.ability_array_obj.getRawArray()

    def getAbilityPrefArray(self):
        return self.ability_array_obj.getPrefArray()

    def getNumericallySortedAbilityArray(self):
        return self.ability_array_obj.getNumericalSortedArray()

    def getAbilityPrefStrArray(self):
        return self.ability_array_obj.getPrefStrArray()

    def getSortedAbilityArray(self):
        return self.ability_array_obj.getSortedArray()

    def getAbilityArray(self):
        return self.ability_array_obj.getArray()

    def getAbilityImprovementArray(self):
        return self.ability_array_obj.getImpArray()

    def assignTaliesinTempermentArchitype(self):
        self.lastMethodLog = (f'assignTaliesinTempermentArchitype()')
        alignArray = ['Bashful', 'Doc', 'Grumpy', 'Happy', 'Sneezy',
                      'Sleepy', 'Dopey']
        alignType = alignArray[(random.randint(0, 6))]
        perArray = ['High', 'Mid', 'Low']
        perType = perArray[(random.randint(0, 2))]

        retStr = (f"{alignType}/{perType}")
        if self.debugInd:
            self.classEval[-1]["TTA"] = retStr

        return retStr

    def getTTA(self):
        return self.TTA

    def getBaseMovement(self):
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

        retStr = ((level * hit_die) + (level * modifier))
        if self.debugInd:
            self.classEval[-1]["hitPoints"] = retStr

        return retStr

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

        if self.debugInd:
            self.classEval[-1]["armorClass"] = self.armor_class

    def contestCheck(self, ability, vantage='Normal'):
        self.lastMethodLog = (f'contestCheck('
                              f'{ability}, {vantage})')
        d = Die(20)
        if (vantage == 'Normal'):
            r = d.roll()
        elif (vantage == 'Advantage'):
            r = d.rollWithAdvantage()
        elif (vantage == 'Disadvantage'):
            r = d.rollWithDisadvantage()

        mod = self.getAbilityModifier(ability)

        return (r + mod)

    def rollForInitiative(self, vantage='Normal'):
        return self.contestCheck('Dexterity', vantage)

    def checkProficiencySkill(self, ability):
        self.lastMethodLog = (f'checkProficiencySkill('
                              f'{ability})')
        retValue = False
        for b in self.raceObj.traitContainer.traits:
                if b.category == "Proficiency Skill":
                    if b.affected_name == ability:
                        retValue = True

        return retValue


    def deathSave(self, vantage='Normal'):
        self.lastMethodLog = (f'deathSave('
                              f'{vantage})')
        tmpStr = 'Performs death save.'
        res = self.contestCheck('Death', vantage)
        if (res == 20):  # character is stablized
            self.cur_hit_points = 1
            self.death_save_passed_cnt = 3
            self.stabilized = 1
            tmpStr = (f'{tmpStr}\nResult: Nat 20. Character Stabilized')
        elif (res >= 10):  # normal pass
            self.death_save_passed_cnt += 1
            tmpStr = (f'{tmpStr}\nPassed. Current counts: (P/F) '
                      f'{self.death_save_passed_cnt}/'
                      f'{self.death_save_failed_cnt}')
        elif (res == 1):   # crit fail
            self.death_save_failed_cnt += 2
            tmpStr = (f'{tmpStr}\nCrit fail. Current counts: (P/F) '
                      f'{self.death_save_passed_cnt}/'
                      f'{self.death_save_failed_cnt}')
        else:   # res < 10 -- normal fail
            self.death_save_failed_cnt += 1
            tmpStr = (f'{tmpStr}\nFailed. Current counts: (P/F) '
                      f'{self.death_save_passed_cnt}/'
                      f'{self.death_save_failed_cnt}')

        if (self.death_save_passed_cnt >= 3):
            self.death_save_passed_cnt = 0
            self.death_save_failed_cnt = 0
            self.stabilized = True
            tmpStr = (f'{tmpStr}\nThree passed death saves. '
                      f'Character Stabilized')
        elif (self.death_save_failed_cnt >= 3):
            self.alive = False
            tmpStr = (f'{tmpStr}\nThree failed death saves. '
                      f'Character has died.')


    def Check(self, skill, vantage='Normal', dc=10):
        self.lastMethodLog = (f'Check({skill}, '
                              f'{vantage}, {dc})')
        tmpStr = ''
        # Saving throw
        if (skill == 'Strength' or skill == 'Dexterity'
            or skill == 'Constitution' or skill == 'Intelligence'
                or skill == 'Wisdom' or skill == 'Charisma'):
                ability = skill
                # at exhaustion level 3 saving throws are affected
                if (self.exhaustion_level >= 3):
                    if (vantage == 'Advantage'):
                        vantage = 'Normal'
                    else:
                        vantage = 'Disadvantage'
                adjustedRoll = self.contestCheck(ability, vantage)
        else:
            # Skill Check
            if skill == 'Athletics':
                ability = 'Strength'
            elif (skill == 'Acrobatics'
                  or skill == 'Sleight of Hand'
                  or skill == 'Stealth'):
                ability = 'Dexterity'
            elif (skill == 'Arcana'
                  or skill == 'History'
                  or skill == 'Investigation'
                  or skill == 'Nature'
                  or skill == 'Religion'):
                ability = 'Intelligence'
            elif (skill == 'Animal Handling'
                  or skill == 'Insight'
                  or skill == 'Medicine'
                  or skill == 'Perception'
                  or skill == 'Survival'):
                ability = 'Wisdom'
            elif (skill == 'Deception'
                  or skill == 'Intimidation'
                  or skill == 'Performance'
                  or skill == 'Persuasion'):
                ability = 'Charisma'
            if (self.debugInd):
                tmpStr = (f'{tmpStr}{skill} ')
            # at exhaustion level 1 skills checks are affected
            if (self.exhaustion_level >= 1):
                if (vantage == 'Advantage'):
                    vantage = 'Normal'
                else:
                    vantage = 'Disadvantage'
            adjustedRoll = self.contestCheck(ability, vantage)

            if(self.checkProficiencySkill(skill)):
                adjustedRoll = adjustedRoll + self.proficiency_bonus
                tmpStr = (f'{tmpStr} + Prof({self.proficiency_bonus}) ')

        if (adjustedRoll >= dc):
            res = True
        else:
            res = False

        if (self.debugInd):
            tmpStr = (f'{tmpStr}{adjustedRoll} >= {dc} ')
            if (res):
                tmpStr = (f'{tmpStr} (true)\n')
            else:
                tmpStr = (f'{tmpStr} (false)\n')

        return res

    def rangedAttack(self, weaponObj, vantage='Normal'):
        # determine modifier
        # 1)  is this a martial weapon that needs specific proficiency
        #     if it is and the character has that, or the weapon is a standard
        #     one, add the character's proficiency bonus.
        if     (weaponObj.martial_weapon_ind is False  # NOQA
                or (weaponObj.martial_weapon_ind is True
                and weaponObj.proficient_ind is True)):
            modifier = int(self.proficiency_bonus)
        else:
            modifier = 0

        modifier += self.getAbilityModifier('Dexterity')

        attempt = Attack(weaponObj=weaponObj, attackModifier=modifier,
                         versatile_use_2handed=False, vantage=vantage)

        print(f'Attack Value: {attempt.attack_value}')
        print(f'Poss. Damage: {attempt.possible_damage}')

    def meleeAttack(self, weaponObj, vantage='Normal'):
        # determine modifier
        # 1)  is this a martial weapon that needs specific proficiency
        #     if it is and the character has that, or the weapon is a standard
        #     one, add the character's proficiency bonus.
        if     (weaponObj.martial_weapon_ind is False  # NOQA
                or (weaponObj.martial_weapon_ind is True
                and weaponObj.proficient_ind is True)):
            modifier = int(self.proficiency_bonus)
        else:
            modifier = 0
        # 2)  Add the users Ability bonus, Strength for standard weapons
        #     or self.finesse_ability_mod for Finesse wepons
        if     (weaponObj.finesse_ind is True):  # NOQA
            modifier += self.getAbilityModifier(self.self.finesse_ability_mod)
        else:
            modifier += self.getAbilityModifier('Strength')

        if     (self.classObj.shield is None  # NoQA
                and weaponObj.versatile_ind is True):
            v2h = True
        else:
            v2h = False

        attempt = Attack(weaponObj=weaponObj, attackModifier=modifier,
                         versatile_use_2handed=v2h, vantage=vantage)

        print(f'Attack Value: {attempt.attack_value}')
        print(f'Poss. Damage: {attempt.possible_damage}')

    def meleeDefend(self, modifier=0, vantage='Normal',
                    possibleDamage=0, damageType='Unknown'):
        self.lastMethodLog = (f'meleeDefend({modifier}, '
                              f'{vantage}, {possibleDamage}, '
                              f'{damageType})')
        d = Die(20)
        if self.prone_ind:
            if vantage == 'Disadvantage':
                vantage = 'Normal'
            else:
                vantage = 'Advantage'
        value = d.roll() + modifier

        if value >= self.armor_class:
            tmpStr = (f'Fails against a melee attack roll: '
                      f'{value} >= {self.armor_class}')
            ret = False
            if possibleDamage > 0:
                self.Damage(possibleDamage, damageType)
        else:
            tmpStr = (f'Succeeds against a melee attack roll: '
                      f'{value} < {self.armor_class}')
            ret = True

        return ret

    def rangedDefend(self, modifier=0, vantage='Normal',
                     possibleDamage=0, damageType='Unknown'):
        self.lastMethodLog = (f'rangedDefend({modifier}, '
                              f'{vantage}, {possibleDamage}'
                              f'{damageType})')
        d = Die(20)
        if self.prone_ind:
            if vantage == 'Advantage':
                vantage = 'Normal'
            else:
                vantage = 'Disadvantage'
        value = d.roll() + modifier

        if value >= self.armor_class:
            tmpStr = (f'Fails against a ranged attack roll: '
                      f'{value} >= {self.armor_class}')
            ret = False
            if possibleDamage > 0:
                self.Damage(possibleDamage, damageType)
        else:
            tmpStr = (f'Succeeds against a ranged attack roll: '
                      f'{value} < {self.armor_class}')
            ret = True

        return ret


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


