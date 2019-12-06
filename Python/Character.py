from InvokePSQL import InvokePSQL
from CommonFunctions import string_to_array
from AbilityArray import AbilityArray
from Attack import Attack
from Die import Die


import random
import logging


class Character(object):
    def __init__(self,
                 db,
                 gender_candidate="Random",
                 ability_array_str="Common",
                 damage_generator="Random",
                 hit_point_generator="Max",
                 level=1,
                 debug_ind=0):

        self.db = db
        level = int(level)
        if level < 1 or level > 20:
            raise ValueError('Level should be between 1 and 20.')
        else:
            self.level = level

        self.damage_generator = damage_generator
        self.hit_point_generator = hit_point_generator
        self.debug_ind = debug_ind
        self.debugStr = ''

        if ((self.debug_ind == 1) and
           ((getattr(self, "logger", None)) is None)):
            log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
            logging.basicConfig(format=log_fmt, level=logging.DEBUG)
            self.logger = logging.getLogger(__name__)

        y = getattr(self, "class_eval", None)
        if y is None:
            self.class_eval = []
        self.class_eval.append({
                       "pythonClass": "Character",
                       "gender_candidate": gender_candidate,
                       "ability_array_str": ability_array_str,
                       "level": level,
                       "debug_ind": debug_ind})
        self.ability_array_str = ability_array_str
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
        self.tta = self.set_taliesin_temperament_archetype()
        self.combat_preference = 'Melee'  # 'Melee' or Ranged'
        self.proficiency_bonus = 0

        self.last_method_log = ''
        if gender_candidate == "Random":
            self.gender = self.assign_gender()
        else:
            self.gender = gender_candidate

        self.blinded_ind = False
        self.charmed_ind = False
        self.deafened_ind = False
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
        self.unconscious_ind = False
        self.ranged_weapon = None
        self.melee_weapon = None
        self.ranged_ammunition_type = None
        self.ranged_ammunition_amt = None
        self.armor = None
        self.shield = None
        self.finesse_ability_mod = self.set_finesse_ability()


        self.exhaustion_level = 0
        # 1   Disadvantage on Ability Checks
        # 2   Speed halved
        # 3   Disadvantage on Attack rolls and Saving Throws
        # 4   Hit point maximum halved
        # 5   Speed reduced to 0
        # 6   Death

        self.attack_rolls = []
        self.attack_roll_count = 0
        self.attack_roll_nat20_count = 0
        self.attack_roll_nat1_count = 0
        self.attack_success_count = 0

    def get_name(self):
        return "Generic Character"

    def get_damage_taken(self):
        return self.damage_taken

    def get_damage_dealt(self):
        return self.damage_dealt

    def assign_gender(self):
        self.last_method_log = f"assign_gender(db)"
        d = Die(100)
        a = d.roll()
        if a <= 40:
            result = "M"
        elif 40 < a <= 90:
            result = "F"
        else:
            result = "U"

        if self.debug_ind == 1:
            self.class_eval[-1]["Gender"] = result

        return result

    def get_gender(self):
        return self.gender

    def assign_ability_array(self, sort_array=None):
        self.last_method_log = (f'assign_ability_array('
                                f'{self.ability_array_str})')
        # if the string doesn't begin and end with a number, then it must
        # be a type that the ability array wants
        tmp = self.ability_array_str
        if tmp[0].isdigit() and tmp[-1].isdigit():
            tmp_array = string_to_array(tmp)
            self.ability_array_obj = AbilityArray(array_type="Predefined",
                                                  raw_array=tmp_array,
                                                  pref_array=sort_array,
                                                  debug_ind=self.debug_ind)
        else:
            self.ability_array_obj = AbilityArray(array_type=tmp,
                                                  pref_array=sort_array,
                                                  debug_ind=self.debug_ind)

    def get_class_eval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.class_eval

    def get_raw_ability_array(self):
        return self.ability_array_obj.get_raw_array()

    def get_ability_pref_array(self):
        return self.ability_array_obj.get_pref_array()

    def get_numerically_sorted_ability_array(self):
        return self.ability_array_obj.get_numerical_sorted_array()

    def get_ability_pref_str_array(self):
        return self.ability_array_obj.get_pref_str_array()

    def get_sorted_ability_array(self):
        return self.ability_array_obj.get_sorted_array()

    def get_ability_array(self):
        return self.ability_array_obj.get_array()

    def get_ability_improvement_array(self):
        return self.ability_array_obj.get_imp_array()

    def set_taliesin_temperament_archetype(self):
        self.last_method_log = f'assignTaliesinTemperamentArchetype()'
        align_array = ['Bashful', 'Doc', 'Grumpy', 'Happy', 'Sneezy', 'Sleepy', 'Dopey']
        align_type = align_array[(random.randint(0, 6))]
        per_array = ['High', 'Mid', 'Low']
        per_type = per_array[(random.randint(0, 2))]

        ret_str = f"{align_type}/{per_type}"
        if self.debug_ind:
            self.class_eval[-1]["tta"] = ret_str

        return ret_str

    def get_tta(self):
        return self.tta

    def get_base_movement(self):
        return 15

    def zero_movement(self):
        self.last_method_log = f'zero_movement()'
        self.cur_movement = 0
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: zero movement to "
                   f"{self.cur_movement}")
            self.logger.debug(msg)

    def half_movement(self):
        self.last_method_log = f'half_movement()'
        self.cur_movement = self.cur_movement // 2
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: half movement to "
                   f"{self.cur_movement}")
            self.logger.debug(msg)

    def double_movement(self):
        self.last_method_log = f'double_movement()'
        self.cur_movement = self.get_base_movement() * 2
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: double movement to "
                   f"{self.cur_movement}")
            self.logger.debug(msg)

    def reset_movement(self):
        self.last_method_log = f'reset_movement()'
        self.cur_movement = self.get_base_movement()
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: reset movement to "
                   f"{self.cur_movement}")
            self.logger.debug(msg)

    def change_exhaustion_level(self, amount):
        self.last_method_log = f'change_exhaustion_level({amount})'
        orig_level = self.exhaustion_level
        self.exhaustion_level += amount

        # 1   Disadvantage on Ability Checks
        # 2   Speed halved
        # 3   Disadvantage on Attack rolls and Saving Throws
        # 4   Hit point maximum halved
        # 5   Speed reduced to 0
        # 6   Death

        if self.exhaustion_level >= 2:
            self.half_movement()
        elif (orig_level > self.exhaustion_level
              and self.exhaustion_level < 2):  # recovery
            self.reset_movement()

        if self.exhaustion_level >= 5:
            self.zero_movement()
        elif (orig_level > self.exhaustion_level
              and self.exhaustion_level < 5):  # recovery
            self.half_movement()

        if self.exhaustion_level >= 6:
            self.alive = False

        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: exhaustion level change to "
                   f"{self.exhaustion_level}")
            self.logger.debug(msg)

    def get_ability_modifier(self, ability):
        self.last_method_log = f'get_ability_modifier({ability})'
        res = 0
        if ability == 'Strength':
            res = self.ability_modifier_array[0]
        if ability == 'Dexterity':
            res = self.ability_modifier_array[1]
        if ability == 'Constitution':
            res = self.ability_modifier_array[2]
        if ability == 'Intelligence':
            res = self.ability_modifier_array[3]
        if ability == 'Wisdom':
            res = self.ability_modifier_array[4]
        if ability == 'Charisma':
            res = self.ability_modifier_array[5]

        return res

    def assign_hit_points(self, level, hit_die, modifier):
        self.last_method_log = (f'assign_hit_points( ' 
                                f'{level}, ' 
                                f'{hit_die}, ' 
                                f'{modifier})')
        if self.hit_point_generator == 'Max':
            ret_str = ((level * hit_die) + (level * modifier))
        else:
            d = Die(hit_die)
            ret_str = ((d.roll(level)) + (level * modifier))

        if self.debug_ind:
            self.class_eval[-1]["hitPoints"] = ret_str

        return ret_str

    def set_armor_class(self):
        self.last_method_log = f'set_armor_class()'
        dex_mod = -99
        base_ac = 10
        if self.armor is not None and self.armor != 'None':
            sql = (f"select ac_base from dnd_5e.lu_armor "
                   f"where name = '{self.armor}';")

            res = self.db.query(sql)
            base_ac = res[0][0]

            sql = (f"select ac_use_dex_mod, ac_dex_mod_max "
                   f"from dnd_5e.lu_armor "
                   f"where name = '{self.armor}';")

            res = self.db.query(sql)
            if res[0][0] is False:
                dex_mod = 0
            elif res[0][1] != -1:
                dex_mod = res[0][1]
            else:
                dex_mod = -99

        if dex_mod == -99:
            dex_mod = self.get_ability_modifier('Dexterity')

        if self.shield is not None and self.shield != 'None':
            sql = (f"select ac_base from dnd_5e.lu_armor "
                   f"where name = '{self.shield}';")

            res = self.db.query(sql)
            shield_bonus = res[0][0]
        else:
            shield_bonus = 0

        self.armor_class = base_ac + shield_bonus + dex_mod

        if self.debug_ind:
            self.class_eval[-1]["armorClass"] = self.armor_class

        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: armorClass set to "
                   f"{self.armor_class}")
            self.logger.debug(msg)

    def contest_check(self, ability, vantage='Normal'):
        self.last_method_log = f'contest_check({ability}, {vantage})'
        d = Die(20)
        if vantage == 'Normal':
            r = d.roll()
        elif vantage == 'Advantage':
            r = d.rollWithAdvantage()
        else:
            r = d.rollWithDisadvantage()

        mod = self.get_ability_modifier(ability)

        ret_val = r + mod

        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: contest_check "
                   f"{ability} with {vantage} vantage returned {ret_val}")
            self.logger.debug(msg)

        return ret_val

    def roll_for_initiative(self, vantage='Normal'):
        ret_val = self.contest_check('Dexterity', vantage)
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: roll_for_initiative "
                   f"with {vantage} vantage returned {ret_val}")
            self.logger.debug(msg)
        return ret_val

    def check_proficiency_skill(self, ability):
        self.last_method_log = f'check_proficiency_skill({ability})'
        ret_val = False
        t = self.get_racial_traits()
        if t:
            for b in t:
                if b.category == "Proficiency Skill":
                    if b.affected_name == ability:
                        ret_val = True
        if self.debug_ind == 1:
            msg = (f"{self.get_name()}: Proficiency for "
                   f"with {ability} returned {ret_val}")
            self.logger.debug(msg)

        return ret_val

    def incr_death_save_failed_cnt(self, amount: int = 1):
        self.death_save_failed_cnt += amount
        if self.death_save_failed_cnt >= 3:
            self.alive = False
            if self.debug_ind == 1:
                self.logger.debug(f'{self.get_name()}: Three failed death saves. '
                                  f'Character has died.')

    def stabilize(self):
        if self.cur_hit_points < 1:
            self.cur_hit_points = 1
        self.death_save_passed_cnt = 0
        self.death_save_failed_cnt = 0
        self.stabilized = True
        self.alive = True
        self.unconscious_ind = False
        if self.debug_ind == 1:
            self.logger.debug(f'{self.get_name()}: Has stabilized.')

    def death_save(self, vantage='Normal'):
        self.last_method_log = f'death_save({vantage})'
        tmp_str = 'Performs death save.'
        res = self.contest_check('Death', vantage)
        if res == 20:  # character is stablized
            self.stabilize()
            tmp_str = f'{tmp_str}\nResult: Nat 20. Character Stabilized'
        elif res >= 10:  # normal pass
            self.death_save_passed_cnt += 1
            tmp_str = (f'{tmp_str}\nPassed. Current counts: (P/F) ' 
                       f'{self.death_save_passed_cnt}/' 
                       f'{self.death_save_failed_cnt}')
        elif res == 1:   # crit fail
            self.incr_death_save_failed_cnt(2)
            tmp_str = (f'{tmp_str}\nCrit fail. Current counts: (P/F) ' 
                       f'{self.death_save_passed_cnt}/' 
                       f'{self.death_save_failed_cnt}')
        else:   # res < 10 -- normal fail
            self.incr_death_save_failed_cnt(1)
            tmp_str = (f'{tmp_str}\nFailed. Current counts: (P/F) ' 
                       f'{self.death_save_passed_cnt}/' 
                       f'{self.death_save_failed_cnt}')

        if self.death_save_passed_cnt >= 3:
            self.stabilize()
            tmp_str = (f'{tmp_str}\nThree passed death saves. ' 
                       f'Character Stabilized')
        # elif self.death_save_failed_cnt >= 3:
        #      self.alive = False
        #     tmp_str = (f'{tmp_str}\nThree failed death saves. '
        #                f'Character has died.')

        if self.debug_ind == 1:
            msg = f"{self.get_name()}: {tmp_str}"
            self.logger.debug(msg)

    def check(self, skill, vantage='Normal', dc=10):
        self.last_method_log = f'check({skill}, {vantage}, {dc})'
        tmp_str = ''
        # Saving throw
        if (skill == 'Strength' or skill == 'Dexterity'
                or skill == 'Constitution' or skill == 'Intelligence'
                or skill == 'Wisdom' or skill == 'Charisma'):
            ability = skill
            # at exhaustion level 3 saving throws are affected
            if self.exhaustion_level >= 3:
                if vantage == 'Advantage':
                    vantage = 'Normal'
                else:
                    vantage = 'Disadvantage'
            adjusted_roll = self.contest_check(ability, vantage)
        else:
            # Skill check
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
            if self.debug_ind:
                tmp_str = f'{tmp_str}{skill} '
            # at exhaustion level 1 skills checks are affected
            if self.exhaustion_level >= 1:
                if vantage == 'Advantage':
                    vantage = 'Normal'
                else:
                    vantage = 'Disadvantage'
            adjusted_roll = self.contest_check(ability, vantage)

            if self.check_proficiency_skill(skill):
                adjusted_roll = adjusted_roll + int(self.proficiency_bonus)
                tmp_str = f'{tmp_str} + Prof({self.proficiency_bonus}) '

        if adjusted_roll >= dc:
            res = True
        else:
            res = False

        if self.debug_ind == 1:
            tmp_str = f'{tmp_str}{adjusted_roll} >= {dc} '
            if res:
                tmp_str = f'{tmp_str} (true)\n'
            else:
                tmp_str = f'{tmp_str} (false)\n'

            msg = f"{self.get_name()}: {tmp_str}"
            self.logger.debug(msg)

        return res

    def get_damage_generator(self):
        return self.damage_generator

    def damage(self, amount, damage_type="Unknown"):
        self.last_method_log = f'damage({amount}, {damage_type})'

        tmp_type = self.damage_adj[damage_type]

        if tmp_type and tmp_type == 'resistant':
            tmp_str = f'Originally, {amount} points of {damage_type} damage.\n'
            amount = amount // 2
            tmp_str = f'Reduced to {amount} points due to {damage_type} resistance.'
        elif tmp_type and tmp_type == 'vulnerable':
            tmp_str = f'Originally, {amount} points of {damage_type} damage.'
            amount = amount * 2
            tmp_str = f'Increased to {amount} points due to {damage_type} vulnerability.'
        else:
            tmp_str = f'Suffers {amount} points of {damage_type} damage.'

        if amount >= self.cur_hit_points:
            if self.unconscious_ind == False:
                tmp_str = (f'{tmp_str}\n{amount} exceeds current hit points' 
                           f'({self.cur_hit_points}): knocked unconsious')
            else:
                tmp_str = (f'{tmp_str}\n{amount} damage against unconscious target '
                           f'({self.cur_hit_points})')
            self.unconscious_ind = True
            self.stabilized = False

            # Instant Death?
            if (amount - self.cur_hit_points) >= self.hit_points:
                tmp_str = (f'{tmp_str}\n{(amount - self.cur_hit_points)}' 
                           f' exceeds hit points' 
                           f'({self.hit_points}): Instant Death')
                self.incr_death_save_failed_cnt(3)

            self.cur_hit_points = 0
        else:
            thp = self.cur_hit_points
            self.cur_hit_points -= amount
            tmp_str = (f'{tmp_str}\nResulting in ({thp} - {amount}) ' 
                       f'{self.cur_hit_points} points')

        self.damage_taken['Total'] += amount
        self.damage_taken[damage_type] += amount

        if self.debug_ind == 1:
            for i in tmp_str.splitlines():
                self.logger.debug(f"{self.get_name()}: {i}")

    def get_action(self, dist_list):
        ret_val = "Done"
        op_dist = dist_list[0][0]
        if not self.alive:
            ret_val = "None"
        elif not self.stabilized:
            ret_val = "Death Save"
        elif self.combat_preference == 'Melee':
            if op_dist > self.cur_movement:
                ret_val = "Movement"
            elif self.cur_movement >= op_dist > 8:
                ret_val = "Wait on Melee"
            elif op_dist <= 8:
                ret_val = "Melee"
        else:
            if op_dist > self.get_ranged_range:
                ret_val = "Movement"
            elif self.get_ranged_range >= op_dist > 8:
                ret_val = "Ranged"
            elif op_dist <= 8:
                ret_val = "Melee"

        return ret_val

    def set_finesse_ability(self):
        s = self.get_ability_modifier('Strength')
        d = self.get_ability_modifier('Dexterity')
        if s > d:
            self.finesse_ability_mod = 'Strength'
        else:
            self.finesse_ability_mod = 'Dexterity'

    def add_proficiency_bonus_for_attack(self, weapon_obj):
        # determine modifier
        # 1)  is this a martial weapon that needs specific proficiency
        #     if it is and the character has that, or the weapon is a standard
        #     one, add the character's proficiency bonus.
        if (weapon_obj.martial_weapon_ind is False
                or (weapon_obj.martial_weapon_ind is True
                    and weapon_obj.proficient_ind is True)):
            ret_val = int(self.proficiency_bonus)
        else:
            ret_val = 0

        return ret_val


    def ranged_attack(self, weapon_obj, vantage='Normal'):
        # determine modifier
        # 1)  is this a martial weapon that needs specific proficiency
        #     if it is and the character has that, or the weapon is a standard
        #     one, add the character's proficiency bonus.
        # if (weapon_obj.martial_weapon_ind is False
        #         or (weapon_obj.martial_weapon_ind is True
        #             and weapon_obj.proficient_ind is True)):
        #     modifier = int(self.proficiency_bonus)
        # else:
        modifier = self.add_proficiency_bonus_for_attack(weapon_obj)

        modifier += self.get_ability_modifier('Dexterity')

        attempt = Attack(weapon_obj=weapon_obj, attack_modifier=modifier,
                         versatile_use_2handed=False, vantage=vantage)

        if self.debug_ind == 1:
            self.logger.debug(f"{self.get_name()}: Ranged Attack Value: "
                              f"{attempt.attack_value}")
            self.logger.debug(f"{self.get_name()}: Ranged Poss. damage: "
                              f"{attempt.possible_damage}")

    def is_not_using_shield(self):
        return False

    def melee_attack(self, weapon_obj, vantage='Normal') -> tuple:
        # determine modifier
        # 1)  is this a martial weapon that needs specific proficiency
        #     if it is and the character has that, or the weapon is a standard
        #     one, add the character's proficiency bonus.
        # if (weapon_obj.martial_weapon_ind is False
        #         or (weapon_obj.martial_weapon_ind is True
        #             and weapon_obj.proficient_ind is True)):
        #     modifier = int(self.proficiency_bonus)
        # else:
        #     modifier = 0
        modifier = self.add_proficiency_bonus_for_attack(weapon_obj)
        damage_modifier = 0
        # 2)  Add the users Ability bonus, Strength for standard weapons
        #     or self.finesse_ability_mod for Finesse wepons
        if weapon_obj.finesse_ind is True:
            modifier += self.get_ability_modifier(self.finesse_ability_mod)
            damage_modifier = self.get_ability_modifier(self.finesse_ability_mod)
        else:
            modifier += self.get_ability_modifier('Strength')
            damage_modifier = self.get_ability_modifier('Strength')

        # if self.classObj.shield is None and weapon_obj.versatile_ind is True:
        if self.is_not_using_shield() and weapon_obj.versatile_ind is True:
            v2h = True
        else:
            v2h = False

        attempt = Attack(weapon_obj=weapon_obj, attack_modifier=modifier, damage_modifier=damage_modifier,
                         versatile_use_2handed=v2h, vantage=vantage)
        ret_val: tuple = (attempt.attack_value, attempt.possible_damage, attempt.damage_type)

        self.attack_roll_count+=1
        if attempt.natural_value == 20:
            self.attack_roll_nat20_count+=1
        if attempt.natural_value == 1:
            self.attack_roll_nat1_count+=1
        attack_roll: tuple = (attempt.natural_value, attempt.attack_value)
        self.attack_rolls.append(attack_roll)

        if self.debug_ind == 1:
            self.logger.debug(f"{self.get_name()}: Melee Attack Value: "
                              f"{attempt.attack_value}")
            self.logger.debug(f"{self.get_name()}: Melee Poss. damage: "
                              f"{attempt.possible_damage}")
        return ret_val

    def melee_defend(self, modifier=0, vantage='Normal',
                     possible_damage=0, damage_type='Unknown', attack_value=None):
        self.last_method_log = (f'melee_defend({modifier}, ' 
                                f'{vantage}, {possible_damage}, ' 
                                f'{damage_type})')

        if self.debug_ind == 1:
            self.logger.debug(f"{self.get_name()} attempts to defend against melee.")

        d = Die(20)
        if self.prone_ind:
            if vantage == 'Disadvantage':
                vantage = 'Normal'
            else:
                vantage = 'Advantage'
        if attack_value:
            value = attack_value
        else:
            value = d.roll() + modifier

        if value >= self.armor_class:
            tmp_str = (f'Fails to defend against melee attack roll: ' 
                       f'{value} >= {self.armor_class}')
            ret = False
            if self.cur_hit_points < 1:
                self.incr_death_save_failed_cnt(2)
                if self.debug_ind == 1:
                    self.logger.debug(f"{self.get_name()}: attacked while unconscious. Incurs two failed Death Saves.")

            if possible_damage > 0:
                self.damage(possible_damage, damage_type)
        else:
            tmp_str = (f'Successful defence against a melee attack roll: ' 
                       f'{value} < {self.armor_class}')
            ret = True

        if self.debug_ind == 1:
            for i in tmp_str.splitlines():
                self.logger.debug(f"{self.get_name()}: {i}")

        return ret

    def ranged_defend(self, modifier=0, vantage='Normal',
                      possible_damage=0, damage_type='Unknown'):
        self.last_method_log = (f'ranged_defend({modifier}, ' 
                                f'{vantage}, {possible_damage}' 
                                f'{damage_type})')
        d = Die(20)
        if self.prone_ind:
            if vantage == 'Advantage':
                vantage = 'Normal'
            else:
                vantage = 'Disadvantage'
        value = d.roll() + modifier

        if value >= self.armor_class:
            tmp_str = (f'Fails to defend against a ranged attack roll: ' 
                       f'{value} >= {self.armor_class}')
            ret = False
            if possible_damage > 0:
                self.damage(possible_damage, damage_type)
        else:
            tmp_str = (f'Successful defence against a ranged attack roll: ' 
                       f'{value} < {self.armor_class}')
            ret = True

        if self.debug_ind == 1:
            msg = f"{self.get_name()}: {tmp_str}"
            self.logger.debug(msg)

        return ret

    def heal(self, amount):
        self.last_method_log = f'heal({amount})'
        tmp_str = f'Heals {amount} hit points.'
        if self.cur_hit_points == 0 and self.alive:
            self.stabilize()

        if (self.cur_hit_points + amount) > self.hit_points:
            self.cur_hit_points = self.hit_points
            tmp_str = f'{tmp_str}\nReturned to max {self.hit_points} points'
        else:
            thp = self.cur_hit_points
            self.cur_hit_points += amount
            tmp_str = (f'{tmp_str}\nResulting in ({thp} + {amount}) ' 
                       f'{self.cur_hit_points} points')

        if self.debug_ind == 1:
            for i in tmp_str.splitlines():
                self.logger.debug(f"{self.get_name()}: {i}")

    def revive(self):
        self.last_method_log = f'revive()'
        self.stabilize()
        self.cur_hit_points = self.hit_points

        if self.debug_ind == 1:
            msg = f"{self.get_name()}: Has been Revived."
            self.logger.debug(msg)

    def get_ranged_range(self):
        if self.ranged_weapon:
            sql = (f"select range_1 from lu_weapon "
                   f"and name = '{self.ranged_weapon}' "
                   f"where category like '%Ranged'")
            res = self.db.query(sql)
            ret_val = res[0][0]
        else:
            ret_val = -1

        return ret_val


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = Character(db)
    a1.assign_ability_array()
    a1.set_armor_class()
    print(a1.get_gender())
    a2 = Character(db=db, ability_array_str='10,11,12,13,14,15', debug_ind=1)
    a2.assign_ability_array()
    a2.set_armor_class()
    print(a2.get_raw_ability_array())
    print(a2.get_ability_pref_array())
    print(a2.get_sorted_ability_array())
    a2.ability_array_obj.set_preference_array(pref_array=string_to_array(
                                            '5,0,2,1,4,3'
                                            ))
    print(a2.get_raw_ability_array())
    print(a2.get_ability_pref_array())
    print(a2.get_sorted_ability_array())
    print(a2.armor_class)
    print(a2.get_gender())

    # a3 = Character(db, level=43)
    a2 = Character(db=db, ability_array_str='6,6,6,6,6,6', debug_ind=1)
    a2.assign_ability_array()
    a2.set_armor_class()
    print(a2.get_raw_ability_array())
    print(a2.get_ability_pref_array())
    print(a2.get_sorted_ability_array())

