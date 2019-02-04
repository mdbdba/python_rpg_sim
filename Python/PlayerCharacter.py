from InvokePSQL import InvokePSQL
from Character import Character
from CommonFunctions import arrayToString
from CommonFunctions import stringToArray
from AbilityArray import AbilityArray
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
from Attack import Attack
from Die import Die

import random
import datetime


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
            self.assignAbilityArray()
            self.raceObj = self.assignRace(raceCandidate)
            self.classObj = self.assignClass(classCandidate)
            self.raceObj.setRandoms(db=self.db, gender=self.gender)

            self.setArmorClass()

    def assignRace(self, raceCandidate):
        self.lastMethodLog = (f'assignRace('
                              f'{raceCandidate})')
        if (raceCandidate == "Random"):
            randObj = CharacterRace(self.db, raceCandidate)
            raceToUse = randObj.race
        else:
            raceToUse = raceCandidate

        return CharacterRace(self.db, raceToUse)

    def getName(self):
        return self.raceObj.name

    def getAlignment(self):
        return self.raceObj.alignment

    def getSkinTone(self):
        return self.raceObj.skinTone

    def getHairColor(self):
        return self.raceObj.hairColor

    def getHairType(self):
        return self.raceObj.hairType

    def getEyeColor(self):
        return self.raceObj.eyeColor

    def getClass(self):
        return self.classObj.name

    def getRace(self):
        return self.raceObj.race

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

        print(f"Setting up {tmpClass}")
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


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = PlayerCharacter(db)
    print(a1.rawAbilityArray)
    print(a1.getGender())
    print(a1.getRace())
    print(a1.getClass())
    print(a1.getTTA())
    print(a1.getName())
    print(a1.getAlignment().get('abbreviation'))
    print(a1.getSkinTone())
    print(a1.getHairColor())
    print(a1.getHairType())
    print(a1.getEyeColor())
    a2 = PlayerCharacter(db=db, abilityArrayStr='10,11,12,13,14,15')
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
    print(a2.getRace())
    print(a2.getClass())
    print(a2.getTTA())

    print(a2.getName())
    print(a2.getAlignment().get('abbreviation'))
    print(a2.getSkinTone())
    print(a2.getHairColor())
    print(a2.getHairType())
    print(a2.getEyeColor())
