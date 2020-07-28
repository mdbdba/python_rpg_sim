import os
import sys
import traceback
from InvokePSQL import InvokePSQL
from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging
from Die import Die
from Spell import Spell
from Foe import Foe

class SpellAction(object):
    @ctx_decorator
    def __init__(self, ctx: Ctx, spell_obj,
                 attack_modifier,  # bonus to the toHit
                 damage_modifier,
                 encounter_round,
                 encounter_turn,
                 caster_name,
                 targets,
                 save_dc=None,
                 vantage='Normal'):
        self.ctx = ctx
        self.method_last_call_audit = {}
        self.spell_obj = spell_obj
        self.spell_name = spell_obj.name
        self.effect_obj = spell_obj.effect_obj  # could be damage or healing
        self.encounter_round = encounter_round
        self.encounter_turn = encounter_turn
        self.caster_name = caster_name
        self.targets = targets
        self.attack_modifier = attack_modifier
        self.damage_modifier = damage_modifier
        self.vantage = vantage
        self.set_possible_effect()
        # possible_effect = {"effect_type": {"effect_category": , "possible_amount": ,
        #                                    "effect_modifier": , "die_used": , "rolls_used": ,}}
        self.duration_amt = spell_obj.duration_amt
        self.duration_uom = spell_obj.duration_uom
        self.duration_amt_counter = 0
        if spell_obj.attack_roll_required_ind:
            self.natural_value = self.roll_attack()
            if self.check_natural_value(20):
                for effect_type in self.possible_effect:
                    self.possible_effect[effect_type]['possible_amount'] = (
                            self.possible_effect[effect_type]['possible_amount'] * 2)
            # self.possible_damage += self.damage_modifier
            self.attack_value = self.natural_value + self.attack_modifier
        self.cast_success = None
        self.cast_success_list = []
        self.set_cast_success_list(save_dc)

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    def get_natural_value(self):
        return self.natural_value

    def check_natural_value(self, check_value):
        if self.natural_value == check_value:
            return True
        else:
            return False

    @ctx_decorator
    def roll_attack(self):
        d = Die(ctx=self.ctx, sides=20)
        if self.vantage == 'Advantage':
            r = d.roll_with_advantage()
        elif self.vantage == 'Disadvantage':
            r = d.roll_with_disadvantage()
        else:
            r = d.roll()
        return r

    def set_possible_effect(self):
        # possible_effect = {"effect_type": {"effect_category": , "possible_amount": ,
        #                                    "effect_modifier": , "die_used": , "rolls_used": ,}}
        self.possible_effect = {}
        for effect in self.effect_obj.keys():
            t_obj = self.effect_obj[effect]
            d = Die(ctx=self.ctx, sides=t_obj['effect_die'])
            tmp_rec = {"effect_category": t_obj['effect_category'],
                       "possible_amount": d.roll(rolls=t_obj['effect_modifier']),
                       "die_used": t_obj['effect_die'],
                       "rolls_used": t_obj['effect_modifier']}
            self.possible_effect[effect] = tmp_rec

    @ctx_decorator
    def set_cast_success_list(self, save_dc):
        jdict = {'dc': save_dc,
                 'attack_roll_required_ind': self.spell_obj.attack_roll_required_ind}
        for target in self.targets:
            if self.spell_obj.attack_roll_required_ind:
                jdict[f'{target.get_name()}_armor_class'] = target.armor_class
                jdict['attack_value'] = self.attack_value
                if self.attack_value >= target.armor_class:
                    attack_roll = 'Success'
                else:
                    attack_roll = 'Failure'
            else:
                attack_roll = 'NotRequired'
            jdict[f'{target.get_name()}_attack_roll'] = attack_roll

            if self.spell_obj.save:
                save_success_ind = target.check(self.spell_obj.save, vantage='Normal', dc=save_dc)
            else:
                save_success_ind = False
            jdict[f'{target.get_name()}_save_success_ind'] = save_success_ind

            if attack_roll != 'Failure':
                for effect in self.possible_effect.keys():
                    t_obj = self.possible_effect[effect]
                    if save_success_ind:
                        if self.spell_obj.save_outcome == 'HalfPossible':
                            poss_amt = int(t_obj['possible_amount']/2)
                        elif self.spell_obj.save_outcome == 'ReducedToZero':
                            poss_amt = 0
                        else:
                            poss_amt = -1
                    else:
                        poss_amt = t_obj['possible_amount']

                    jdict[f'{target.get_name()}_{effect}_possible_amount'] = poss_amt
                    if t_obj['effect_category'] == 'damage':
                        jdict[f'{target.get_name()}_{effect}_effect_category'] = 'damage'
                        target.damage(amount=poss_amt, damage_type=effect)
                    else:
                        jdict[f'{target.get_name()}_{effect}_effect_category'] = 'heal'
                        target.heal(amount=poss_amt)
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    def __repr__(self):
        out_dict = {
            'spell_name': self.spell_name,
            'spell_obj':  self.spell_obj,
            'attack_modifier': self.attack_modifier,
            'damage_modifier': self.damage_modifier,
            'effect_obj': self.effect_obj,
            'vantage': self.vantage,
            'encounter_round': self.encounter_round,
            'encounter_turn': self.encounter_turn,
            'caster_name': self.caster_name,
            'targets': self.targets,
            'possible_effect': self.possible_effect,
            'duration_amt': self.duration_amt,
            'duration_uom': self.duration_uom
        }
        return out_dict

    def __str__(self):
        out_str = '{'
        c_dict = self.__repr__()
        for key in c_dict.keys():
            out_str = f"{out_str}'{key}': {c_dict[key]}, "
        if out_str[-2:] == ", ":
            out_str = f'{out_str[:-2]}'
        out_str = f'{out_str}}}'
        return out_str


if __name__ == '__main__':
    db = InvokePSQL()
    logger_name = f'spell_action_main'
    ctx = Ctx(app_username='spell_action_class_init', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging(log_dir=ctx.log_file_dir)
    try:
        s1 = Spell(db=db, ctx=ctx, name="Dragonborn Breath Weapon - Blue", cast_at_level=None)
        f1 = [Foe(db=db, ctx=ctx, foe_candidate="Skeleton"), Foe(db=db, ctx=ctx, foe_candidate="Skeleton")]

        a1 = SpellAction(ctx=ctx,
                         spell_obj=s1,
                         attack_modifier=0,
                         damage_modifier=0,
                         encounter_round=13,
                         encounter_turn=5,
                         caster_name='Bob',
                         save_dc=14,
                         targets=f1,
                         vantage='Normal')
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
