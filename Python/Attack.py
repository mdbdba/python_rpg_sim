from Die import Die
from Ctx import Ctx
from Ctx import ctx_decorator


class Attack(object):
    @ctx_decorator
    def __init__(self, ctx: Ctx, weapon_obj,
                 attack_modifier,  # bonus to the toHit
                 damage_modifier,
                 encounter_round,
                 encounter_turn,
                 attacker_name,
                 target_name,
                 attack_type,
                 versatile_use_2handed=True,
                 vantage='Normal'):
        self.ctx = ctx
        self.method_last_call_audit = {}
        self.weapon_obj = weapon_obj
        self.weapon_name = weapon_obj.name
        self.damage_type = weapon_obj.default_damage_type
        self.encounter_round = encounter_round
        self.encounter_turn = encounter_turn
        self.attacker_name = attacker_name
        self.target_name = target_name
        self.attack_type = attack_type
        self.attack_modifier = attack_modifier
        self.damage_modifier = damage_modifier
        self.vantage = vantage
        if (self.weapon_obj.versatile_ind is True
                and self.weapon_obj.versatile_2hnd_mod
                and self.weapon_obj.versatile_2hnd_die
                and versatile_use_2handed is True):
            self.versatile_use_2handed = True
        else:
            self.versatile_use_2handed = False
        self.rolls_used = None
        self.die_used = None
        self.possible_damage = self.set_possible_damage()
        self.natural_value = self.roll_attack()
        if self.check_natural_value(20):
            self.possible_damage = self.possible_damage * 2
        self.possible_damage += self.damage_modifier
        self.attack_value = self.natural_value + self.attack_modifier

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

        # print(self.possible_damage)
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

    @ctx_decorator
    def set_possible_damage(self):
        total = 0
        # print(self.weapon_obj.damage_dict.items())
        for key, value in self.weapon_obj.damage_dict.items():
            if value[0] == 1 and self.versatile_use_2handed is True:
                d = Die(ctx=self.ctx, sides=self.weapon_obj.versatile_2hnd_die)
                self.die_used = self.weapon_obj.versatile_2hnd_die
                self.rolls_used = self.weapon_obj.versatile_2hnd_mod
                total += d.roll(rolls=self.weapon_obj.versatile_2hnd_mod)
            else:
                d = Die(ctx=self.ctx, sides=value[2])
                total += d.roll(rolls=value[1])
                self.die_used = value[2]
                self.rolls_used = value[1]
        return total

    def __repr__(self):
        return (f'"method_last_call_audit": {self.method_last_call_audit}, ' 
                f'"weapon_obj": {self.weapon_obj}, ' 
                f'"damage_type":{self.damage_type}, ' 
                f'"attack_modifier":{self.attack_modifier}, ' 
                f'"damage_modifier":{self.damage_modifier}, ' 
                f'"vantage":{self.vantage}, ' 
                f'"versatile_use_2handed":{self.versatile_use_2handed}, ' 
                f'"rolls_used":{self.rolls_used}, ' 
                f'"die_used":{self.die_used}, ' 
                f'"possible_damage":{self.possible_damage}, ' 
                f'"natural_value":{self.natural_value}, ' 
                f'"possible_damage":{self.possible_damage}, ' 
                f'"attack_value":{self.attack_value}, ')
