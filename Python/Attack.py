from Die import Die
# from collections import defaultdict
# from Weapon import Weapon    # NOQA
# from Common.InvokePSQL import InvokePSQL    # NOQA


class Attack(object):
    def __init__(self, weaponObj,
                 attackModifier,   # bonus to the toHit amt
                 versatile_use_2handed=True,
                 vantage='Normal'):
        self.weapon_obj = weaponObj
        self.attack_modifier = attackModifier
        self.vantage = vantage
        if   (self.weapon_obj.versatile_ind is True  # NOQA
              and self.weapon_obj.versatile_2hnd_mod
              and self.weapon_obj.versatile_2hnd_die
              and versatile_use_2handed is True):
            self.versatile_use_2handed = True
        else:
            self.versatile_use_2handed = False
        self.rolls_used = None
        self.die_used = None
        self.possible_damage = self.setPossibleDamage()
        self.attack_value = self.rollAttack() + self.attack_modifier

        # print(self.possible_damage)

    def rollAttack(self):
        d = Die(20)
        if (self.vantage == 'Advantage'):
            r = d.rollWithAdvantage()
        elif (self.vantage == 'Disadvantage'):
            r = d.rollWithDisadvantage()
        else:
            r = d.roll()
        return r

    def setPossibleDamage(self):
        total = 0
        # print(self.weapon_obj.damage_dict.items())
        for key, value in self.weapon_obj.damage_dict.items():
            if     (value[0] == 1  # NOQA
                    and self.versatile_use_2handed is True):
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


#  if __name__ == '__main__':
#      d = defaultdict(list)
#      d['Piercing'].append(1)
#      d['Piercing'].append(6)
#      d['Piercing'].append(0)
#      # print(d.items())
#      db = InvokePSQL()
#      a = Weapon(db, 'Club')
#      b = Attack(a, 0)
#      a = Weapon(db, 'Spear')
#      b = Attack(a, 0)
