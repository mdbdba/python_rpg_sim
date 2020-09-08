import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PlayerCharacter import PlayerCharacter    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from CommonFunctions import array_to_string, string_to_array    # NOQA
from CommonFunctions import compare_arrays    # NOQA
from Ctx import Ctx
from distanceFromPlayer import distanceTarget
from distanceFromPlayer import distanceFromPlayer


def test_character_spell_list():
    db = InvokePSQL()
    ctx = Ctx(app_username='character_class_init', logger_name="test_logger")
    a1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='High elf', class_candidate='Sorcerer')
    b1 = PlayerCharacter(db=db, ctx=ctx, race_candidate='Loredrake kobold', class_candidate='Sorcerer')
    assert(a1)
    assert(b1)
    assert(a1.level == 1)
    assert(b1.level == 1)
    dist_target = distanceTarget(distance=20,x=1,y=4,occupied_by_group='Opponents',
                                 occupied_by_index=0, in_need=False)
    dist_target_2 = distanceTarget(distance=0,x=1,y=1,occupied_by_group='Heroes',
                                 occupied_by_index=0, in_need=False)
    d1 = distanceFromPlayer(player_name=a1.get_name(), player_group='Heroes',player_index=0,x=1,y=1,targets=[dist_target],
                            ranged_targets=[dist_target],touch_range_chums=[],
                            touch_range_chums_in_need=[],touch_range_targets=[],chums=[dist_target_2])
    action = a1.get_action(d1)
    print(f"Got Action {action} back")
    assert(action['Action'] == 'Spell')
    assert(action['Specific_Name'] == 'Toll the Dead')
    assert(action['Targets'][0].occupied_by_group == 'Opponents')
    assert(action['Targets'][0].occupied_by_index == 0)
