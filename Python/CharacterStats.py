from dataclasses import dataclass # , field
from typing import Dict, List   # Others: Set, Tuple, Optional

def get_empty_list():
    return []

def get_empty_dict():
    return {}


@dataclass
class CharacterStats:
    study_instance_id: int
    series_id: int
    encounter_id: int
    character_id: int
    character_name: str
    character_class: str
    character_race: str
    character_level: int
    attack_rolls: List = None
    attack_attempts: int = None
    attack_successes: int = None
    attack_nat20_count: int = None
    attack_nat1_count: int = None
    unconscious_list: List  = None   # holds {Round, Turn} list of times character was knocked unconscious
    death_list: List  = None         # holds Round.Turn list of times character was killed.
    defense_rolls: List = None
    damage_dealt_dict: Dict = None
    damage_taken_dict: Dict = None