from InvokePSQL import InvokePSQL
from CommonFunctions import string_to_array
from AbilityArray import AbilityArray
from Attack import Attack
from Die import Die
from CharacterStats import CharacterStats
from Ctx import RpgLogging
from Ctx import Ctx, ctx_decorator

import random
import sys
import traceback


class Character(object):
    ctx: Ctx
    logger: RpgLogging

    @ctx_decorator
    def __init__(self,
                 db,
                 ctx: Ctx,
                 gender_candidate="Random",
                 ability_array_str="Common",
                 damage_generator="Random",
                 hit_point_generator="Max",
                 level=1,
                 debug_ind=0,
                 study_instance_id=-1,
                 series_id=-1,
                 encounter_id=-1,
                 **kwargs):

        # raise Exception("test error")
        self.db = db
        self.ctx = ctx
        self.method_last_call_audit = {}
        level = int(level)
        if level < 1 or level > 20:
            raise ValueError('Level should be between 1 and 20.')
        else:
            self.level = level

        self.damage_generator = damage_generator
        self.hit_point_generator = hit_point_generator
        self.debug_ind = debug_ind
        self.debugStr = ''

        self.logger = RpgLogging(logger_name=ctx.logger_name)

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
        # self.damage_taken = dict(Acid=0, Bludgeoning=0, Cold=0,
        #                          Fire=0, Force=0, Ligtning=0,
        #                          Necrotic=0, Piercing=0, Poison=0,
        #                          Psychic=0, Radiant=0, Slashing=0,
        #                          Thunder=0, Total=0, Unknown=0)
        # self.damage_dealt = dict(Acid=0, Bludgeoning=0, Cold=0,
        #                          Fire=0, Force=0, Ligtning=0,
        #                          Necrotic=0, Piercing=0, Poison=0,
        #                          Psychic=0, Radiant=0, Slashing=0,
        #                          Thunder=0, Total=0, Unknown=0)
        self.damage_adj = dict(Acid="", Bludgeoning="", Cold="", Fire="",
                               Force="", Ligtning="", Necrotic="", Piercing="",
                               Poison="", Psychic="", Radiant="", Slashing="",
                               Thunder="")
        # self.healing_received = 0
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
        self.set_finesse_ability()

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
        self.stats = None
        self.init_stats(study_instance_id=study_instance_id,
                        series_id=series_id,
                        encounter_id=encounter_id
                        )

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    @ctx_decorator
    def init_stats(self, study_instance_id, series_id, encounter_id):
        self.stats = CharacterStats(study_instance_id=study_instance_id,
                                    series_id=series_id,
                                    encounter_id=encounter_id,
                                    character_id=-1,
                                    character_name="Default",
                                    character_class="Default",
                                    character_race="Default",
                                    character_level=self.level
                                    )

    @ctx_decorator
    def get_character_stats(self):
        return self.stats.get_dict()

    def get_name(self):
        return "Generic Character"

    @ctx_decorator
    def get_damage_taken(self):
        return self.stats.get_damage_taken()

    @ctx_decorator
    def get_damage_dealt(self):
        return self.stats.get_damage_dealt()

    @ctx_decorator
    def inc_damage_dealt(self, damage_type, amount):
        return self.stats.inc_damage_dealt(damage_type=damage_type, amount=amount)

    @ctx_decorator
    def assign_gender(self):
        self.last_method_log = f"assign_gender(db)"
        d = Die(ctx=self.ctx, sides=100)
        a = d.roll()
        if a <= 40:
            result = "M"
        elif 40 < a <= 90:
            result = "F"
        else:
            result = "U"

        return result

    def get_gender(self):
        return self.gender

    @ctx_decorator
    def assign_ability_array(self, sort_array=None):
        self.last_method_log = (f'assign_ability_array('
                                f'{self.ability_array_str})')
        # if the string doesn't begin and end with a number, then it must
        # be a type that the ability array wants
        tmp = self.ability_array_str
        if tmp[0].isdigit() and tmp[-1].isdigit():
            tmp_array = string_to_array(tmp)
            self.ability_array_obj = AbilityArray(ctx=self.ctx, array_type="Predefined",
                                                  raw_array=tmp_array,
                                                  pref_array=sort_array,
                                                  debug_ind=self.debug_ind)
        else:
            self.ability_array_obj = AbilityArray(ctx=self.ctx, array_type=tmp,
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

    @ctx_decorator
    def set_taliesin_temperament_archetype(self):
        self.last_method_log = f'assignTaliesinTemperamentArchetype()'
        align_array = ['Bashful', 'Doc', 'Grumpy', 'Happy', 'Sneezy', 'Sleepy', 'Dopey']
        align_type = align_array[(random.randint(0, 6))]
        per_array = ['High', 'Mid', 'Low']
        per_type = per_array[(random.randint(0, 2))]

        ret_str = f"{align_type}/{per_type}"

        return ret_str

    def get_tta(self):
        return self.tta

    def get_base_movement(self):
        return 15

    @ctx_decorator
    def set_movement(self, amount: int):
        jdict = {
            "from_movement": self.cur_movement,
            "to_movement": amount,
        }
        self.cur_movement = amount
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    def zero_movement(self):
        self.set_movement(0)

    def half_movement(self):
        self.set_movement((self.cur_movement // 2))

    def double_movement(self):
        self.set_movement((self.cur_movement * 2))

    def reset_movement(self):
        self.set_movement(self.get_base_movement())

    @ctx_decorator
    def change_exhaustion_level(self, amount):
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

        jdict = {
            "from_exhaustion_level": orig_level,
            "to_exhaustion_level": self.exhaustion_level
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
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

    @ctx_decorator
    def assign_hit_points(self, level, hit_die, modifier):
        self.last_method_log = (f'assign_hit_points( ' 
                                f'{level}, ' 
                                f'{hit_die}, ' 
                                f'{modifier})')
        if self.hit_point_generator == 'Max':
            ret_str = ((level * hit_die) + (level * modifier))
        else:
            d = Die(ctx=self.ctx, sides=hit_die)
            ret_str = ((d.roll(rolls=level)) + (level * modifier))

        return ret_str

    @ctx_decorator
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
            dex_mod = self.get_ability_modifier(ability='Dexterity')

        if self.shield is not None and self.shield != 'None':
            sql = (f"select ac_base from dnd_5e.lu_armor "
                   f"where name = '{self.shield}';")

            res = self.db.query(sql)
            shield_bonus = res[0][0]
        else:
            shield_bonus = 0

        self.armor_class = base_ac + shield_bonus + dex_mod

        jdict = {
            "base_ac": base_ac,
            "shield_bonus": shield_bonus,
            "dex_mod": dex_mod,
            "armor_class": self.armor_class
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def contest_check(self, ability, vantage='Normal'):
        d = Die(ctx=self.ctx, sides=20)
        if vantage == 'Normal':
            r = d.roll()
        elif vantage == 'Advantage':
            r = d.roll_with_advantage()
        else:
            r = d.roll_with_disadvantage()

        mod = self.get_ability_modifier(ability=ability)

        ret_val = r + mod

        jdict = {
            "roll_amount": r,
            "modifier": mod
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

        return ret_val

    @ctx_decorator
    def roll_for_initiative(self, vantage='Normal'):
        ret_val = self.contest_check(ability='Dexterity', vantage=vantage)
        return ret_val

    def get_racial_traits(self):
        return iter([])

    @ctx_decorator
    def check_proficiency_skill(self, ability):
        ret_val = False
        t = self.get_racial_traits()
        if t:
            for b in t:
                if b.category == "Proficiency Skill":
                    if b.affected_name == ability:
                        ret_val = True
        return ret_val

    @ctx_decorator
    def incr_death_save_failed_cnt(self, amount: int = 1):
        from_value = self.death_save_failed_cnt
        from_alive = self.alive
        self.death_save_failed_cnt += amount
        if self.death_save_failed_cnt >= 3:
            self.alive = False

        jdict = {
            "from_death_save_value": from_value,
            "to_death_save_value": self.death_save_failed_cnt,
            "from_alive": from_alive,
            "to_alive": self.alive
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def stabilize(self):
        from_cur_hit_points = self.cur_hit_points
        from_death_save_passed_cnt = self.death_save_passed_cnt
        from_death_save_failed_cnt = self.death_save_failed_cnt
        from_stabilized = self.stabilized
        from_alive = self.alive
        from_unconscious_ind = self.unconscious_ind

        if self.cur_hit_points < 1:
            self.cur_hit_points = 1
        self.death_save_passed_cnt = 0
        self.death_save_failed_cnt = 0
        self.stabilized = True
        self.alive = True
        self.unconscious_ind = False

        jdict = {
            "from_cur_hit_points": from_cur_hit_points,
            "to_cur_hit_points": self.cur_hit_points,
            "from_death_save_passed_cnt": from_death_save_passed_cnt,
            "to_death_save_passed_cnt": self.death_save_passed_cnt,
            "from_death_save_failed_cnt": from_death_save_failed_cnt,
            "to_death_save_failed_cnt": self.death_save_failed_cnt,
            "from_stabilized": from_stabilized,
            "to_stabilized": self.stabilized,
            "from_alive": from_alive,
            "to_alive": self.alive,
            "from_unconscious_ind": from_unconscious_ind,
            "to_unconscious_ind": self.unconscious_ind,
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def death_save(self, vantage='Normal'):
        from_death_save_passed_cnt = self.death_save_passed_cnt,
        from_death_save_failed_cnt = self.death_save_failed_cnt
        res = self.contest_check(ability='Death', vantage=vantage)
        if res == 20:  # character is stablized
            self.stabilize()
        elif res >= 10:  # normal pass
            self.death_save_passed_cnt += 1
        elif res == 1:   # crit fail
            self.incr_death_save_failed_cnt(amount=2)
        else:   # res < 10 -- normal fail
            self.incr_death_save_failed_cnt(amount=1)

        if self.death_save_passed_cnt >= 3:
            self.stabilize()

        jdict = {
            "roll_value": res,
            "from_death_save_passed_cnt": from_death_save_passed_cnt,
            "to_death_save_passed_cnt": self.death_save_passed_cnt,
            "from_death_save_failed_cnt": from_death_save_failed_cnt,
            "to_death_save_failed_cnt": self.death_save_failed_cnt
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def check(self, skill, vantage='Normal', dc=10):
        jdict = {"dc": dc}
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
            adjusted_roll = self.contest_check(ability=ability, vantage=vantage)
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
            # elif (skill == 'Deception'
            #       or skill == 'Intimidation'
            #       or skill == 'Performance'
            #       or skill == 'Persuasion'):
            else:
                ability = 'Charisma'
            jdict['ability'] = ability
            # at exhaustion level 1 skills checks are affected
            if self.exhaustion_level >= 1:
                if vantage == 'Advantage':
                    vantage = 'Normal'
                else:
                    vantage = 'Disadvantage'
            jdict['exhaustion_level'] = self.exhaustion_level
            jdict['used_vantage'] = vantage

            adjusted_roll = self.contest_check(ability=ability, vantage=vantage)

            jdict['ability_adjusted_roll'] = adjusted_roll

            t_pb = 0
            if self.check_proficiency_skill(ability=skill):
                t_pb = int(self.proficiency_bonus)
                adjusted_roll = adjusted_roll + t_pb

            jdict['added_proficiency_bonus'] = t_pb
            jdict['used_adjusted_roll'] = adjusted_roll

        if adjusted_roll >= dc:
            res = True
        else:
            res = False

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return res

    def get_damage_generator(self):
        return self.damage_generator

    @ctx_decorator
    def damage(self, amount, damage_type="Unknown"):

        tmp_type = self.damage_adj[damage_type]

        jdict = {"damage_adj": tmp_type}
        if tmp_type and tmp_type == 'resistant':
            amount = amount // 2
        elif tmp_type and tmp_type == 'vulnerable':
            amount = amount * 2

        jdict['used_amount'] = amount
        jdict['from_unconscious'] = self.unconscious_ind
        jdict['from_stabilized'] = self.stabilized
        jdict['from_hit_points'] = self.cur_hit_points

        if amount >= self.cur_hit_points:
            self.unconscious_ind = True
            self.stabilized = False
            jdict['to_unconscious'] = self.unconscious_ind
            jdict['to_stabilized'] = self.stabilized

            # Instant Death?
            if (amount - self.cur_hit_points) >= self.hit_points:
                self.incr_death_save_failed_cnt(amount=3)
                jdict['instant_death'] = True
            else:
                jdict['instant_death'] = False

            self.cur_hit_points = 0
        else:
            self.cur_hit_points -= amount

        jdict['cur_hit_points'] = self.cur_hit_points
        self.stats.inc_damage_taken(damage_type=damage_type, amount=amount)

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    def get_user_header(self):
        return f'{self.get_name()}({self.cur_hit_points}/{self.hit_points})'

    @ctx_decorator
    def get_action(self, dist_list):
        ret_val = "Done"
        op_dist = dist_list[0][0]
        jdict = {
            "character_alive": self.alive,
            "character_stabilized": self.stabilized,
            "combat_preference": self.combat_preference,
            "cur_movement": self.cur_movement,
            "opponent_distance": op_dist,
            "ranged_weapon_range": self.get_ranged_range()
        }
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
            if op_dist > self.get_ranged_range():
                ret_val = "Movement"
            elif self.get_ranged_range >= op_dist > 8:
                ret_val = "Ranged"
            elif op_dist <= 8:
                ret_val = "Melee"

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return ret_val

    def get_vantage(self):
        return 'Normal'

    @ctx_decorator
    def set_finesse_ability(self):
        s = self.get_ability_modifier('Strength')
        d = self.get_ability_modifier('Dexterity')
        if s > d:
            self.finesse_ability_mod = 'Strength'
        else:
            self.finesse_ability_mod = 'Dexterity'

        jdict = {
            "strength_ability_mod": s,
            "dexterity_ability_mod": d,
            "finesse_ability_mod": self.finesse_ability_mod
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
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

    @ctx_decorator
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
        jdict = {"weapon_proficiency_bonus": modifier}

        modifier += self.get_ability_modifier('Dexterity')
        damage_modifier = self.get_ability_modifier('Dexterity')

        jdict["attack_modifier"] = modifier
        jdict["ability_damage_modifier"] = damage_modifier

        attempt = Attack(weapon_obj=weapon_obj, attack_modifier=modifier,
                         damage_modifier=damage_modifier,
                         versatile_use_2handed=False, vantage=vantage)

        jdict['ranged_attack_value'] = attempt.attack_value
        jdict['ranged_possible_damage'] = attempt.possible_damage
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def is_not_using_shield(self):
        return False

    @ctx_decorator
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
        modifier = self.add_proficiency_bonus_for_attack(weapon_obj=weapon_obj)
        jdict = {"weapon_proficiency_bonus": modifier}
        # damage_modifier = 0
        # 2)  Add the users Ability bonus, Strength for standard weapons
        #     or self.finesse_ability_mod for Finesse wepons
        if weapon_obj.finesse_ind is True:
            modifier += self.get_ability_modifier(ability=self.finesse_ability_mod)
            damage_modifier = self.get_ability_modifier(ability=self.finesse_ability_mod)
        else:
            modifier += self.get_ability_modifier(ability='Strength')
            damage_modifier = self.get_ability_modifier(ability='Strength')

        jdict["weapon"] = weapon_obj.name
        jdict["finesse_ind"] = weapon_obj.finesse_ind
        jdict["attack_modifier"] = modifier
        jdict["ability_damage_modifier"] = damage_modifier
        jdict["is_not_using_shield"] = self.is_not_using_shield()
        jdict["versatile_weapon"] = weapon_obj.versatile_ind

        if self.is_not_using_shield() and weapon_obj.versatile_ind is True:
            v2h = True
        else:
            v2h = False

        attempt = Attack(ctx=self.ctx, weapon_obj=weapon_obj,
                         attack_modifier=modifier, damage_modifier=damage_modifier,
                         versatile_use_2handed=v2h, vantage=vantage)
        ret_val: tuple = (attempt.attack_value, attempt.possible_damage, attempt.damage_type)

        jdict["roll_natural_value"] = attempt.natural_value
        jdict["attack_value"] = attempt.attack_value
        self.attack_roll_count += 1
        if attempt.natural_value == 20:
            self.attack_roll_nat20_count += 1
        if attempt.natural_value == 1:
            self.attack_roll_nat1_count += 1
        attack_roll: tuple = (attempt.natural_value, attempt.attack_value)
        self.attack_rolls.append(attack_roll)

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

        return ret_val

    @ctx_decorator
    def melee_defend(self, modifier=0, vantage='Normal',
                     possible_damage=0, damage_type='Unknown', attack_value=None):

        d = Die(ctx=self.ctx, sides=20)
        if self.prone_ind:
            if vantage == 'Disadvantage':
                vantage = 'Normal'
            else:
                vantage = 'Advantage'

        jdict = {"prone_ind": self.prone_ind,
                 "used_vantage": vantage}

        if attack_value:
            value = attack_value
        else:
            if vantage == 'Disadvantage':
                t_val = d.roll_with_disadvantage()
            elif vantage == 'Advantage':
                t_val = d.roll_with_advantage()
            else:
                t_val = d.roll()

            value = t_val + modifier

        jdict['used_attack_value'] = value
        jdict['armor_class'] = self.armor_class

        if value >= self.armor_class:
            ret = False
            if self.cur_hit_points < 1:
                self.incr_death_save_failed_cnt(amount=2)

            if possible_damage > 0:
                self.damage(amount=possible_damage, damage_type=damage_type)
        else:
            ret = True

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return ret

    @ctx_decorator
    def ranged_defend(self, modifier=0, vantage='Normal',
                      possible_damage=0, damage_type='Unknown'):
        d = Die(ctx=self.ctx, sides=20)
        if self.prone_ind:
            if vantage == 'Advantage':
                vantage = 'Normal'
            else:
                vantage = 'Disadvantage'

        jdict = {"prone_ind": self.prone_ind,
                 "used_vantage": vantage}

        if vantage == 'Disadvantage':
            t_val = d.roll_with_disadvantage()
        elif vantage == 'Advantage':
            t_val = d.roll_with_advantage()
        else:
            t_val = d.roll()

        value = t_val + modifier

        jdict['used_attack_value'] = value
        jdict['armor_class'] = self.armor_class

        if value >= self.armor_class:
            ret = False
            if possible_damage > 0:
                self.damage(possible_damage, damage_type)
        else:
            ret = True

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return ret

    @ctx_decorator
    def heal(self, amount):
        jdict = {"from_hit_points": self.cur_hit_points,
                 "max_hit_points": self.hit_points,
                 "character_alive": self.alive}
        if self.cur_hit_points == 0 and self.alive:
            self.stabilize()

        if (self.cur_hit_points + amount) > self.hit_points:
            self.cur_hit_points = self.hit_points
        else:
            self.cur_hit_points += amount

        jdict["to_hit_points"] = self.cur_hit_points
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def revive(self):
        jdict = {"from_hit_points": self.cur_hit_points}
        self.stabilize()
        self.cur_hit_points = self.hit_points
        jdict["to_hit_points"] = self.cur_hit_points
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def get_ranged_range(self):
        jdict = {}
        if self.ranged_weapon:
            jdict["ranged weapon"] = self.ranged_weapon
            sql = (f"select range_1 from lu_weapon "
                   f"where category like '%Ranged'" 
                   f"and name = '{self.ranged_weapon}' ")
            res = self.db.query(sql)
            jdict["query_result"] = res[0][0]
            self.ctx.crumbs[-1].add_audit(json_dict=jdict)
            ret_val = res[0][0]
        else:
            ret_val = -1


        return ret_val


if __name__ == '__main__':
    logger_name = 'character_main_test'
    ctx = Ctx(app_username='character_class_init', logger_name=logger_name)
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging()
    try:
        db = InvokePSQL()
        a1 = Character(db=db, ctx=ctx, debug_ind=1)
        a1.assign_ability_array()
        a1.set_armor_class()
        print(a1.get_gender())
        a2 = Character(db=db, ctx=ctx, ability_array_str='10,11,12,13,14,15', debug_ind=1)
        a2.assign_ability_array()
        a2.set_armor_class()
        print(a2.get_raw_ability_array())
        print(a2.get_ability_pref_array())
        print(a2.get_sorted_ability_array())
        a2.ability_array_obj.set_preference_array(pref_array=string_to_array('5,0,2,1,4,3'))
        print(a2.get_raw_ability_array())
        print(a2.get_ability_pref_array())
        print(a2.get_sorted_ability_array())
        print(a2.armor_class)
        print(a2.get_gender())

        # a3 = Character(db, level=43)
        a2 = Character(db=db, ctx=ctx, ability_array_str='6,6,6,6,6,6', debug_ind=1)
        a2.assign_ability_array()
        a2.set_armor_class()
        print(a2.get_raw_ability_array())
        print(a2.get_ability_pref_array())
        print(a2.get_sorted_ability_array())
    except Exception as error:
        print(ctx)
        print('error running encounter. error: {}'.format(error))
        print(type(error))  # the exception instance
        print(error.args)  # arguments stored in .args
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)))
