import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PlayerCharacter import PlayerCharacter    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from CommonFunctions import array_to_string, string_to_array    # NOQA
from CommonFunctions import compare_arrays    # NOQA
from Ctx import Ctx # NOQA
from distanceFromPlayer import distanceTarget # NOQA
from distanceFromPlayer import distanceFromPlayer # NOQA
from Foe import Foe # NOQA
from SpellAction import SpellAction # NOQA
from Spell import Spell # NOQA


def mock_distance_from_player(attacker, distance):
    dist_target = distanceTarget(distance=distance, x=1, y=4, occupied_by_group='Opponents',
                                 occupied_by_index=0, in_need=False)
    dist_target_2 = distanceTarget(distance=0, x=1, y=1, occupied_by_group='Heroes',
                                   occupied_by_index=0, in_need=False)
    return distanceFromPlayer(player_name=attacker.get_name(), player_group='Heroes',
                              player_index=0, x=1, y=1, targets=[dist_target],
                              ranged_targets=[dist_target], touch_range_chums=[],
                              touch_range_chums_in_need=[], touch_range_targets=[],
                              chums=[dist_target_2])


def test_character_spell_list():
    logger_name = 'character_test'
    ctx = Ctx(app_username='character_test', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    db = InvokePSQL()
    a1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='High elf', class_candidate='Sorcerer')
    a1.set_name_str(group_str='Heroes', index_position=0)
    b1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='Loredrake kobold', class_candidate='Sorcerer')
    b1.set_name_str(group_str='Heroes', index_position=1)
    f1 = Foe(db=db, ctx=ctx, foe_candidate='Skeleton')
    f1.set_name_str(group_str='Opponents', index_position=0)
    assert a1
    assert b1
    assert(a1.level == 1)
    assert(b1.level == 1)

    d1 = mock_distance_from_player(attacker=a1, distance=20)
    action = a1.get_action(d1)
    print(f"Got Action {action} back")
    print(a1.spell_list)
    assert(a1.get_combat_preference() == 'Melee')
    assert(action['Action'] == 'Spell')
    assert(action['Specific_Name'] == 'Toll the Dead')
    assert(a1.spell_list[action['Specific_Name']]['available_count'] == -1)
    assert(action['Targets'][0].occupied_by_group == 'Opponents')
    assert(action['Targets'][0].occupied_by_index == 0)
    s1 = Spell(db=db, ctx=ctx, name=action['Specific_Name'], cast_at_level=a1.level)
    dc = a1.get_spell_saving_throw_dc(s1.save)
    a1.use_spell(action['Specific_Name'])
    attack1 = SpellAction(ctx=ctx, spell_obj=s1, attack_modifier=0,
                          damage_modifier=0, caster=a1, save_dc=dc,
                          targets=[f1], vantage='Normal')
    print(attack1)
