import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Attack import Attack    # NOQA
from Weapon import Weapon    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from Ctx import Ctx

def test_Attack_with_Club():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = Weapon(db=db, ctx=ctx, name='Club')
    b = Attack(ctx=ctx, weapon_obj=a, attack_modifier=0, damage_modifier=0)
    assert(b.weapon_obj.name == 'Club')
    assert(b.vantage == 'Normal')
    assert(b.die_used == 4)
    assert(b.rolls_used == 1)
    assert(b.possible_damage > 0 and b.possible_damage <= 4)
    assert(b.attack_value)


def test_Attack_with_Spear():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = Weapon(db=db, ctx=ctx, name='Spear')
    b = Attack(ctx=ctx, weapon_obj=a, attack_modifier=0, damage_modifier=0)
    assert(b.weapon_obj.name == 'Spear')
    assert(b.vantage == 'Normal')
    assert(b.die_used == 8)
    assert(b.rolls_used == 1)
    assert(b.possible_damage > 0 and b.possible_damage <= 8)
    assert(b.attack_value)
