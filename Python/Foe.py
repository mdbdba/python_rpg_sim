from InvokePSQL import InvokePSQL
from Character import Character
from Weapon import Weapon
from Die import Die

from CommonFunctions import string_to_array


class Foe(Character):
    def __init__(self,
                 db,
                 foe_name=None,
                 foe_candidate="Random",
                 challenge_level=".25",
                 damage_generator="Random",
                 hit_point_generator="Max",
                 debug_ind=0):
        gender_candidate = 'U'
        self.name = foe_name
        ability_array_str = 'Common'
        if foe_candidate == "Random":
            foe_candidate = self.find_random(db, challenge_level)
        level = 1   # Player level will always be 1 for Foes
        Character.__init__(self, db, gender_candidate, ability_array_str,
                           damage_generator, hit_point_generator,
                           level, debug_ind)
        self.get_foe(db, foe_candidate)

        if self.melee_weapon is not None:
            self.melee_weapon_obj = Weapon(db, self.get_melee_weapon())
            self.melee_weapon_obj.setWeaponProficient()
        if self.ranged_weapon is not None:
            self.ranged_weapon_obj = Weapon(db, self.get_ranged_weapon())

        self.class_eval.append({
                       "pythonClass": "Foe",
                       "foe_candidate": foe_candidate,
                       "challenge_level": challenge_level,
                       "damage_generator": damage_generator,
                       "hit_point_generator": hit_point_generator,
                       "level": level,
                       "debug_ind": debug_ind})

        if self.debug_ind == 1:
            for i in self.__str__().splitlines():
                self.logger.debug(f"{self.get_name()}: {i}")

    def get_melee_weapon(self):
        return self.melee_weapon

    def get_ranged_weapon(self):
        return self.ranged_weapon

    def default_melee_attack(self, vantage='Normal'):
        return self.melee_attack(self.melee_weapon_obj, vantage)

    def find_random(self, db, challenge_level):
        sql = (f"SELECT name FROM dnd_5e.foe "
               f"where challenge_level='{challenge_level}' "
               f"ORDER BY RANDOM() LIMIT 1")
        results = db.query(sql)
        try:
            retstr = results[0][0]
        except IndexError:
            raise ValueError(f'Could not find foe for challenge level: {challenge_level}')
        return retstr

    def get_foe(self, db, foe_candidate):
        sql = (f"SELECT id, name, foe_type, size, base_walking_speed, "
               f"challenge_level, ability_string, ability_modifier_string, "
               f"hit_point_die, hit_point_modifier, hit_point_adjustment, "
               f"standard_hit_points, alignment, ranged_weapon, melee_weapon, "
               f"ranged_ammunition_type, ranged_ammunition_amt, armor, "
               f"shield, source_material, source_credit_url, "
               f"source_credit_comment FROM dnd_5e.foe "
               f"where name='{foe_candidate}'")

        results = db.query(sql)
        try:
            # results[0][0]     # id,
            if self.name is None:
                self.name = results[0][1]     # name,
            # if name is used for something specific (skeleton_1, or jimmyjam,
            # this will tell us what creature it is.
            # Otherwise, these two will match.
            self.race = results[0][1]
            self.foe_type = results[0][2]     # foe_type,
            self.size = results[0][3]     # size,
            self.base_walking_speed = results[0][4]     # base_walking_speed,
            self.cur_movement = results[0][4]
            self.challenge_level = results[0][5]     # challenge_level,
            self.ability_array_str = results[0][6]     # ability_string,
            # ability_modifier_string,
            self.ability_modifier_array = string_to_array(results[0][7])
            self.hit_point_die = results[0][8]     # hit_point_die,
            self.hit_point_modifier = results[0][9]     # hit_point_modifier,
            self.hit_point_adjustment = results[0][10]
            self.standard_hit_points = results[0][11]
            self.alignment = results[0][12]     # alignment,
            self.ranged_weapon = results[0][13]     # ranged_weapon,
            self.melee_weapon = results[0][14]     # melee_weapon,
            self.ranged_ammunition_type = results[0][15]
            self.ranged_ammunition_amt = results[0][16]
            self.armor = results[0][17]     # armor,
            self.shield = results[0][18]     # shield,
            self.source_material = results[0][19]     # source_material,
            self.source_credit_url = results[0][20]     # source_credit_url,
            self.source_credit_comment = results[0][21]
            self.assign_ability_array()
            self.set_armor_class()
            self.hit_points = self.assign_hit_points()
            self.cur_hit_points = self.hit_points
            self.temp_hit_points = 0
        except IndexError:
            raise ValueError(f'Could not find foe: {foe_candidate}')

    def assign_hit_points(self):
        self.lastMethodLog = (f'assign_hit_points( '
                              f'{self.hit_point_die}, '
                              f'{self.hit_point_modifier}, '
                              f'{self.hit_point_adjustment})')
        if not self.hit_point_adjustment:
            self.hit_point_adjustment = 0

        if self.hit_point_generator == 'Max':
            ret_val = ((self.hit_point_modifier * self.hit_point_die)
                       + self.hit_point_adjustment)
        elif self.hit_point_generator == 'Standard':
            ret_val = self.standard_hit_points
        else:
            d = Die(self.hit_point_die)
            ret_val = (d.roll(self.hit_point_modifier)
                       + self.hit_point_adjustment)

        if self.debug_ind:
            self.class_eval[-1]["hitPoints"] = ret_val

        return ret_val

    def get_racial_traits(self):
        return None

    def get_name(self):
        return self.name

    def get_race(self):
        return self.race

    def get_alignment_str(self):
        return self.alignment

    def get_alignment_abbrev(self):
        sql = (f"select abbreviation from lu_alignment where value = "
               f"'{self.alignment}';")
        results = self.db.query(sql)

        return results[0][0]

    def is_not_using_shield(self):
        if self.shield == 'None':
            ret_val = True
        else:
            ret_val = False
        return ret_val

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'gender: {self.gender}\n'
                  f'name: {self.get_name()}\n'
                  f'race: {self.get_race()}\n'
                  f'foe_type: {self.foe_type}\n'
                  f'size: {self.size}\n'
                  f'alignment: {self.get_alignment_str() }\n'
                  f'alignment abbrev: {self.get_alignment_abbrev() }\n'
                  f'base_walking_speed: {self.base_walking_speed }\n'
                  f'challenge_level: {self.challenge_level }\n'
                  f'ability_array_str: {self.ability_array_str }\n'
                  f'abilityArrayStr: {self.get_ability_array()}\n'
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

        outstr = f'\n{outstr}\n'
        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = Foe(db, foe_candidate="Skeleton", debug_ind=1)
    print(a1)
    a1.melee_defend(modifier=13, possible_damage=a1.hit_points,
                    damage_type='Bludgeoning')
    a1.heal(10)
    a1.melee_defend(modifier=13, possible_damage=(2 * a1.hit_points),
                    damage_type='Bludgeoning')
