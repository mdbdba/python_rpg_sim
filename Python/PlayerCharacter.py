import sys
import traceback

from InvokePSQL import InvokePSQL
from Character import Character
from CommonFunctions import array_to_string
# from CommonFunctions import dict_to_string
from CommonFunctions import string_to_array
from CommonFunctions import inches_to_feet
from CharacterRace import CharacterRace
from PlayerCharacterClass import get_random_class_name
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
from Die import Die
from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging
from distanceFromPlayer import distanceTarget
from distanceFromPlayer import distanceFromPlayer

import os


class PlayerCharacter(Character):
    @ctx_decorator
    def __init__(self,
                 db,
                 ctx: Ctx,
                 character_id=-1,
                 race_candidate="Random",
                 class_candidate="Random",
                 gender_candidate="Random",
                 ability_array_str="Common",
                 damage_generator="Random",
                 hit_point_generator="Max",
                 level=1):

        Character.__init__(self, db=db, ctx=ctx, gender_candidate=gender_candidate,
                           ability_array_str=ability_array_str,
                           damage_generator=damage_generator,
                           hit_point_generator=hit_point_generator,
                           level=level)
        if character_id == -1:
            new_character_ind = True
        else:
            new_character_ind = False
        self.class_eval.append({
                       "pythonClass": "PlayerCharacter",
                       "newCharacter": new_character_ind,
                       "race_candidate": race_candidate,
                       "class_candidate": class_candidate,
                       "gender_candidate": gender_candidate,
                       "ability_array_str": ability_array_str,
                       "damage_generator": damage_generator,
                       "hit_point_generator": hit_point_generator,
                       "level": level})

        self.character_id = -1
        if character_id == -1:
            self.create_character(db=db,
                                  race_candidate=race_candidate,
                                  class_candidate=class_candidate,
                                  gender_candidate=gender_candidate,
                                  ability_array_type=ability_array_str,
                                  level=self.level)
        else:
            self.character_id = character_id
            self.get_character(db=db, character_id=self.character_id)

        self.stats.character_race = self.race_obj.race
        self.stats.character_class = self.class_obj.name
        self.stats.character_name = self.get_name()

        self.feature_obj = self.class_obj.get_class_level_feature(level=self.level, db=db)
        self.reset_movement()
        self.set_finesse_ability()
        self.set_proficiency_bonus()
        self.apply_traits()
        self.set_damage_adjs(db=db)
        self.set_armor_class()

        if character_id == -1:
            self.save_character(db=db)

        self.stats.character_id = self.character_id
        self.ranged_ammunition_type = self.class_obj.ranged_ammunition_type
        self.ranged_ammunition_amt = self.class_obj.ranged_ammunition_amt
        self.set_feature_list(db=db)
        self.add_class_feature_counts()
        self.add_available_spell_slots()
        self.set_spell_lists(db=db)

        self.class_eval[-1]["character_id"] = self.character_id
        self.class_eval[-1]["race"] = self.get_race()
        self.class_eval[-1]["class"] = self.get_class()
        self.class_eval[-1]["gender"] = self.get_gender()
        self.class_eval[-1]["rawAbilityArray"] = (
            array_to_string(self.get_raw_ability_array()))
        self.class_eval[-1]["sortedAbilityArray"] = (
            array_to_string(self.get_sorted_ability_array()))
        self.class_eval[-1]["racialAbilityArray"] = (
            array_to_string(self.get_racial_ability_bonus_array()))
        self.class_eval[-1]["abilityImpArray"] = (
            array_to_string(self.get_ability_improvement_array()))
        self.class_eval[-1]["abilityArray"] = (
            array_to_string(self.get_ability_array()))

        self.logger.info(msg="user_audit", json_dict=self.__dict__, ctx=ctx)

    @ctx_decorator
    def assign_race(self, race_candidate):
        if race_candidate == "Random":
            rand_obj = CharacterRace(db=self.db, ctx=self.ctx, race_candidate=race_candidate)
            race_to_use = rand_obj.race
        else:
            race_to_use = race_candidate

        return CharacterRace(db=self.db, ctx=self.ctx, race_candidate=race_to_use)

    @ctx_decorator
    def create_character(self,
                         db,
                         race_candidate,
                         class_candidate,
                         gender_candidate,
                         ability_array_type,
                         level):

        self.last_method_log = (f'create_character(db, ' 
                                f'{race_candidate}, '
                                f'{class_candidate}, '
                                f'{gender_candidate}, '
                                f'{ability_array_type}, '
                                f'{level})')
        self.assign_ability_array()
        self.race_obj = self.assign_race(race_candidate=race_candidate)
        self.class_obj = self.assign_class(class_candidate=class_candidate)
        self.race_obj.set_randoms(db=self.db, gender=self.gender)

        self.ability_array_obj.set_preference_array(pref_array=self.get_ability_sort_array())
        self.ability_array_obj.set_racial_array(bonus_array=self.get_racial_ability_bonus_array())

        # Since ability array bonuses are figured when levels change we
        # will figure hit points the same way.  That way of the constitution
        # mod changes from level to level the hit points will reflect that.
        if self.class_obj.melee_weapon is not None:
            self.melee_weapon_obj = Weapon(db=db, ctx=self.ctx, name=self.get_melee_weapon())
            self.melee_weapon_obj.set_weapon_proficient()
        if self.class_obj.ranged_weapon is not None:
            self.ranged_weapon_obj = Weapon(db=db, ctx=self.ctx, name=self.get_ranged_weapon())
            self.ranged_weapon_obj.set_weapon_proficient()

        self.hit_points = 0
        self.adjust_for_levels(db=db)
        self.set_armor_class()
        self.cur_hit_points = self.hit_points
        self.temp_hit_points = 0

    @ctx_decorator
    def set_feature_list(self, db):
        self.feature_list.extend(self.class_obj.feature_list)

        sql = (f"select distinct case when category = 'Spell' then 'Spellcasting' else lrt.name end " 
               f"from lu_racial_trait lrt " 
               f"join lu_race as r on (lrt.race = r.race or lrt.race = r.subrace_of)"
               f"where category in ('Feat', 'Vision', 'Armor Class', 'Spell') "
               f"and coalesce(description, '') not in ('targetAffect:Smell') "
               f"and name not like '% Build' "
               f"and name is not null " 
               f"and (r.race = '{self.get_race()}' or r.subrace_of = '{self.get_race()}')")

        results = db.query(sql)
        for result in results:
            self.feature_list.append(result[0])

    def add_class_feature_counts(self):
        for a in range(len(self.feature_obj)):
            if self.feature_obj[a][2] == 'Rage':
                self.feature_counts['Rage'] = {'Rages Available': int(self.feature_obj[a][4]),
                                               'Rage Damage': int(self.feature_obj[a][6])}

    def add_available_spell_slots(self):
        # print(self.feature_obj)
        for i in self.feature_obj:
            if i[2] == 'Spellcasting' and i[3] == 'Spell Slots':
                if i[5] == 'Cantrips Known':
                    cantrips = i[6]
                else:
                    if i[8]:
                        cantrips = i[8]
                    else:
                        cantrips = '0'

                self.populate_available_spell_slots(cantrips_known=cantrips, spell_slot_str=i[4])

    @ctx_decorator
    def get_max_impact(self, db, spell_name, cast_at_level):
        effect_sql = (f"select spell_id, effect_category, effect_type, "
                      f"effect_modifier, effect_die, effect_adj, explicit_targets "
                      f"from v_spell_effect_by_level "
                      f"where spell_name = '{spell_name}' "
                      f"and {cast_at_level} between lower_level and upper_level")
        effect_results = db.query(effect_sql)
        max_impact = 0

        for effect_result in effect_results:
            if effect_result[3]:
                effect_modifier = effect_result[3]
            else:
                effect_modifier = 0

            if effect_result[4]:
                effect_die = effect_result[4]
            else:
                effect_die = 0

            if effect_result[5]:
                effect_adj = effect_result[5]
            else:
                effect_adj = 0

            if effect_result[6]:
                explicit_targets = effect_result[6]
            else:
                explicit_targets = 1

            max_impact = max_impact + ((effect_modifier * effect_die) + effect_adj) * explicit_targets

        return max_impact

    @ctx_decorator
    def set_spell_lists(self, db):
        self.set_racial_spells(db)
        self.set_class_spells(db)
        self.set_granted_spells(db)

    @ctx_decorator
    def set_granted_spells(self, db):
        pass

    @ctx_decorator
    def set_class_spells(self, db):
        # print("Setting class spells")
        if "Spellcasting" in self.feature_list:
            # print("Found Spellcasting for this character")
            i=0
            max_spell_level = -1
            while i <= self.level:
                # print(f"level {i} = {self.available_spell_slots[i]}")
                if self.available_spell_slots[i] > 0:
                    max_spell_level = i
                i += 1
            print(f"max_spell_level = {max_spell_level}")
            if max_spell_level > -1:
                sql = (f"select a.spell_level, b.id, a.spell_name, a.order_by, b.save, "
                       f"b.casting_time_uom, b.range_amt, b.range_uom, b.range_aoe, "
                       f"b.duration_amt, b.duration_uom, b.verbal_component_ind, "
                       f"b.concentration_ind, b.higher_level_cast, b.save_outcome, "
                       f"b.general_category "
                       f"from dnd_5e.lu_class_spell_choice_defaults a "
                       f"join dnd_5e.lu_spell b on a.spell_name = b.name "
                       f"and a.spell_level = b.level "
                       f"where a.spell_level <= {max_spell_level} "
                       f"and a.class = '{self.get_class()}' "
                       f"order by a.spell_level, a.order_by ")

                spells = db.query(sql)
                print(spells)
                for spell in spells:
                    max_impact = self.get_max_impact(db=db, spell_name=spell[2], cast_at_level=spell[0])
                    spell_ref_dict = {"category": spell[15],
                                      "source": "class",
                                      "id": spell[1],
                                      "name": spell[2],
                                      "min_level": spell[0],
                                      "max_impact": max_impact,
                                      "cast_at_level": spell[0],
                                      "cast_with_ability": "Default",
                                      "range_amt": spell[6],
                                      "range_aoe": spell[8],
                                      "casting_uom": spell[5],
                                      "verbal_component_ind": spell[11],
                                      "available_count": -1
                                      }

    @ctx_decorator
    def set_racial_spells(self, db):
        # Set racial spells first.  Then if they are already there, then:
        # if it is a cantrip or can be used to deal more damage, use the class spell definition
        # otherwise keep the racial allowance.
        sql = (f"select lrt.affected_name, lrt.race, lrt.name, lrt.affected_adj, "
               f"lrt.recharge_on, lrt.description " 
               f"from lu_racial_trait lrt " 
               f"join lu_race as r on (lrt.race = r.race or lrt.race = r.subrace_of) " 
               f"where category in ('Spell') " 
               f"and affected_name != 'Cantrip' " 
               f"and affected_name not like 'level:%' " 
               f"and lrt.name is not null "
               f"and (r.race = '{self.get_race()}' or r.subrace_of = '{self.get_race()}')" 
               f"union all " 
               f"select lrscd.spell_name as affected_name, lrscd.race, " 
               f"'Racial Choice ' || ((spell_level * 10) + order_by) as name, " 
               f"null as affected_adj, lrscd.recharge_on, null as description " 
               f"from lu_racial_spell_choice_defaults lrscd " 
               f"where race = '{self.get_race()}'")

        results = db.query(sql)
        search_str = "'No Spells', "
        lrt_dict = {}
        for result in results:
            if search_str == "'No Spells', ":  # if there are no results the search string will equal 'No Spells'
                search_str = ""                # otherwise, we're going to build the search string.

            if result[4] and (result[4] == 'Long Rest' or result[4] == 'Sunrise'):
                available_count = 1
            else:
                available_count = -1

            tmp_dict = {"available_count": available_count}
            no_level_restriction = True
            if result[5]:
                # split by , and then :   -- examples: onLevel:3,spellLevel:2  Cost:Movement(15feet);Range:60feet
                category_array = result[5].split(',')
                for cat in category_array:
                    tmp_record = cat.split(':')
                    if tmp_record[0] == 'onLevel' and self.level < int(tmp_record[1]):
                        no_level_restriction = False
                    else:
                        tmp_dict[tmp_record[0]] = tmp_record[1]

            if no_level_restriction:
                lrt_dict[result[0]] = tmp_dict
                search_str = f"{search_str}'{result[0]}', "

        if (search_str != "'No Spells', "
                and search_str != ""
                and search_str is not None):
            search_str = search_str[0:-2]
            sql2 = (f"select name, level, save, casting_time_uom, range_amt, range_uom, range_aoe, "
                    f"duration_amt, duration_uom, concentration_ind, higher_level_cast, "
                    f"verbal_component_ind, general_category, id "
                    f"from lu_spell ls "
                    f"where name in ({search_str})")
            spell_results = db.query(sql2)
        else:
            spell_results = []

        if spell_results:
            for spell in spell_results:
                # effect_sql = (f"select spell_id, effect_category, effect_type, "
                #               f"effect_modifier, effect_die, effect_adj, explicit_targets "
                #               f"from v_spell_effect_by_level "
                #               f"where spell_name = '{spell[0]}' "
                #               f"and {self.level} between lower_level and upper_level")
                # effect_results = db.query(effect_sql)

                # if effect_results[0][3]:
                #     effect_modifier = effect_results[0][3]
                # else:
                #     effect_modifier = 0

                # if effect_results[0][4]:
                #     effect_die = effect_results[0][4]
                # else:
                #     effect_die = 0

                # if effect_results[0][5]:
                #     effect_adj = effect_results[0][5]
                # else:
                #     effect_adj = 0

                # if effect_results[0][6]:
                #     explicit_targets = effect_results[0][6]
                # else:
                #     explicit_targets = 1

                # max_impact = ((effect_modifier*effect_die)+effect_adj)*explicit_targets

                if 'spellLevel' in lrt_dict[spell[0]].keys():
                    cast_at_level = int(lrt_dict[spell[0]]['spellLevel'])
                else:
                    cast_at_level = int(spell[1])
                max_impact = self.get_max_impact(db=db, spell_name=spell[0], cast_at_level=cast_at_level)
                if 'castAbility' in lrt_dict[spell[0]].keys():
                    cast_with_ability = lrt_dict[spell[0]]['castAbility']
                else:
                    cast_with_ability = "Default"

                spell_ref_dict = {"category": spell[12],
                                  "source": "race",
                                  "id": spell[13],
                                  "name": spell[0],
                                  "min_level": spell[1],
                                  "cast_at_level": cast_at_level,
                                  "cast_with_ability": cast_with_ability,
                                  "max_impact": max_impact,
                                  "range_amt": spell[4],
                                  "range_aoe": spell[6],
                                  "casting_uom": spell[3],
                                  "verbal_component_ind": spell[11],
                                  "available_count": lrt_dict[spell[0]]['available_count']
                                  }

                self.spell_list[spell[0]] = spell_ref_dict
                if spell[3] == 'Action':
                    self.spell_list_action[spell[0]] = spell_ref_dict
                elif spell[3] == 'Bonus Action':
                    self.spell_list_bonus_action[spell[0]] = spell_ref_dict
                else:
                    self.spell_list_reaction[spell[0]] = spell_ref_dict

    @ctx_decorator
    def adjust_for_levels(self, db):
        for adj_level in range(self.level):
            level = adj_level + 1  # range indexes start at 0.
            # if there's ability change for this level make that change
            sql = (f"select count(level) "
                   f"from dnd_5e.lu_class_level_feature "
                   f"where level = {level} "
                   f"and class = '{self.get_class()}' "
                   f"and feature = 'Ability Score Improvement';")
            result = db.query(sql)
            if int(result[0][0]) == 1:
                # print("\n\n\nDoing ability_score_improvement\n\n\n")
                self.ability_array_obj.ability_score_improvement()

            # since the constitution could change at each level
            # that would affect the hit point amount. So, have to
            # do it for each level.
            self.set_ability_modifier_array(db=db)
            # Add new hit points
            self.hit_points = self.add_hit_points(db=self.db, hit_die=self.get_hit_die(),
                                                  modifier=self.ability_modifier_array[2])

    @ctx_decorator
    def set_ability_modifier_array(self, db):
        q = self.get_ability_array()
        for r in range(len(q)):
            sql = (f"select modifier "
                   f"from dnd_5e.lu_ability_score_modifier "
                   f"where value = '{q[r]}';")

            result = db.query(sql)
            self.ability_modifier_array[r] = int(result[0][0])

    @ctx_decorator
    def add_hit_points(self, db, hit_die, modifier):
        self.last_method_log = (f'assign_hit_points( '
                                f'{hit_die}, '
                                f'{modifier})')

        sql = (f"select affected_adj "
               f"from lu_racial_trait "
               f"where category = 'Hit Point Adj' "
               f"and recharge_on = 'Level' "
               f"and race = '{self.get_race()}'")

        result = db.query(sql)
        if result:
            racial_adj = int(result[0][0])
        else:
            racial_adj = 0

        if self.hit_point_generator == 'Max':
            ret_val = (self.hit_points + (hit_die + modifier + racial_adj))
        else:
            d = Die(self.get_hit_die())
            ret_val = d.roll(1) + (modifier + racial_adj)
        return ret_val

    @ctx_decorator
    def save_character(self, db):
        self.last_method_log = f'save_character(db)'
        raw_ability_string = array_to_string(self.get_raw_ability_array())
        ability_base_string = array_to_string(self.get_raw_ability_array())
        ability_string = array_to_string(self.get_ability_array())
        ability_racial_mod_string = (
            array_to_string(self.get_racial_ability_bonus_array()))

        ability_modifier_string = array_to_string(self.ability_modifier_array)
        sql = (f"insert into dnd_5e.character(name, gender, race, class, "
               f"level, TTA, raw_ability_string, "
               f"ability_base_string,ability_string, "
               f"ability_racial_mod_string, ability_modifier_string, "
               f"hit_points, temp_hit_points, cur_hit_points, height, "
               f"weight, alignment, alignment_abbrev, skin_tone, hair_color, "
               f"hair_type, eye_color, melee_weapon, ranged_weapon, "
               f"ranged_ammunition_type, ranged_ammunition_amt, armor, shield"
               f") values ('{self.get_name()}', "
               f"'{self.get_gender()}', '{self.get_race()}', "
               f"'{self.get_class()}',{self.level}, '{self.tta}', "
               f"'{raw_ability_string}', "
               f"'{ability_base_string}', '{ability_string}', "
               f"'{ability_racial_mod_string}', "
               f"'{ability_modifier_string}', {self.hit_points}, "
               f"{self.temp_hit_points}, {self.cur_hit_points}, "
               f"{self.get_height()}, {self.get_weight()}, "
               f"'{self.get_alignment_str()}', '{self.get_alignment_abbrev()}', "
               f"'{self.get_skin_tone()}', '{self.get_hair_color()}', "
               f"'{self.get_hair_type()}', '{self.get_eye_color()}', "
               f"'{self.get_melee_weapon()}', '{self.get_ranged_weapon()}', "
               f"'{self.get_ranged_ammunition_type()}', "
               f"{self.get_ranged_ammunition_amt()}, '{self.get_armor()}', "
               f"'{self.get_shield()}')")

        self.character_id = db.insert_and_return_id(sql)

    @ctx_decorator
    def valid_character_id(self, db, character_id):
        sql = f"select count(id) from dnd_5e.character where id = {character_id};"
        results = db.query(sql)
        id_cnt = results[0][0]
        if id_cnt == 1:
            return True
        else:
            return False

    @ctx_decorator
    def get_character(self, db, character_id):
        if self.valid_character_id(db=db, character_id=character_id):
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
            self.race_obj = self.assign_race(race_candidate=results[0][2])
            self.race_obj.set_randoms(
                   name=results[0][0],
                   alignment={"alignment": results[0][16],
                              "abbreviation": results[0][17]},
                   skin_tone=results[0][18],
                   hair_color=results[0][19],
                   hair_type=results[0][20],
                   eye_color=results[0][21])
            self.race_obj.height = results[0][14]
            self.race_obj.weight = results[0][15]
            self.class_obj = self.assign_class(class_candidate=results[0][3])
            self.level = results[0][4]
            self.tta = results[0][5]
            self.ability_array_str = results[0][6]
            ability_racial_mod_string = results[0][9]
            self.ability_modifier_array = string_to_array(results[0][10])
            self.class_obj.melee_weapon = results[0][22]
            self.class_obj.ranged_weapon = results[0][23]
            self.class_obj.ranged_ammunition_type = results[0][24]
            self.class_obj.ranged_ammunition_amt = results[0][25]
            self.class_obj.armor = results[0][26]
            self.class_obj.shield = results[0][27]

            self.assign_ability_array(sort_array=self.class_obj.get_class_ability_sort_array())
            self.ability_array_obj.set_racial_array(bonus_array=self.race_obj.ability_bonuses)
            self.hit_points = 0
            self.adjust_for_levels(db=db)
            self.set_armor_class()
            self.cur_hit_points = self.hit_points
            self.temp_hit_points = 0

            # Since ability array bonuses are figured when levels change we
            # will figure hit points the same way.  That way of the constitution
            # mod changes from level to level the hit points will reflect that.
            if self.class_obj.melee_weapon is not None:
                self.melee_weapon_obj = Weapon(db=db, ctx=self.ctx, name=self.get_melee_weapon())
                self.melee_weapon_obj.set_weapon_proficient()
            if self.class_obj.ranged_weapon is not None:
                self.ranged_weapon_obj = Weapon(db=db, ctx=self.ctx, name=self.get_ranged_weapon())

            tmp_rab_str = array_to_string(self.race_obj.ability_bonuses)

            if ability_racial_mod_string != tmp_rab_str:
                tmp_str = (f"\n**WARNING: "
                           f"Racial Ability Array Mismatches: "
                           f"{ability_racial_mod_string} "
                           f"{tmp_rab_str}**\n")
                print(tmp_str)
            self.set_armor_class()

    @ctx_decorator
    def apply_traits(self):
        jdict = {}
        for i in self.race_obj.traitContainer.rawtraits:
            if i[7]:
                value = i[7]
            else:
                value = True
            if i[1] == 'Relentless':
                self.feature_counts['Relentless'] = value
                jdict['relentless_uses_available'] = self.feature_counts['Relentless']
            if i[1] == 'Lucky':
                self.feature_counts['Lucky'] = 3
                jdict['lucky_uses_available'] = self.feature_counts['Lucky']
            if i[1] == 'Savage Attacks':
                self.feature_counts['Savage Attacks'] = value
                jdict['savage_attack_crit_bonus'] = self.feature_counts['Savage Attacks']
            if i[1] == 'Nimble Escape':
                self.feature_counts['Nimble Escape'] = value
                jdict['nimble_escape_bonus'] = self.feature_counts['Nimble Escape']

            self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    def get_combat_preference(self):
        if self.class_obj.combat_preference:
            return_val = self.class_obj.combat_preference
        else:
            return_val = self.combat_preference

        return return_val

    def get_ability_sort_array(self):
        return self.class_obj.ability_sort_array

    def set_preference_array(self, pref_array_str):
        tmp_array = string_to_array(pref_array_str)
        self.ability_array_obj.set_preference_array(pref_array=tmp_array)
        self.set_ability_modifier_array(self.db)

    @ctx_decorator
    def set_racial_array(self, bonus_array):
        tmp_array = string_to_array(bonus_array)
        self.ability_array_obj.set_racial_array(bonus_array=tmp_array)
        self.set_ability_modifier_array(self.db)

    def get_racial_ability_bonus_array(self):
        return self.race_obj.ability_bonuses

#    def get_ability_improvement_array(self):
#          return self.ability_array_obj.get_imp_array()

    def get_name(self):
        try:
            return self.race_obj.name
        except AttributeError:
            return "Not Assigned"

    def get_alignment_str(self):
        return self.race_obj.alignment.get('alignment')

    def get_alignment_abbrev(self):
        return self.race_obj.alignment.get('abbreviation')

    def get_skin_tone(self):
        return self.race_obj.skinTone

    def get_hair_color(self):
        return self.race_obj.hairColor

    def get_hair_type(self):
        return self.race_obj.hairType

    def get_eye_color(self):
        return self.race_obj.eyeColor

    def get_height(self):
        return self.race_obj.height

    def get_weight(self):
        return self.race_obj.weight

    def get_race(self):
        return self.race_obj.race

    def get_class(self):
        return self.class_obj.name

    def get_hit_die(self):
        return self.class_obj.hit_die

    def get_ranged_weapon(self):
        if self.class_obj.ranged_weapon:
            return_val = self.class_obj.ranged_weapon
        else:
            return_val = "NotDefined"
        return return_val

    def get_melee_weapon(self):
        return self.class_obj.melee_weapon

    def get_ranged_ammunition_type(self):
        return self.class_obj.ranged_ammunition_type

    def get_ranged_ammunition_amt(self):
        return self.class_obj.ranged_ammunition_amt

    def get_armor(self):
        return self.class_obj.armor

    def get_shield(self):
        return self.class_obj.shield

    def get_base_movement(self):
        return self.race_obj.base_walking_speed

    def get_racial_traits(self):
        return self.race_obj.traitContainer.traits

    @ctx_decorator
    def assign_class(self, class_candidate):
        self.last_method_log = f'assign_class(db, {class_candidate})'

        if class_candidate == "Random":
            tmp_class = get_random_class_name(self.db)
        else:
            tmp_class = class_candidate
        obj = self.class_subclass_switch(class_candidate=tmp_class)

        return obj

    @ctx_decorator
    def class_subclass_switch(self, class_candidate):
        switcher = {
            'Barbarian': BarbarianPCClass(db=self.db, ctx=self.ctx),
            'Bard': BardPCClass(db=self.db, ctx=self.ctx),
            'Cleric': ClericPCClass(db=self.db, ctx=self.ctx),
            'Druid': DruidPCClass(db=self.db, ctx=self.ctx),
            'Fighter': FighterPCClass(db=self.db, ctx=self.ctx),
            'Monk': MonkPCClass(db=self.db, ctx=self.ctx),
            'Paladin': PaladinPCClass(db=self.db, ctx=self.ctx),
            'Ranger': RangerPCClass(db=self.db, ctx=self.ctx),
            'Rogue': RoguePCClass(db=self.db, ctx=self.ctx),
            'Sorcerer': SorcererPCClass(db=self.db, ctx=self.ctx),
            'Warlock': WarlockPCClass(db=self.db, ctx=self.ctx),
            'Wizard': WizardPCClass(db=self.db, ctx=self.ctx)
        }
        return switcher.get(class_candidate, "Unknown Class")

    # def set_finesse_ability(self):
    #     s = self.get_ability_modifier('Strength')
    #     d = self.get_ability_modifier('Dexterity')
    #     if s > d:
    #         self.finesse_ability_mod = 'Strength'
    #     else:
    #         self.finesse_ability_mod = 'Dexterity'

    @ctx_decorator
    def set_damage_adjs(self, db):
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
               f"and (r.race = '{self.get_race()}' "
               f"or r.subrace_of = '{self.get_race()}')")

        rows = db.query(sql)
        for row in rows:
            self.damage_adj[row[0]] = row[1]

    @ctx_decorator
    def set_proficiency_bonus(self):
        for a in range(len(self.feature_obj)):
            if self.feature_obj[a][2] == 'proficiency_bonus':
                self.proficiency_bonus = int(self.feature_obj[a][4])

    @ctx_decorator
    def is_not_using_shield(self):
        if self.class_obj.shield == 'None':
            ret_val = True
        else:
            ret_val = False
        return ret_val

    @ctx_decorator
    def default_melee_attack(self, ctx, target_name, target, attacker_id='unknown',
                             vantage='Normal', luck_retry=False):
        return self.melee_attack(ctx=ctx, weapon_obj=self.melee_weapon_obj,
                                 attacker_id=attacker_id, target_name=target_name, target=target,
                                 vantage=vantage, luck_retry=luck_retry)

    @ctx_decorator
    def default_ranged_attack(self, ctx, target,
                              attacker_id='unknown', vantage='Normal', luck_retry=False):
        self.stats.ranged_attack_attempts += 1
        return self.ranged_attack(ctx=ctx, weapon_obj=self.ranged_weapon_obj,
                                  target=target, attacker_id=attacker_id,
                                  vantage=vantage, luck_retry=luck_retry)

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'Name:         {self.get_name()}\n'
                  f'Id            {self.character_id}\n'
                  f'TTA:          {self.get_tta()}\n'
                  f'Gender:       {self.get_gender()}\n'
                  f'Race:         {self.get_race()} ('
                  f'{self.race_obj.source_material})\n'
                  f'Movement:     {self.cur_movement}\n'
                  f'Class:        {self.get_class()} ('
                  f'{self.class_obj.source_material})\n'
                  f'Armor Class:  {self.armor_class}\n'
                  f'Level:        {self.level}\n'
                  f'Hit Die:      {self.get_hit_die()}\n')
        if self.cur_hit_points:
            outstr = (f'{outstr}'
                      f'Hit Points:   {self.cur_hit_points} / '
                      f'{self.hit_points}\n')
        if self.proficiency_bonus:
            outstr = (f'{outstr}'
                      f'Prof Bonus:   {self.proficiency_bonus}\n')

        outstr = (f'{outstr}'
                  f'Height:       {inches_to_feet(self.get_height())}\n'
                  f'Weight:       {self.get_weight()} pounds\n'
                  f'Alignment:    {self.get_alignment_str()}\n'
                  f'AlignAbbrev:  {self.get_alignment_abbrev()}\n'
                  f'Skin Tone:    {self.get_skin_tone()}\n')

        if self.get_hair_color():
            outstr = (f'{outstr}Hair Color:   {self.get_hair_color()}\n'
                      f'Hair Type:    {self.get_hair_type()}\n')

        outstr = (f'{outstr}Eye Color:    {self.get_eye_color()}\n'
                  f'Size:         {self.race_obj.size}\n')
        if self.race_obj.source_credit_url:
            outstr = (f'{outstr}Race URL:          '
                      f'{self.race_obj.source_credit_url}\n')
        if self.race_obj.source_credit_comment:
            outstr = (f'{outstr}Race Comment:      '
                      f'{self.race_obj.source_credit_comment}\n')

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
                  f'{self.get_raw_ability_array()}\n'
                  f'Ordered Array:      '
                  f'{self.get_numerically_sorted_ability_array()}\n'
                  f'Sort Array:    {self.get_ability_pref_str_array()}\n'
                  f'Nbr Sort Array:     {self.ability_array_obj.get_pref_array()}\n'
                  f'Sorted:             {self.get_sorted_ability_array()}\n')

        outstr = (f'{outstr}\nAbility         Mod  Total = (Base + '
                  f'Racial + Level Improvements)\n')

        sorted_array = self.get_sorted_ability_array()
        ability_array = self.get_ability_array()
        ability_imp_array = self.get_ability_improvement_array()
        label_array = self.ability_array_obj.ability_label_array
        for c in range(len(label_array)):
            outstr = (f'{outstr}\n{label_array[c].ljust(16)}'
                      f'{str(self.ability_modifier_array[c]).rjust(3)}   '
                      f'{str(ability_array[c]).rjust(2)}   = ('
                      f'{str(sorted_array[c]).rjust(2)}  +   '
                      f'{str(self.race_obj.ability_bonuses[c]).rjust(2)}'
                      f'   +   {str(ability_imp_array[c]).rjust(2)})\n')

        if self.race_obj.languages:
            outstr = f'{outstr}\n\nLanguages:'
            for lang in self.race_obj.languages:
                outstr = f'{outstr}\n   {lang}'

        if self.race_obj.traitContainer.proficient:
            outstr = f'{outstr}\n\nProficiencies:'

            tmp_var = self.race_obj.traitContainer.proficient
            for p in range(len(tmp_var)):
                tmpprofstr = tmp_var[p].ljust(23)
                tmpsrcstr = self.race_obj.traitContainer.proficient_source[p]
                outstr = f'{outstr}\n   {tmpprofstr} ({tmpsrcstr})'

        for b in self.race_obj.traitContainer.traits:
            if b.category != "Proficiency Skill":
                outstr = f'{outstr}\n{b}'

        if self.feature_obj:
            outstr = f'{outstr}\n\nClass Features:\n'
            for b in range(len(self.feature_obj)):
                for c in range(len(self.feature_obj[b])):
                    if self.feature_obj[b][c] is not None:
                        outstr = f'{outstr} {self.feature_obj[b][c]}'
                outstr = f'{outstr}\n'
        outstr = f'{outstr}\ndamage ADJ:'

        for pkey, pvalue in sorted(self.damage_adj.items()):
            if len(pvalue) > 2:
                outstr = f'{outstr}\n{pkey}: {pvalue}'

        outstr = f'\n{outstr}\n'
        return outstr

    def __repr__(self):
        outstr = (f'{{ "class": "{self.__class__.__name__}", '
                  f'"Name": "{self.get_name()}", '
                  f'"Id": "{self.character_id}", '
                  f'"TTA": "{self.get_tta()}", '
                  f'"Gender": "{self.get_gender()}", '
                  f'"Race": "{self.get_race()}", '
                  f'"Movement": "{self.cur_movement}", '
                  f'"Class": "{self.get_class()}", '
                  f'"Armor Class": "{self.armor_class}", '
                  f'"Level": "{self.level}", '
                  f'"Hit Die": "{self.get_hit_die()}", ')
        if self.cur_hit_points:
            outstr = f'{outstr}"Hit Points": "{self.cur_hit_points}/{self.hit_points}", '

        if self.proficiency_bonus:
            outstr = f'{outstr}"Prof Bonus": "{self.proficiency_bonus}", '

        outstr = (f'{outstr}'
                  f'"Height": "{inches_to_feet(self.get_height())}", '
                  f'"Weight": "{self.get_weight()} pounds", '
                  f'"Alignment": "{self.get_alignment_str()}", '
                  f'"AlignAbbrev": "{self.get_alignment_abbrev()}", '
                  f'"Skin Tone": "{self.get_skin_tone()}", ')

        if self.get_hair_color():
            outstr = (f'{outstr}"Hair Color": "{self.get_hair_color()}", '
                      f'"Hair Type":  "{self.get_hair_type()}", ')

        outstr = (f'{outstr}"Eye Color": "{self.get_eye_color()}", '
                  f'"Size": "{self.race_obj.size}", ')
        if self.race_obj.source_credit_url:
            outstr = (f'{outstr}"Race URL": '
                      f'"{self.race_obj.source_credit_url}", ')
        if self.race_obj.source_credit_comment:
            outstr = (f'{outstr}"Race Comment": '
                      f'"{self.race_obj.source_credit_comment}", ')

        if self.finesse_ability_mod is not None:
            outstr = (f'{outstr}"Finesse Ability": '
                      f'"{self.finesse_ability_mod}", ')
        if self.melee_weapon is not None:
            outstr = (f'{outstr}"Melee Weapon": '
                      f'"{self.melee_weapon}", ')
        if self.ranged_weapon is not None:
            outstr = (f'{outstr}"Ranged Weapon": '
                      f'"{self.ranged_weapon}", ')
        if self.ranged_ammunition_amt is not None:
            outstr = (f'{outstr}"Ranged Ammo": '
                      f'"{self.ranged_ammunition_amt}", ')

        outstr = (f'{outstr}"Raw Ability Array": '
                  f'{self.get_raw_ability_array()}, '
                  f'"Ordered Array": '
                  f'{self.get_numerically_sorted_ability_array()}, '
                  f'"Sort Array": "{self.get_ability_pref_str_array()}", '
                  f'"Nbr Sort Array": {self.ability_array_obj.get_pref_array()}, '
                  f'"Sorted": {self.get_sorted_ability_array()}, ')

        if self.race_obj.languages:
            outstr = f'{outstr}"Languages": ['
            for obj_lang in self.race_obj.languages:
                outstr = f'{outstr} "{obj_lang}", '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}], '

        outstr = f'{outstr}"damage ADJ": {{'

        for pkey, pvalue in sorted(self.damage_adj.items()):
            if len(pvalue) > 2:
                outstr = f'{outstr}"{pkey}": "{pvalue}", '
        if outstr[-2:] == ', ':
            outstr = outstr[:-2]
        outstr = f'{outstr}}}, '

        if self.feature_list:
            outstr = f'{outstr}"feature list": {{'
            for f in self.feature_list:
                outstr = f'{outstr} "{f}", '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}}}, '

        if self.feature_counts:
            outstr = f'{outstr}"feature counts": {{'
            for k in self.feature_counts.keys():
                outstr = f'{outstr} "{k}: {self.feature_counts[k]}", '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}}}, '

        if self.spell_list:
            outstr = f'{outstr}"spell list": {{'
            for key in self.spell_list.keys():
                outstr = f'{outstr} "{key}: {{ '
                for spell_name in self.spell_list[key].keys():
                    outstr = f'{outstr} "{spell_name}: {self.spell_list[key][spell_name]}", '
                if outstr[-2:] == ', ':
                    outstr = f'{outstr[:-2]}}}, '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}}}}}'
        if self.spell_list_bonus_action:
            outstr = f'{outstr}"spell list bonus action": {{'
            for key in self.spell_list_bonus_action.keys():
                outstr = f'{outstr} "{key}: {{ '
                for spell_name in self.spell_list_bonus_action[key].keys():
                    outstr = f'{outstr} "{spell_name}: {self.spell_list_bonus_action[key][spell_name]}", '
                if outstr[-2:] == ', ':
                    outstr = f'{outstr[:-2]}}}, '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}}}}}'
        if self.spell_list_reaction:
            outstr = f'{outstr}"spell list reaction": {{'
            for key in self.spell_list_reaction.keys():
                outstr = f'{outstr} "{key}: {{ '
                for spell_name in self.spell_list_reaction[key].keys():
                    outstr = f'{outstr} "{spell_name}: {self.spell_list_reaction[key][spell_name]}", '
                if outstr[-2:] == ', ':
                    outstr = f'{outstr[:-2]}}}, '
            if outstr[-2:] == ', ':
                outstr = outstr[:-2]
            outstr = f'{outstr}}}}}'

        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    logger_name = f'playercharacter_main'
    ctx = Ctx(app_username='pc_class_init', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    logger = RpgLogging(logger_name=logger_name, level_threshold='notset')
    logger.setup_logging(log_dir=ctx.log_file_dir)
    try:

        # a1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='Hill dwarf', level=10)
        # a2 = PlayerCharacter(db=db, ctx=ctx,
        #                     ability_array_str='10,11,12,13,14,15'
        #                     )
        # print(a2)
        # a2.ability_array_obj.set_preference_array(pref_array=string_to_array(
        #                                        '5,0,2,1,4,3'
        #                                        ))
        # a5 = PlayerCharacter(db=db, ctx=ctx, race_candidate='Hill dwarf', level=10)
        # for i in range(len(a5.get_class_eval())):
        #     for key, value in a5.get_class_eval()[i].items():
        #         print(f"{i} -- {str(key).ljust(25)}: {value}")
        #
        # a6 = PlayerCharacter(db=db, ctx=ctx,
        #                      ability_array_str="18,12,12,10,10,8",
        #                      race_candidate="Mountain Dwarf",
        #                      class_candidate="Barbarian")

        # attack_obj = a5.default_melee_attack(target_name_str=a6.get_name())
        # a6.defend(attack_obj=attack_obj)
        # a6.heal(amount=10)
        # attack_obj = a5.default_melee_attack(target_name_str=a6.get_name())
        # a6.defend(attack_obj=attack_obj)
        # a6.heal(amount=30)
        # t_a1 = a5.default_melee_attack(a6.get_name())
        # a6.defend(attack_obj=t_a1)

        # a7 = PlayerCharacter(db=db, ctx=ctx,
        #                      ability_array_str="6,6,6,6,6,6",
        #                      race_candidate="Half-Orc",
        #                      class_candidate="Barbarian")

        # a20 = PlayerCharacter(db=db, ctx=ctx,
        #                       ability_array_str="10,13,13,10,17,10",
        #                       race_candidate="Wood elf",
        #                       class_candidate="Cleric")
        # print(a20.__repr__)

        a21 = PlayerCharacter(db=db, ctx=ctx,
                              ability_array_str="11,14,14,13,13,12",
                              race_candidate="Tiefling",
                              class_candidate="Rogue",
                              level=3)
        print(a21.__repr__)
        print(f"Bonus Action Spell List: {a21.spell_list_bonus_action}")
        print(f"Action Spell List: {a21.spell_list_action}")
        print(f"Reaction Spell List: {a21.spell_list_reaction}")
        print(f"Spell List: {a21.spell_list}")

        a22 = PlayerCharacter(db=db, ctx=ctx,
                              ability_array_str="13,13,13,13,13,13",
                              # race_candidate="Half-elf",
                              race_candidate="Tiefling",
                              class_candidate="Bard",
                              level=3)
        print(a22.__repr__)
        print(f"Bonus Action Spell List: {a22.spell_list_bonus_action}")
        print(f"Action Spell List: {a22.spell_list_action}")
        print(f"Reaction Spell List: {a22.spell_list_reaction}")
        print(f"Spell List: {a22.spell_list}")

        a22 = PlayerCharacter(db=db, ctx=ctx,
                              ability_array_str="Common",
                              race_candidate="Wood elf",
                              class_candidate="Cleric")
        print(a22.__repr__)

        # a8 = PlayerCharacter(db=db, ctx=ctx,
        #                      ability_array_str="18,12,12,10,10,8",
        #                      race_candidate="Copper dragonborn",
        #                      class_candidate="Barbarian")
        # print(a8.__repr__)

        # a9 = PlayerCharacter(db=db, ctx=ctx,
        #                      ability_array_str="18,12,12,10,10,8",
        #                      race_candidate="High elf",
        #                      class_candidate="Sorcerer")
        # print(a9.__repr__)
        # print(a9)

        # a10 = PlayerCharacter(db=db, ctx=ctx,
        #                       ability_array_str="18,12,12,10,10,8",
        #                       race_candidate="Loredrake kobold",
        #                       class_candidate="Rogue")
        # print(a10.__repr__)

        # dist_target = distanceTarget(distance=20, x=1, y=4, occupied_by_group='Opponents',
        #                              occupied_by_index=0, in_need=False)
        # dist_target_2 = distanceTarget(distance=0, x=1, y=1, occupied_by_group='Heroes',
        #                                occupied_by_index=0, in_need=False)
        # d1 = distanceFromPlayer(player_name=a9.get_name(), player_group='Heroes', player_index=0, x=1, y=1,
        #                         targets=[dist_target],
        #                         ranged_targets=[dist_target], touch_range_chums=[],
        #                         touch_range_chums_in_need=[], touch_range_targets=[], chums=[dist_target_2])
        # action = a9.get_action(d1)
        # print(d1)
        # print(f"Action for {a9.get_name()}: {action}")
        # print(a9.feature_obj)
        # print(a9.available_spell_slots)

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ctx.summary()
        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print(line)
