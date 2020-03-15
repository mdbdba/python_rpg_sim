from dataclasses import dataclass
from dataclasses import field
from typing import List   # Others: Dict, List, Set, Tuple, Optional

def get_empty_list():
    return []

@dataclass
class distanceTarget:
    distance: float
    x: int
    y: int
    occupied_by_group: str
    occupied_by_index: int
    in_melee: bool = False
    used_ranged: bool = False
    in_need: bool = True


@dataclass
class distanceFromPlayer:
    player_name: str
    player_group: str
    player_index: int
    x: int
    y: int
    targets: List[distanceTarget] = field(default_factory=get_empty_list)
    ranged_targets: List[distanceTarget] = field(default_factory=get_empty_list)
    touch_range_chums: List[distanceTarget] = field(default_factory=get_empty_list)
    touch_range_chums_in_need: List[distanceTarget] = field(default_factory=get_empty_list)
    touch_range_targets: List[distanceTarget] = field(default_factory=get_empty_list)
    chums: List[distanceTarget] = field(default_factory=get_empty_list)

    def are_all_targets_in_melee(self):
        if len(self.ranged_targets) == 0:
            return_value = True
        else:
            return_value = False

        return return_value

    def any_touch_range_chums(self):
        if len(self.touch_range_chums) > 0:
            return_value = True
        else:
            return_value = False

        return return_value

    def any_touch_range_chums_in_need(self):
        if len(self.touch_range_chums_in_need) > 0:
            return_value = True
        else:
            return_value = False

        return return_value

    def any_touch_range_targets(self):
        if len(self.touch_range_targets) > 0:
            return_value = True
        else:
            return_value = False

        return return_value
