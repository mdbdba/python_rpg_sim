import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from distanceFromPlayer import distanceTarget # NOQA
from distanceFromPlayer import distanceFromPlayer # NOQA

def mock_distance_from_player(attacker, distance, chum_in_need=False):
    dist_target = distanceTarget(distance=distance, x=1, y=4, occupied_by_group='Opponents',
                                 occupied_by_index=0, in_need=False)
    attacker_dt = distanceTarget(distance=0, x=1, y=1, occupied_by_group='Heroes',
                                   occupied_by_index=0, in_need=False)
    if distance > 8:
        dfp = distanceFromPlayer(player_name=attacker.get_name(), player_group='Heroes',
                                 player_index=0, x=1, y=1, targets=[dist_target],
                                 ranged_targets=[dist_target], touch_range_chums=[attacker_dt],
                                 touch_range_chums_in_need=[], touch_range_targets=[],
                                 chums=[attacker_dt])
    elif chum_in_need:
        dfp = distanceFromPlayer(player_name=attacker.get_name(), player_group='Heroes',
                                 player_index=0, x=1, y=1, targets=[dist_target],
                                 ranged_targets=[], touch_range_chums=[attacker_dt],
                                 touch_range_chums_in_need=[dist_target], touch_range_targets=[],
                                 chums=[attacker_dt])
    else:
        dfp = distanceFromPlayer(player_name=attacker.get_name(), player_group='Heroes',
                                 player_index=0, x=1, y=1, targets=[dist_target],
                                 ranged_targets=[], touch_range_chums=[attacker_dt],
                                 touch_range_chums_in_need=[], touch_range_targets=[dist_target],
                                 chums=[attacker_dt])

    return dfp