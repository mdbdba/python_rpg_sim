from InvokePSQL import InvokePSQL
from Character import Character
# from CommonFunctions import arrayToString
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
            # self.saveCharacter(db)
        self.characterId = characterId

        self.setFinesseAbility()
        self.setArmorClass()
        self.featureObj = self.classObj.getClassLevelFeature(self.level, db)

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
        sortArray = self.getAbilitySortArray()
        for r in range(len(sortArray)):
            t = sortArray[r]
            self.ability_base_array[t] = self.rawAbilityArray[r]

        bonusArray = self.getRacialAbilityBonusArray()
        for r in range(len(self.ability_base_array)):
            self.ability_array[r] = (
                self.ability_base_array[r] + bonusArray[r])

            sql = (f"select modifier from dnd_5e.lu_ability_score_modifier "
                   f"where value = '{self.ability_array[r]}';")

            result = db.query(sql)
            self.ability_modifier_array[r] = int(result[0][0])

        self.hit_points = self.assignHitPoints(self.level,
                                               self.getHitDie(),
                                               self.ability_modifier_array[2])
        self.cur_hit_points = self.hit_points
        self.temp_hit_points = 0

        if (self.classObj.melee_weapon is not None):
            self.melee_weapon_obj = Weapon(db, self.getMeleeWeapon())
            self.melee_weapon_obj.setWeaponProficient()
        if (self.classObj.ranged_weapon is not None):
            self.ranged_weapon_obj = Weapon(db, self.getRangedWeapon())

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

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'Name:         {self.getName()}\n'
                  f'Id            {self.characterId}\n'
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

        outstr = (f'{outstr}\n\nAbility Array:  {self.rawAbilityArray}\n'
                  f'Sort Array:    {self.classObj.ability_sort_str_array}\n')

        outstr = (f'{outstr}\nAbility         Mod  Total  (Base + '
                  f'Racial + Bonus + Temp)\n')

        labelArray = self.ability_array_obj.ability_label_array
        for c in range(len(labelArray)):
            outstr = (f'{outstr}\n{labelArray[c].ljust(16)}'
                      f'{str(self.ability_modifier_array[c]).rjust(3)}   '
                      f'{str(self.ability_array[c]).rjust(2)}     ('
                      f'{str(self.ability_base_array[c]).rjust(2)}  +   '
                      f'{str(self.raceObj.ability_bonuses[c]).rjust(2)}'
                      f'   +   0   +   0)\n')

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
    a1 = PlayerCharacter(db)
    # print(a1.rawAbilityArray)
    # print(a1.getGender())
    # print(a1.getRace())
    # print(a1.getClass())
    # print(a1.getTTA())
    # print(a1.getName())
    # print(a1.getAlignmentStr())
    # print(a1.getAlignmentAbbrev())
    # print(a1.getSkinTone())
    # print(a1.getHairColor())
    # print(a1.getHairType())
    # print(a1.getEyeColor())
    # print(a1.getHeight())
    # print(a1.getWeight())
    print(a1)
    a2 = PlayerCharacter(db=db, abilityArrayStr='10,11,12,13,14,15')
    # print(a2.getRawAbilityArray())
    # print(a2.getAbilityPrefArray())
    # print(a2.getSortedAbilityArray())
    a2.ability_array_obj.setPreferenceArray(prefArray=stringToArray(
                                            '5,0,2,1,4,3'
                                            ))
    # print(a2.getRawAbilityArray())
    # print(a2.getAbilityPrefArray())
    # print(a2.getSortedAbilityArray())
    # print(a2.armor_class)
    # print(a2.getGender())
    # print(a2.getRace())
    # print(a2.getClass())
    # print(a2.getTTA())

    # print(a2.getName())
    # print(a2.getAlignmentStr())
    # print(a2.getAlignmentAbbrev())
    # print(a2.getSkinTone())
    # print(a2.getHairColor())
    # print(a2.getHairType())
    # print(a2.getEyeColor())
    # print(a2.getHeight())
    # print(a2.getWeight())
    print(a2)
