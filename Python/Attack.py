from Die import Die
from Ctx import Ctx
from Ctx import ctx_decorator

class Attack(object):
    @ctx_decorator
    def __init__(self, ctx: Ctx, weapon_obj,
                 attack_modifier,  # bonus to the toHit
                 damage_modifier,
                 versatile_use_2handed=True,
                 vantage='Normal'):
        self.weapon_obj = weapon_obj
        self.damage_type = weapon_obj.default_damage_type
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
        self.possible_damage = self.set_possible_damage(ctx=ctx)
        self.natural_value = self.roll_attack(ctx=ctx)
        if self.check_natural_value(20):
            self.possible_damage = self.possible_damage * 2
        self.possible_damage += self.damage_modifier
        self.attack_value = self.natural_value + self.attack_modifier

        # print(self.possible_damage)
    def get_natural_value(self):
        return self.natural_value

    def check_natural_value(self, check_value):
        if self.natural_value == check_value:
            return True
        else:
            return False

    @ctx_decorator
    def roll_attack(self, ctx):
        d = Die(ctx=ctx, sides=20)
        if self.vantage == 'Advantage':
            r = d.roll_with_advantage(ctx=ctx)
        elif self.vantage == 'Disadvantage':
            r = d.roll_with_disadvantage(ctx=ctx)
        else:
            r = d.roll(ctx=ctx)
        return r

    @ctx_decorator
    def set_possible_damage(self, ctx):
        total = 0
        # print(self.weapon_obj.damage_dict.items())
        for key, value in self.weapon_obj.damage_dict.items():
            if value[0] == 1 and self.versatile_use_2handed is True:
                d = Die(ctx=ctx, sides=self.weapon_obj.versatile_2hnd_die)
                self.die_used = self.weapon_obj.versatile_2hnd_die
                self.rolls_used = self.weapon_obj.versatile_2hnd_mod
                total += d.roll(ctx=ctx, rolls=self.weapon_obj.versatile_2hnd_mod)
            else:
                d = Die(ctx=ctx, sides=value[2])
                total += d.roll(ctx=ctx, rolls=value[1])
                self.die_used = value[2]
                self.rolls_used = value[1]
        return total
