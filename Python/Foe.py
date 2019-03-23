from InvokePSQL import InvokePSQL
from Character import Character
from Die import Die

from CommonFunctions import stringToArray


class Foe(Character):
    def __init__(self,
                 db,
                 foeCandidate="Random",
                 challengeLevel=".25",
                 damageGenerator="Random",
                 hitpointGenerator="Max",
                 debugInd=0):
        genderCandidate = 'U'
        abilityArrayStr = 'Common'
        level = 1   # Player level will always be 1 for Foes
        Character.__init__(self, db, genderCandidate, abilityArrayStr,
                           damageGenerator, hitpointGenerator,
                           level, debugInd)
        self.getFoe(db, foeCandidate)

    def getFoe(self, db, foeCandidate):
        sql = (f"SELECT id, name, foe_type, size, base_walking_speed, "
               f"challenge_level, ability_string, ability_modifier_string, "
               f"hit_point_die, hit_point_modifier, hit_point_adjustment, "
               f"standard_hit_points, alignment, ranged_weapon, melee_weapon, "
               f"ranged_ammunition_type, ranged_ammunition_amt, armor, "
               f"shield, source_material, source_credit_url, "
               f"source_credit_comment FROM dnd_5e.foe "
               f"where name='{foeCandidate}'")

        results = db.query(sql)
        # results[0][0]     # id,
        self.name = results[0][1]     # name,
        self.foe_type = results[0][2]     # foe_type,
        self.size = results[0][3]     # size,
        self.base_walking_speed = results[0][4]     # base_walking_speed,
        self.challenge_level = results[0][5]     # challenge_level,
        self.ability_array_str = results[0][6]     # ability_string,
        # ability_modifier_string,
        self.ability_modifier_array = stringToArray(results[0][7])
        self.hit_point_die = results[0][8]     # hit_point_die,
        self.hit_point_modifier = results[0][9]     # hit_point_modifier,
        self.hit_point_adjustment = results[0][10]     # hit_point_adjustment,
        self.standard_hit_points = results[0][11]     # standard_hit_points,
        self.alignment = results[0][12]     # alignment,
        self.ranged_weapon = results[0][13]     # ranged_weapon,
        self.melee_weapon = results[0][14]     # melee_weapon,
        self.ranged_ammunition_type = results[0][15]
        self.ranged_ammunition_amt = results[0][16]
        self.armor = results[0][17]     # armor,
        self.shield = results[0][18]     # shield,
        self.source_material = results[0][19]     # source_material,
        self.source_credit_url = results[0][20]     # source_credit_url,
        self.source_credit_comment = results[0][21]     # source_credit_comment

        self.assignAbilityArray()
        self.setArmorClass()
        self.hit_points = self.assignHitPoints()
        self.cur_hit_points = self.hit_points
        self.temp_hit_points = 0

    def assignHitPoints(self):
        self.lastMethodLog = (f'assignHitPoints( '
                              f'{self.hit_point_die}, '
                              f'{self.hit_point_modifier}, '
                              f'{self.hit_point_adjustment})')
        if (self.hit_point_generator == 'Max'):
            retVal = ((self.hit_point_modifier * self.hit_point_die)
                      + (self.hit_point_adjustment))
        elif (self.hit_point_generator == 'Standard'):
            retVal = self.standard_hit_points
        else:
            d = Die(self.hit_point_die)
            retVal = ((d.roll(self.hit_point_modifier))
                      + (self.hit_point_adjustment))

        if self.debugInd:
            self.classEval[-1]["hitPoints"] = retVal

        return retVal

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'gender: {self.gender}\n'
                  f'name: {self.name}\n'
                  f'foe_type: {self.foe_type}\n'
                  f'size: {self.size}\n'
                  f'alignment: {self.alignment }\n'
                  f'base_walking_speed: {self.base_walking_speed }\n'
                  f'challenge_level: {self.challenge_level }\n'
                  f'ability_array_str: {self.ability_array_str }\n'
                  f'abilityArrayStr: {self.getAbilityArray()}\n'
                  f'ability_modifier_array: {self.ability_modifier_array }\n'
                  f'hit_point_die: {self.hit_point_die }\n'
                  f'hit_point_modifier: {self.hit_point_modifier }\n'
                  f'hit_point_adjustment: {self.hit_point_adjustment}\n'
                  f'standard_hit_points: {self.standard_hit_points}\n'
                  f'armor_class: {self.armor_class}\n'
                  f'hit_points: {self.hit_points}\n'
                  f'cur_hit_points: {self.cur_hit_points}\n'
                  f'temp_hit_points: {self.temp_hit_points}\n'
                  f'ranged_weapon: {self.ranged_weapon }\n'
                  f'melee_weapon: {self.melee_weapon }\n'
                  f'ranged_ammunition_type: {self.ranged_ammunition_type }\n'
                  f'ranged_ammunition_amt: {self.ranged_ammunition_amt }\n'
                  f'armor: {self.armor }\n'
                  f'shield: {self.shield }\n'
                  f'source_material: {self.source_material }\n'
                  f'source_credit_url: {self.source_credit_url}\n'
                  f'source_credit_comment: {self.source_credit_comment}\n')

        outstr = (f'\n{outstr}\n')
        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = Foe(db, foeCandidate="Skeleton")
    print(a1)
