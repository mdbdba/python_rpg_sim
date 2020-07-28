import os
import sys
import traceback

from InvokePSQL import InvokePSQL
from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging


class Spell(object):
    @ctx_decorator
    def __init__(self, db, ctx, name, cast_at_level=None):
        self.db = db
        self.ctx = ctx
        self.method_last_call_audit = {}
        self.name = name
        self.cast_at_level = cast_at_level
        self.effect_obj = {}
        self.id = None
        self.level = None
        self.save = None
        self.school = None
        self.casting_time_amt = None
        self.casting_time_uom = None
        self.casting_time_note = None
        self.range_amt = None
        self.range_uom = None
        self.range_aoe = None
        self.verbal_component_ind = None
        self.somatic_component_ind = None
        self.material_component_ind = None
        self.material_component_desc = None
        self.duration_amt = None
        self.duration_uom = None
        self.concentration_ind = None
        self.description = None
        self.higher_level_cast = None
        self.attack_roll_required_ind = None
        self.set_properties(self.db)
        self.set_effect(self.db)

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    @ctx_decorator
    def set_properties(self, db):
        sql = (f"select id, level, save, school, casting_time_amt, casting_time_uom, casting_time_note, "
               f"range_amt, range_uom, range_aoe, verbal_component_ind, somatic_component_ind, "
               f"material_component_ind, material_component_desc, duration_amt, duration_uom, concentration_ind, "
               f"description, higher_level_cast, attack_roll_required_ind, save_outcome "
               f"from dnd_5e.lu_spell "
               f"where name = '{self.name}';")
        results = db.query(sql)
        self.id = results[0][0]
        self.level = results[0][1]
        self.save = results[0][2]
        self.school = results[0][3]
        self.casting_time_amt = results[0][4]
        self.casting_time_uom = results[0][5]
        self.casting_time_note = results[0][6]
        self.range_amt = results[0][7]
        self.range_uom = results[0][8]
        self.range_aoe = results[0][9]
        self.verbal_component_ind = results[0][10]
        self.somatic_component_ind = results[0][11]
        self.material_component_ind = results[0][12]
        self.material_component_desc = results[0][13]
        self.duration_amt = results[0][14]
        self.duration_uom = results[0][15]
        self.concentration_ind = results[0][16]
        self.description = results[0][17]
        self.higher_level_cast = results[0][18]
        self.attack_roll_required_ind = results[0][19]
        self.save_outcome = results[0][20]

    @ctx_decorator
    def set_effect(self, db):
        if self.cast_at_level is None:
            if self.level == 0:
                self.cast_at_level = 1
            else:
                self.cast_at_level = self.level
        sql = (f"select spell_id, effect_category, effect_type, effect_modifier, effect_die " 
               f"from v_spell_effect_by_level " 
               f"where spell_name = '{self.name}' "
               f"and {self.cast_at_level} between lower_level and upper_level")
        results = db.query(sql)
        for result in results:
            self.effect_obj[result[2]] = {"spell_id": result[0],
                                          "effect_category": result[1],
                                          "effect_modifier": result[3],
                                          "effect_die": result[4]}

    def __repr__(self):
        out_dict = {
            'name': self.name,
            'cast_at_level': self.cast_at_level,
            'effect_obj': self.effect_obj,
            'id': self.id,
            'level': self.level,
            'save': self.save,
            'school': self.school,
            'casting_time_amt': self.casting_time_amt,
            'casting_time_uom': self.casting_time_uom,
            'casting_time_note': self.casting_time_note,
            'range_amt': self.range_amt,
            'range_uom': self.range_uom,
            'range_aoe': self.range_aoe,
            'verbal_component_ind': self.verbal_component_ind,
            'somatic_component_ind': self.somatic_component_ind,
            'material_component_ind': self.material_component_ind,
            'material_component_desc': self.material_component_desc,
            'duration_amt': self.duration_amt,
            'duration_uom': self.duration_uom,
            'concentration_ind': self.concentration_ind,
            'description': self.description,
            'higher_level_cast': self.higher_level_cast,
            'attack_roll_required_ind': self.attack_roll_required_ind
        }
        return out_dict

    def __str__(self):
        out_str = '{'
        out_dict = self.__repr__()
        for key in out_dict.keys():
             out_str = f"{out_str}'{key}': {out_dict[key]}, "
        if out_str[-2:] == ", ":
            out_str = f'{out_str[:-2]}'
        out_str = f'{out_str}}}'
        return out_str


if __name__ == '__main__':
    db = InvokePSQL()
    logger_name = f'spell_main'
    ctx = Ctx(app_username='spell_class_init', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging(log_dir=ctx.log_file_dir)
    try:
        a1 = Spell(db=db, ctx=ctx,
                   name="Dragonborn Breath Weapon - Blue",
                   cast_at_level=None)
        print(a1)

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
