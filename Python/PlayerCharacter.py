from InvokePSQL import InvokePSQL
from Character import Character
from CommonFunctions import arrayToString
from CommonFunctions import stringToArray
from CommonFunctions import inchesToFeet
# from AbilityArray import AbilityArray
from CharacterRace import CharacterRace
from PlayerCharacterClass import getRandomClassName
from BardPCClass import BardPCClass
from BarbarianPCClass import BarbarianPCClass
from ClericPCClass import ClericPCClass
from DruidPCClass import DruidPCClass
from FighterPCClass import FighterPCClass
from MonkPCClass import MonkPCClass
from PaladinPCClass import PaladinPCClass
from RangerPCClass import RangerPCClass
from RoguePCClass import RoguePCClass
from SorcererPCClass import SorcererPCClass
from WarlockPCClass import WarlockPCClass
from WizardPCClass import WizardPCClass
from Weapon import Weapon
# from Attack import Attack
# from Die import Die

# import random
# import datetime


class PlayerCharacter(Character):
    def __init__(self,
                 db,
                 characterId=-1,
                 raceCandidate="Random",
                 classCandidate="Random",
                 genderCandidate="Random",
                 abilityArrayStr="Common",
                 level=1,
                 debugInd=0):

        self.db = db

        Character.__init__(self, db, genderCandidate, abilityArrayStr,
                           level, debugInd)
        if (characterId == -1):
            self.createCharacter(db,
                                 raceCandidate,
                                 classCandidate,
                                 genderCandidate,
                                 abilityArrayStr,
                                 self.level)
        else:
            self.character_id = characterId
            self.getCharacter(db, self.character_id)

        self.featureObj = self.classObj.getClassLevelFeature(self.level, db)
        self.resetMovement()
        self.setFinesseAbility()
        self.setProficiencyBonus()
        self.setDamageAdjs(db)
        self.setArmorClass()
        if (characterId == -1):
            self.saveCharacter(db)

    def assignRace(self, raceCandidate):
        self.lastMethodLog = (f'assignRace('
                              f'{raceCandidate})')
        if (raceCandidate == "Random"):
            randObj = CharacterRace(self.db, raceCandidate)
            raceToUse = randObj.race
        else:
            raceToUse = raceCandidate

        return CharacterRace(self.db, raceToUse)

    def createCharacter(self,
                        db,
                        raceCandidate,
                        classCandidate,
                        genderCandidate,
                        abilityArrayType,
                        level):

        self.lastMethodLog = (f'createCharacter(db, '
                              f'{raceCandidate}, '
                              f'{classCandidate}, '
                              f'{genderCandidate}, '
                              f'{abilityArrayType}, '
                              f'{level})')
        self.assignAbilityArray()
        self.raceObj = self.assignRace(raceCandidate)
        self.classObj = self.assignClass(classCandidate)
        self.raceObj.setRandoms(db=self.db, gender=self.gender)

        self.ability_array_obj.setPreferenceArray(self.getAbilitySortArray())
#        sortArray = self.getAbilitySortArray()
#        for r in range(len(sortArray)):
#            t = sortArray[r]
#            self.ability_base_array[t] = self.rawAbilityArray[r]

        self.ability_array_obj.setRacialArray(self.getRacialAbilityBonusArray())
#        bonusArray = self.getRacialAbilityBonusArray()
#        for r in range(len(self.ability_base_array)):
#            self.ability_array[r] = (
#                self.ability_base_array[r] + bonusArray[r])

# Since ability array bonuses are figured when levels change we will figure
# hit points the same way.  That way of the constitution mod changes from
# level to level the hit points will reflect that.

        # ability_array_history[0] will show the base array
#        self.ability_array_history.append(self.ability_base_array)
        self.hit_points = 0
        self.adjustForLevels(db)
        self.cur_hit_points = self.hit_points
        self.temp_hit_points = 0

        if (self.classObj.melee_weapon is not None):
            self.melee_weapon_obj = Weapon(db, self.getMeleeWeapon())
            self.melee_weapon_obj.setWeaponProficient()
        if (self.classObj.ranged_weapon is not None):
            self.ranged_weapon_obj = Weapon(db, self.getRangedWeapon())

    def adjustForLevels(self, db):
        for l in range((self.level)):
            level = l + 1  # range indexes start at 0.
            # if there's ability change for this level make that change
            sql = (f"select count(level) "
                   f"from dnd_5e.lu_class_level_feature "
                   f"where level = {level} "
                   f"and class = '{self.getClass()}' "
                   f"and feature = 'Ability Score Improvement';")
            result = db.query(sql)
            if (int(result[0][0]) == 1):
                # print("\n\n\nDoing abilityScoreImprovement\n\n\n")
                self.ability_array_obj.abilityScoreImprovement()
            # repopulate the ability modifier array with any new values
            q = self.getAbilityArray()
            for r in range(len(q)):
                sql = (f"select modifier "
                       f"from dnd_5e.lu_ability_score_modifier "
                       f"where value = '{q[r]}';")

                result = db.query(sql)
                self.ability_modifier_array[r] = int(result[0][0])

            # Add new hit points
            self.hit_points = self.addHitPoints(self.getHitDie(),
                                                self.ability_modifier_array[2])


    def addHitPoints(self, hit_die, modifier):
        self.lastMethodLog = (f'assignHitPoints( '
                              f'{hit_die}, '
                              f'{modifier})')
        return (self.hit_points + (hit_die + modifier))

    def saveCharacter(self, db):
        self.lastMethodLog = (f'saveCharacter(db)')
        raw_ability_string = arrayToString(self.getRawAbilityArray())
        ability_base_string = arrayToString(self.getRawAbilityArray())
        ability_string = arrayToString(self.getAbilityArray())
        ability_racial_mod_string = (
            arrayToString(self.getRacialAbilityBonusArray()))

        ability_modifier_string = arrayToString(self.ability_modifier_array)
        sql = (f"insert into dnd_5e.character(name, gender, race, class, "
               f"level, TTA, raw_ability_string, "
               f"ability_base_string,ability_string, "
               f"ability_racial_mod_string, ability_modifier_string, "
               f"hit_points, temp_hit_points, cur_hit_points, height, "
               f"weight, alignment, alignment_abbrev, skin_tone, hair_color, "
               f"hair_type, eye_color, melee_weapon, ranged_weapon, "
               f"ranged_ammunition_type, ranged_ammunition_amt, armor, shield"
               f") values ('{self.getName()}', "
               f"'{self.getGender()}', '{self.getRace()}', "
               f"'{self.getClass()}',{self.level}, '{self.TTA}', "
               f"'{raw_ability_string}', "
               f"'{ability_base_string}', '{ability_string}', "
               f"'{ability_racial_mod_string}', "
               f"'{ability_modifier_string}', {self.hit_points}, "
               f"{self.temp_hit_points}, {self.cur_hit_points}, "
               f"{self.getHeight()}, {self.getWeight()}, "
               f"'{self.getAlignmentStr()}', '{self.getAlignmentAbbrev()}', "
               f"'{self.getSkinTone()}', '{self.getHairColor()}', "
               f"'{self.getHairType()}', '{self.getEyeColor()}', "
               f"'{self.getMeleeWeapon()}', '{self.getRangedWeapon()}', "
               f"'{self.getRangedAmmunitionType()}', "
               f"{self.getRangedAmmunitionAmt()}, '{self.getArmor()}', "
               f"'{self.getShield()}')")

        self.character_id = db.insertAndReturnId(sql)

    def validCharacterId(self, db, character_id):
        self.lastMethodLog = (f'validCharacterId(db, '
                              f'{character_id})')
        sql = (f"select count(id) from dnd_5e.character where "
               f"id = {character_id};")
        results = db.query(sql)
        idCnt = results[0][0]
        if idCnt == 1:
            return True
        else:
            return False

    def getCharacter(self, db, character_id):
        self.lastMethodLog = (f'getCharacter(db, '
                              f'{character_id})')
        if self.validCharacterId(db, character_id):
            sql = (f"select name, gender, race, class, "
                   f"level, TTA, raw_ability_string, "
                   f"ability_base_string, ability_string, "
                   f"ability_racial_mod_string, ability_modifier_string, "
                   f"hit_points, temp_hit_points, cur_hit_points, height, "
                   f"weight, alignment, alignment_abbrev, skin_tone, "
                   f"hair_color, hair_type, eye_color, melee_weapon, "
                   f"ranged_weapon, ranged_ammunition_type, "
                   f"ranged_ammunition_amt, armor, shield "
                   f"from dnd_5e.character where id = {character_id}")
            results = db.query(sql)

            self.gender = results[0][1]
            self.raceObj = self.assignRace(results[0][2])
            self.raceObj.setRandoms(
                   name=results[0][0],
                   alignment={"alignment": results[0][16],
                              "abbreviation": results[0][17]},
                   skinTone=results[0][18],
                   hairColor=results[0][19],
                   hairType=results[0][20],
                   eyeColor=results[0][21])
            self.raceObj.height = results[0][14]
            self.raceObj.weight = results[0][15]
            self.classObj = self.assignClass(results[0][3])
            self.level = results[0][4]
            self.TTA = results[0][5]
            self.rawAbilityArray = stringToArray(results[0][6])
            self.ability_base_array = stringToArray(results[0][7])
            self.ability_array_str = results[0][8]
            ability_racial_mod_string = results[0][9]
            self.ability_modifier_array = stringToArray(results[0][10])
            self.hit_points = results[0][11]
            self.temp_hit_points = results[0][12]
            self.cur_hit_points = results[0][13]
            # print(f"Raw:    {self.rawAbilityArray} ")
            # print(f"Base:   {self.ability_base_array} ")
            # print(f"Racial: {ability_racial_mod_string}")
            # print(f"Str:    {self.ability_array_str} ")
            # print(f"Mod:    {self.ability_modifier_array}")
            for r in range(len(self.ability_base_array)):
                self.ability_array[r] = (
                    self.ability_base_array[r] +
                    self.raceObj.ability_bonuses[r])
            self.assignAbilityArray()

            self.classObj.melee_weapon = results[0][22]
            self.classObj.ranged_weapon = results[0][23]
            self.classObj.ranged_ammunition_type = results[0][24]
            self.classObj.ranged_ammunition_amt = results[0][25]
            self.classObj.armor = results[0][26]
            self.classObj.shield = results[0][27]

            tmp_rab_str = arrayToString(self.raceObj.ability_bonuses)

            if (ability_racial_mod_string != tmp_rab_str):
                tmpStr = (f"\n**WARNING: "
                          f"Racial Ability Array Mismatches: "
                          f"{ability_racial_mod_string} "
                          f"{tmp_rab_str}**\n")
                print(tmpStr)
            self.setArmorClass()

    def getAbilitySortArray(self):
        return self.classObj.ability_sort_array

    def getRacialAbilityBonusArray(self):
        return self.raceObj.ability_bonuses

    def getName(self):
        return self.raceObj.name

    def getAlignmentStr(self):
        return self.raceObj.alignment.get('alignment')

    def getAlignmentAbbrev(self):
        return self.raceObj.alignment.get('abbreviation')

    def getSkinTone(self):
        return self.raceObj.skinTone

    def getHairColor(self):
        return self.raceObj.hairColor

    def getHairType(self):
        return self.raceObj.hairType

    def getEyeColor(self):
        return self.raceObj.eyeColor

    def getHeight(self):
        return self.raceObj.height

    def getWeight(self):
        return self.raceObj.weight

    def getRace(self):
        return self.raceObj.race

    def getClass(self):
        return self.classObj.name

    def getHitDie(self):
        return self.classObj.hit_die

    def getRangedWeapon(self):
        return self.classObj.ranged_weapon

    def getMeleeWeapon(self):
        return self.classObj.melee_weapon

    def getRangedAmmunitionType(self):
        return self.classObj.ranged_ammunition_type

    def getRangedAmmunitionAmt(self):
        return self.classObj.ranged_ammunition_amt

    def getArmor(self):
        return self.classObj.armor

    def getShield(self):
        return self.classObj.shield

    def getBaseMovement(self):
        return self.raceObj.base_walking_speed

    def assignClass(self, classCandidate):
        self.lastMethodLog = (f'assignClass(db, '
                              f'{classCandidate})')

        if classCandidate == "Random":
            tmpClass = getRandomClassName(self.db)
        else:
            tmpClass = classCandidate
        obj = self.ClassSubclassSwitch(tmpClass)

        return obj

    def ClassSubclassSwitch(self, classCandidate):
        switcher = {
            'Barbarian': BarbarianPCClass(self.db),
            'Bard': BardPCClass(self.db),
            'Cleric': ClericPCClass(self.db),
            'Druid': DruidPCClass(self.db),
            'Fighter': FighterPCClass(self.db),
            'Monk': MonkPCClass(self.db),
            'Paladin': PaladinPCClass(self.db),
            'Ranger': RangerPCClass(self.db),
            'Rogue': RoguePCClass(self.db),
            'Sorcerer': SorcererPCClass(self.db),
            'Warlock': WarlockPCClass(self.db),
            'Wizard': WizardPCClass(self.db)
        }
        return switcher.get(classCandidate, "Unknown Class")

    def setFinesseAbility(self):
        s = self.getAbilityModifier('Strength')
        d = self.getAbilityModifier('Dexterity')
        if s > d:
            self.finesse_ability_mod = 'Strength'
        else:
            self.finesse_ability_mod = 'Dexterity'

    def setDamageAdjs(self, db):
        self.lastMethodLog = (f'setDamagedAdjs(db)')
        sql = (f"select rt.affected_name, rt.affect "
               f"from lu_racial_trait as rt "
               f"join lu_race as r on (rt.race = r.race "
               f"or rt.race = r.subrace_of)"
               f"where rt.category = 'Damage Received' "
               f"and rt.affect is not null "
               f"and rt.affected_name in ('Acid', 'Bludgeoning', "
               f"'Cold', 'Fire', 'Force', 'Ligtning', 'Necrotic',"
               f"'Piercing', 'Poison', 'Psychic', 'Radiant',"
               f"'Slashing', 'Thunder')"
               f"and (r.race = '{self.getRace()}' "
               f"or r.subrace_of = '{self.getRace()}')")

        rows = db.query(sql)
        for row in rows:
            self.damage_adj[row[0]] = row[1]

    def setProficiencyBonus(self):
        for a in range(len(self.featureObj)):
            if self.featureObj[a][2] == 'proficiency_bonus':
                self.proficiency_bonus = self.featureObj[a][4]

    def Damage(self, amount, damageType="Unknown"):
        self.lastMethodLog = (f'Damage({amount}, '
                              f'{damageType})')

        tmpType = self.damage_adj[damageType]

        if (tmpType and tmpType == 'resistant'):
            tmpStr = (f'Originally, {amount} points of {damageType} damage.\n')
            amount = (amount // 2)
            tmpStr = (f'Reduced to {amount} points due to '
                      f'{damageType} resistance.')
        elif (tmpType and tmpType == 'vulnerable'):
            tmpStr = (f'Originally, {amount} points of {damageType} damage.')
            amount = (amount * 2)
            tmpStr = (f'Increased to {amount} points due to '
                      f'{damageType} vulnerability.')
        else:
            tmpStr = (f'Suffers {amount} points of {damageType} damage.')

        if (amount >= self.cur_hit_points):
            tmpStr = (f'{tmpStr}\n{amount} exceeds current hit points'
                      f'({self.cur_hit_points}): knocked unconsious')
            self.stabilized = False
            # Instant Death?
            if ((amount - self.cur_hit_points) >= self.hit_points):
                tmpStr = (f'{tmpStr}\n{(amount - self.cur_hit_points)}'
                          f' exceeds hit points'
                          f'({self.hit_points}): Instant Death')
                self.death_save_failed_cnt = 3
                self.alive = False

            self.cur_hit_points = 0
        else:
            thp = self.cur_hit_points
            self.cur_hit_points -= amount
            tmpStr = (f'{tmpStr}\nResulting in ({thp} - {amount}) '
                      f'{self.cur_hit_points} points')

        self.damage_taken['Total'] += amount
        self.damage_taken[damageType] += amount

    def Heal(self, amount):
        self.lastMethodLog = (f'Heal({amount})')
        tmpStr = (f'Heals {amount} hit points.')
        if (self.cur_hit_points == 0 and self.alive):
            self.death_save_failed_cnt = 0
            self.death_save_passed_cnt = 0
            self.stabilized = True
            # tmpStr = (f'{tmpStr}\nResulting in {self.cur_hit_points} points')

        if ((self.cur_hit_points + amount) > self.hit_points):
            self.cur_hit_points = self.hit_points
            tmpStr = (f'{tmpStr}\nReturned to max {self.hit_points} points')
        else:
            thp = self.cur_hit_points
            self.cur_hit_points += amount
            tmpStr = (f'{tmpStr}\nResulting in ({thp} + {amount}) '
                      f'{self.cur_hit_points} points')

    def Revive(self):
        self.lastMethodLog = (f'Revive()')
        self.death_save_failed_cnt = 0
        self.death_save_passed_cnt = 0
        self.stabilized = True
        self.alive = True
        self.cur_hit_points = self.hit_points

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'Name:         {self.getName()}\n'
                  f'Id            {self.character_id}\n'
                  f'TTA:          {self.getTTA()}\n'
                  f'Gender:       {self.getGender()}\n'
                  f'Race:         {self.getRace()} ('
                  f'{self.raceObj.source_material})\n'
                  f'Movement:     {self.cur_movement}\n'
                  f'Class:        {self.getClass()} ('
                  f'{self.classObj.source_material})\n'
                  f'Armor Class:  {self.armor_class}\n'
                  f'Level:        {self.level}\n'
                  f'Hit Die:      {self.getHitDie()}\n')
        if self.cur_hit_points:
            outstr = (f'{outstr}'
                      f'Hit Points:   {self.cur_hit_points} / '
                      f'{self.hit_points}\n')
        if self.proficiency_bonus:
            outstr = (f'{outstr}'
                      f'Prof Bonus:   {self.proficiency_bonus}\n')

        outstr = (f'{outstr}'
                  f'Height:       {inchesToFeet(self.getHeight())}\n'
                  f'Weight:       {self.getWeight()} pounds\n'
                  f'Alignment:    {self.getAlignmentStr()}\n'
                  f'AlignAbbrev:  {self.getAlignmentAbbrev()}\n'
                  f'Skin Tone:    {self.getSkinTone()}\n')

        if (self.getHairColor()):
            outstr = (f'{outstr}Hair Color:   {self.getHairColor()}\n'
                      f'Hair Type:    {self.getHairType()}\n')

        outstr = (f'{outstr}Eye Color:    {self.getEyeColor()}\n'
                  f'Size:         {self.raceObj.size}\n')
        if self.raceObj.source_credit_url:
            outstr = (f'{outstr}Race URL:          '
                      f'{self.raceObj.source_credit_url}\n')
        if self.raceObj.source_credit_comment:
            outstr = (f'{outstr}Race Comment:      '
                      f'{self.raceObj.source_credit_comment}\n')

        if self.finesse_ability_mod is not None:
            outstr = (f'{outstr}\nFinesse Ability: '
                      f'{self.finesse_ability_mod}')
        if self.melee_weapon is not None:
            outstr = (f'{outstr}\nMelee Weapon:   '
                      f'{self.melee_weapon}')
        if self.ranged_weapon is not None:
            outstr = (f'{outstr}\nRanged Weapon:  '
                      f'{self.ranged_weapon}')
        if self.ranged_ammunition_amt is not None:
            outstr = (f'{outstr}\nRanged Ammo:   '
                      f'{self.ranged_ammunition_amt}')

        outstr = (f'{outstr}\n\nRaw Ability Array:  '
                  f'{self.getRawAbilityArray()}\n'
                  f'Ordered Array:      '
                  f'{self.getNumericallySortedAbilityArray()}\n'
                  f'Sort Array:    {self.getAbilityPrefStrArray()}\n'
                  f'Nbr Sort Array:     {self.ability_array_obj.getPrefArray()}\n'
                  f'Sorted:             {self.getSortedAbilityArray()}\n')

        outstr = (f'{outstr}\nAbility         Mod  Total = (Base + '
                  f'Racial + Level Improvements)\n')

        sorted_array = self.getSortedAbilityArray()
        ability_array = self.getAbilityArray()
        ability_imp_array = self.getAbilityImprovementArray()
        labelArray = self.ability_array_obj.ability_label_array
        for c in range(len(labelArray)):
            outstr = (f'{outstr}\n{labelArray[c].ljust(16)}'
                      f'{str(self.ability_modifier_array[c]).rjust(3)}   '
                      f'{str(ability_array[c]).rjust(2)}   = ('
                      f'{str(sorted_array[c]).rjust(2)}  +   '
                      f'{str(self.raceObj.ability_bonuses[c]).rjust(2)}'
                      f'   +   {str(ability_imp_array[c]).rjust(2)})\n')

        if self.raceObj.languages:
            outstr = (f'{outstr}\n\nLanguages:')
            for l in self.raceObj.languages:
                outstr = (f'{outstr}\n   {l}')

        if self.raceObj.traitContainer.proficient:
            outstr = (f'{outstr}\n\nProficiencies:')

            tmpVar = (self.raceObj.traitContainer.proficient)
            for p in range(len(tmpVar)):
                tmpprofstr = tmpVar[p].ljust(23)
                tmpsrcstr = self.raceObj.traitContainer.proficient_source[p]
                outstr = (f'{outstr}\n   {tmpprofstr}'
                          f' ({tmpsrcstr})')

        for b in self.raceObj.traitContainer.traits:
                if b.category != "Proficiency Skill":
                    outstr = (f'{outstr}\n{b}')

        if self.featureObj:
            outstr = (f'{outstr}\n\nClass Features:\n')
            for b in range(len(self.featureObj)):
                for c in range(len(self.featureObj[b])):
                    if self.featureObj[b][c] is not None:
                        outstr = (f'{outstr} {self.featureObj[b][c]}')
                outstr = (f'{outstr}\n')
        outstr = (f'{outstr}\nDamage ADJ:')

        for key, value in sorted(self.damage_adj.items()):
            if len(value) > 2:
                outstr = (f'{outstr}\n{key}: {value}')

        # outstr = (f'{outstr}\n\nJournal Output:\n{self.debugStr}\n\n')

        outstr = (f'\n{outstr}\n')
        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = PlayerCharacter(db, level=10)
    print(a1)
    for key, value in a1.ability_array_obj.getClassEval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")

    a2 = PlayerCharacter(db=db, abilityArrayStr='10,11,12,13,14,15')
    a2.ability_array_obj.setPreferenceArray(prefArray=stringToArray(
                                            '5,0,2,1,4,3'
                                            ))
    print(a2)
    for key, value in a2.ability_array_obj.getClassEval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    # a3 = PlayerCharacter(db, characterId=10)
    # print(a3)
    # a4 = PlayerCharacter(db, characterId=138)
    # print(a4)
