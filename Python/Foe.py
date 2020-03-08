import sys
import traceback
from InvokePSQL import InvokePSQL
from Character import Character
from Weapon import Weapon
from Die import Die
from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging

from CommonFunctions import string_to_array


class Foe(Character):
    @ctx_decorator
    def __init__(self,
                 db,
                 ctx: Ctx,
                 foe_name=None,
                 foe_candidate="Random",
                 challenge_level=".25",
                 damage_generator="Random",
                 hit_point_generator="Max"):
        gender_candidate = 'U'
        self.character_id = -1
        self.ctx = ctx
        self.name = foe_name
        ability_array_str = 'Common'
        if foe_candidate == "Random":
            foe_candidate = self.find_random(db=db, challenge_level=challenge_level)
        level = 1   # Player level will always be 1 for Foes
        Character.__init__(self, db=db, ctx=ctx, gender_candidate=gender_candidate,
                           ability_array_str=ability_array_str,
                           damage_generator=damage_generator,
                           hit_point_generator=hit_point_generator,
                           level=level)
        self.get_foe(db=db, foe_candidate=foe_candidate)
        self.stats.character_id = self.character_id
        self.stats.character_class = self.race     # this looks funky, but characterStats presentation for the foe race
        self.stats.character_race = self.foe_type  # is easier to compare using the class as "skeleton" and race as
        # Undead.  Leaving that like that for it.  In all programmatic work the foe race and foe_type will be used.

        if self.melee_weapon is not None:
            self.melee_weapon_obj = Weapon(db=db, ctx=ctx, name=self.get_melee_weapon())
            self.melee_weapon_obj.setWeaponProficient()
        if self.ranged_weapon is not None:
            self.ranged_weapon_obj = Weapon(db=db, ctx=ctx, name=self.get_ranged_weapon())
            self.melee_weapon_obj.setWeaponProficient()

        self.set_damage_adjs(db=db)

        self.class_eval.append({
                       "pythonClass": "Foe",
                       "foe_candidate": foe_candidate,
                       "challenge_level": challenge_level,
                       "damage_generator": damage_generator,
                       "hit_point_generator": hit_point_generator,
                       "level": level})
        self.logger.debug(msg="user_audit", json_dict=self.__dict__, ctx=ctx)

    def get_melee_weapon(self):
        return self.melee_weapon

    def get_ranged_weapon(self):
        if self.ranged_weapon:
            return_val = self.ranged_weapon
        else:
            return_val = "Not_Defined"
        return return_val

    @ctx_decorator
    def default_melee_attack(self, vantage='Normal'):
        return self.melee_attack(weapon_obj=self.melee_weapon_obj, vantage=vantage)

    @ctx_decorator
    def default_ranged_attack(self, vantage='Normal'):
        self.stats.ranged_attack_attempts += 1
        return self.ranged_attack(weapon_obj=self.ranged_weapon_obj, vantage=vantage)

    @ctx_decorator
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

    @ctx_decorator
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
            self.character_id = results[0][0]     # id,
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

    @ctx_decorator
    def set_damage_adjs(self, db):
        sql = (f"select rt.affected_name, rt.affect "
               f"from lu_foe_trait as rt "
               f"join foe as r on rt.foe = r.name "
               f"where rt.category = 'Damage Received' "
               f"and rt.affect is not null "
               f"and rt.affected_name in ('Acid', 'Bludgeoning', "
               f"'Cold', 'Fire', 'Force', 'Ligtning', 'Necrotic',"
               f"'Piercing', 'Poison', 'Psychic', 'Radiant',"
               f"'Slashing', 'Thunder')"
               f"and r.name = '{self.get_race()}' ")

        rows = db.query(sql)
        for row in rows:
            self.damage_adj[row[0]] = row[1]

    @ctx_decorator
    def assign_hit_points(self):
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

        jdict = {
            "hit_point_generator": self.hit_point_generator,
            "hit_point_modifier": self.hit_point_modifier,
            "hit_point_die": self.hit_point_die,
            "hit_point_admustment": self.hit_point_adjustment
        }
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

        return ret_val

    def get_combat_preference(self):
        # TODO: Add a Ranged option
        if self.ranged_weapon:
            return_val = "Mixed"
        else:
            return_val = "Melee"

        return return_val

    def get_racial_traits(self):
        return None

    def get_name(self):
        return self.name

    def get_race(self):
        return self.race

    def get_class(self):
        return self.foe_type

    def get_alignment_str(self):
        return self.alignment

    @ctx_decorator
    def get_alignment_abbrev(self):
        sql = (f"select abbreviation from lu_alignment where value = "
               f"'{self.alignment}';")
        results = self.db.query(sql)

        return results[0][0]

    @ctx_decorator
    def is_not_using_shield(self):
        if self.shield == 'None':
            ret_val = True
        else:
            ret_val = False
        return ret_val

    def __str__(self):
        outstr = (f'{self.__class__.__name__}\n'
                  f'gender: {self.get_gender()}\n'
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

    def __repr__(self):
        outstr = (f'{{ "class": "{self.__class__.__name__}", '
                  f'"gender": "{self.get_gender()}", '
                  f'"name": "{self.get_name()}", '
                  f'"race": "{self.get_race()}", '
                  f'"foe_type": "{self.foe_type}", '
                  f'"size": "{self.size}", '
                  f'"alignment": "{self.get_alignment_str() }", '
                  f'"alignment abbrev": "{self.get_alignment_abbrev() }", '
                  f'"base_walking_speed": "{self.base_walking_speed}", '
                  f'"challenge_level": "{self.challenge_level}", '
                  f'"ability_array_str": "{self.ability_array_str}", '
                  f'"returned ability_array": {self.get_ability_array()}, '
                  f'"ability_modifier_array": "{self.ability_modifier_array }", '
                  f'"hit_point_die": {self.hit_point_die }, '
                  f'"hit_point_modifier": {self.hit_point_modifier }, '
                  f'"hit_point_adjustment": {self.hit_point_adjustment}, '
                  f'"standard_hit_points": {self.standard_hit_points}, '
                  f'"armor_class": {self.armor_class}, '
                  f'"hit_points": {self.hit_points}, '
                  f'"cur_hit_points": {self.cur_hit_points}, '
                  f'"temp_hit_points": {self.temp_hit_points}, '
                  f'"ranged_weapon": "{self.ranged_weapon }", '
                  f'"melee_weapon": "{self.melee_weapon }", '
                  f'"ranged_ammunition_type": "{self.ranged_ammunition_type }", '
                  f'"ranged_ammunition_amt": {self.ranged_ammunition_amt }, '
                  f'"armor": "{self.armor }", '
                  f'"shield": "{self.shield }", '
                  f'"source_material": "{self.source_material }", '
                  f'"source_credit_url": "{self.source_credit_url}", '
                  f'"source_credit_comment": "{self.source_credit_comment}" }}')

        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    logger_name = f'foe_main'
    ctx = Ctx(app_username='foe_class_init', logger_name=logger_name)
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging()
    try:
        a1 = Foe(db=db, ctx=ctx, foe_candidate="Skeleton")
        a2 = Foe(db=db, ctx=ctx, foe_candidate="Skeleton")
        print(a1)
        attack_obj = a2.default_melee_attack()
        a1.defend(attack_obj=attack_obj)
        a1.heal(amount=10)
        attack_obj = a2.default_melee_attack()
        a1.defend(attack_obj=attack_obj)
        print(a1.__repr__())

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f'Context Information:\n\t'
              f'App_username:      {ctx.app_username}\n\t'
              f'Full Name:         {ctx.fullyqualified}\n\t'
              f'Logger Name:       {ctx.logger_name}\n\t' 
              f'Trace Id:          {ctx.trace_id}\n\t' 
              f'Study Instance Id: {ctx.study_instance_id}\n\t' 
              f'Study Name:        {ctx.study_name}\n\t' 
              f'Series Id:         {ctx.series_id}\n\t' 
              f'Encounter Id:      {ctx.encounter_id}\n\t' 
              f'Round:             {ctx.round}\n\t' 
              f'Turn:              {ctx.turn}\n')

        for line in ctx.crumbs:
            print(line)

        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print(line)
