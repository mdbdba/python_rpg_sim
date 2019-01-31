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
from Character import Character
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

    def getRace(self):
        return self.raceObj.race


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = PlayerCharacter(db)
    print(a1.rawAbilityArray)
    print(a1.getGender())
    print(a1.getRace())
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
