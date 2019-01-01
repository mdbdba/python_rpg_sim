from InvokePSQL import InvokePSQL
from CommonFunctions import arrayToString, stringToArray
from AbilityArray import AbilityArray
from Die import Die

import random
import datetime


class Character(object):
    def __init__(self,
                 db,
                 genderCandidate="Random",
                 abilityArrayStr="Common",
                 level=1,
                 debugInd=0):

        self.db = db

        self.ability_base_array = [6, 6, 6, 6, 6, 6]
        self.ability_array = [6, 6, 6, 6, 6, 6]
        self.ability_modifier_array = [0, 0, 0, 0, 0, 0]
        self.abilityLabelArray = ['Strength', 'Dexterity', 'Constitution',
                                  'Intelligence', 'Wisdom', 'Charisma']
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

        self.assignAbilityArray(abilityArrayStr)

    def assignAbilityArray(self, abilityArrayStr):
        self.lastMethodLog = (f'assignAbilityArray('
                              f'{abilityArrayStr})')
        # if the string doesn't begin and end with a number, then it must
        # be a type that the ability array wants
        if (abilityArrayStr[1].isdigit() and abilityArrayStr[-1].isdigit()):
            self.rawAbilityArray = stringToArray(abilityArrayStr)
        else:
            a1 = AbilityArray(abilityArrayStr)
            self.rawAbilityArray = a1.getArray()







