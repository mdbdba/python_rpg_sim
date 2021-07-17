import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Attack import Attack    # NOQA
from Weapon import Weapon    # NOQA
from PlayerCharacter import PlayerCharacter    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from Ctx import Ctx

def test_Attack_with_Club():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = Weapon(db=db, ctx=ctx, name='Club')
    c = PlayerCharacter(ctx=ctx, db=db, race_candidate='Hill dwarf',
                        class_candidate='Fighter', ability_array_str='point_buy_even')
    c.set_name_str(group_str="Heroes",index_position=0)
    d = PlayerCharacter(ctx=ctx, db=db, race_candidate='Hill dwarf',
                        class_candidate='Fighter', ability_array_str='point_buy_even')
    d.set_name_str(group_str="Opponents",index_position=0)
    b = Attack(ctx=ctx, weapon_obj=a, attack_modifier=0,
                     damage_modifier=0,
                     attack_type='Melee', attacker=c,
                     target=d, versatile_use_2handed=False, vantage='Normal')
    assert(b.weapon_obj.name == 'Club')
    assert(b.vantage == 'Normal')
    assert(b.die_used == 4)
    assert(b.rolls_used == 1)
    assert(b.possible_damage > 0 and b.possible_damage <= 6)
    assert(b.attack_value)


def test_Attack_with_Spear():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = Weapon(db=db, ctx=ctx, name='Spear')
    c = PlayerCharacter(ctx=ctx, db=db, race_candidate='Hill dwarf',
                        class_candidate='Fighter', ability_array_str='point_buy_even')
    c.set_name_str(group_str="Heroes",index_position=0)
    d = PlayerCharacter(ctx=ctx, db=db, race_candidate='Hill dwarf',
                        class_candidate='Fighter', ability_array_str='point_buy_even')
    d.set_name_str(group_str="Opponents",index_position=0)
    b = Attack(ctx=ctx, weapon_obj=a, attack_modifier=0,
               damage_modifier=0,
               attack_type='Ranged', attacker=c,
               target=d, versatile_use_2handed=False, vantage='Normal')
    assert(b.weapon_obj.name == 'Spear')
    assert(b.vantage == 'Normal')
    assert(b.die_used == 6)
    assert(b.rolls_used == 1)
    assert(b.possible_damage > 0 and b.possible_damage <= 8)
    assert(b.attack_value)
