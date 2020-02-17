from dataclasses import dataclass, field
from typing import Dict, List   # Others: Dict, List, Set, Tuple, Optional
from CommonFunctions import get_random_key


def get_empty_list():
    return []


def get_empty_dict():
    return {}


@dataclass
class PointInTime:
    round: int
    turn: int


@dataclass
class PointInTimeAmount(PointInTime):
    amount: int


@dataclass
class RollAmount:
    die_used: int
    roll_id: str = field(default_factory=get_random_key)
    die_rolls: int = None
    die_total_used: int = None
    base_roll: List[int] = field(default_factory=get_empty_list)
    adjustment_values: Dict = field(default_factory=get_empty_dict)

    def __repr__(self):
        out_str = (f'{{"die_used":  {self.die_used}, '
                   f'"roll_id":  "{self.roll_id}", '
                   f'"die_rolls":  {self.die_rolls}, '
                   f'"die_total_used":  {self.die_total_used}, '
                   f'"base_roll": {self.base_roll}, '
                   '"adjustment_value": {')
        for adj in self.adjustment_values.keys():
            if isinstance(self.adjustment_values[adj], (str, bool)):
                out_str = f'{out_str} "{adj}": "{self.adjustment_values[adj]}", '
            else:
                out_str = f'{out_str} "{adj}": {self.adjustment_values[adj]!r}, '
        if out_str[-2:] == ', ':
            out_str = out_str[:-2]
        out_str = f'{out_str}}}}}'
        return out_str


@dataclass
class DamageAmountPair(RollAmount):
    damage_type: str = None
    amount: int = None


@dataclass
class PointInTimeDamageAmount(PointInTimeAmount):
    damage_values: List[DamageAmountPair] = field(default_factory=get_empty_list)


@dataclass
class PointInTimeRollAmount(PointInTimeAmount):
    base_roll: int = None
    adjustment_values: Dict = field(default_factory=get_empty_dict)


@dataclass
class PointInTimeRollSuccess(PointInTimeRollAmount):
    comparison_value: int = None
    successful_result: bool = None


if __name__ == '__main__':
    roll_details = RollAmount(die_used=6)
    print(roll_details)
