import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helper_functions_for_testing import mock_distance_from_player  # NOQA
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

def test_character_spell_list():
    logger_name = 'character_test'
    ctx = Ctx(app_username='character_test', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    db = InvokePSQL()
    b1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='Loredrake kobold', class_candidate='Sorcerer',
                         ability_array_str='10,10,10,10,10,10')
    b1.set_name_str(group_str='Heroes', index_position=1)
    f1 = Foe(db=db, ctx=ctx, foe_candidate='Skeleton')
    f1.set_name_str(group_str='Opponents', index_position=0)
    assert b1
    assert(b1.level == 1)

    d1 = mock_distance_from_player(attacker=b1, distance=20)
    action = b1.get_action(d1)
    assert(b1.get_combat_preference() == 'Ranged')
    assert(action['Action'] == 'Spell')

    assert(action['Specific_Name'] == 'Magic Missile')
    assert(b1.spell_list[action['Specific_Name']]['available_count'] == 1)
    assert(action['Targets'][0].occupied_by_group == 'Opponents')
    assert(action['Targets'][0].occupied_by_index == 0)
    s1 = Spell(db=db, ctx=ctx, name=action['Specific_Name'], cast_at_level=b1.level)
    dc = b1.get_spell_saving_throw_dc(s1.save)
    assert(dc == 10)
    # a1.use_spell(action['Specific_Name'])
