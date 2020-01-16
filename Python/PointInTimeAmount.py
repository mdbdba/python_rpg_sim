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
