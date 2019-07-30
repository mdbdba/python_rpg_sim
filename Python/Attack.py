from Die import Die


class Attack(object):
    def __init__(self, weapon_obj,
                 attack_modifier,  # bonus to the toHit amt
                 versatile_use_2handed=True,
                 vantage='Normal'):
        self.weapon_obj = weapon_obj
        self.damage_type = weapon_obj.default_damage_type
        self.attack_modifier = attack_modifier
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
        self.attack_value = self.roll_attack() + self.attack_modifier

        # print(self.possible_damage)

    def roll_attack(self):
        d = Die(20)
        if self.vantage == 'Advantage':
            r = d.rollWithAdvantage()
        elif self.vantage == 'Disadvantage':
            r = d.rollWithDisadvantage()
        else:
            r = d.roll()
        return r

    def set_possible_damage(self):
        total = 0
        # print(self.weapon_obj.damage_dict.items())
        for key, value in self.weapon_obj.damage_dict.items():
            if value[0] == 1 and self.versatile_use_2handed is True:
                d = Die(self.weapon_obj.versatile_2hnd_die)
                self.die_used = self.weapon_obj.versatile_2hnd_die
                self.rolls_used = self.weapon_obj.versatile_2hnd_mod
                total += d.roll(self.weapon_obj.versatile_2hnd_mod)
            else:
                d = Die(value[2])
                total += d.roll(value[1])
                self.die_used = value[2]
                self.rolls_used = value[1]
        return total
