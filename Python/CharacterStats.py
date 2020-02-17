from dataclasses import dataclass
from dataclasses import field
from typing import Dict   # Others: Set, Tuple, Optional
from typing import List
# from typing import Tuple
from PointInTimeAmount import PointInTime
from PointInTimeAmount import PointInTimeAmount
from PointInTimeAmount import PointInTimeRollAmount


def get_empty_list():
    return []


def get_empty_dict():
    return {}


def get_empty_damage_dict():
    return dict(Acid=0, Bludgeoning=0, Cold=0,
                Fire=0, Force=0, Ligtning=0,
                Necrotic=0, Piercing=0, Poison=0,
                Psychic=0, Radiant=0, Slashing=0,
                Thunder=0, Total=0, Unknown=0)


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
    attack_rolls: List[PointInTimeRollAmount] = field(default_factory=get_empty_list)
    attack_attempts: int = None
    attack_successes: int = None
    attack_nat20_count: int = None
    attack_nat1_count: int = None
    healing_received: List[PointInTimeAmount] = field(default_factory=get_empty_list)
    total_healing_received: int = None
    unconscious_list: List[PointInTime] = field(default_factory=get_empty_list)
    death_list: List[PointInTime] = field(default_factory=get_empty_list)
    defense_rolls: List[PointInTimeRollAmount] = field(default_factory=get_empty_list)
    defense_attempts: int = None
    defense_successes: int = None
    defense_nat20_count: int = None
    defense_nat1_count: int = None
    damage_dealt_dict: Dict = field(default_factory=get_empty_damage_dict)
    damage_taken_dict: Dict = field(default_factory=get_empty_damage_dict)

    def append_attack_roll(self, values):
        nat, adj = values
        self.attack_rolls.append(values)
        self.attack_attempts += 1
        if nat == 20:
            self.attack_nat20_count += 1
        if nat == 1:
            self.attack_nat1_count += 1

    def get_attack_rolls(self):
        return self.attack_rolls

    def append_defense_roll(self, values):
        nat, adj = values
        self.defense_rolls.append(values)
        self.defense_attempts += 1
        if nat == 20:
            self.defense_nat20_count += 1
        if nat == 1:
            self.defense_nat1_count += 1

    def get_defense_rolls(self):
        return self.defense_rolls

    def inc_attack_successes(self):
        self.attack_successes += 1

    def inc_defense_successes(self):
        self.defense_successes += 1

    def inc_damage_dealt(self, damage_type, amount):
        self.damage_dealt_dict[damage_type] += amount
        self.damage_dealt_dict['Total'] += amount

    def get_damage_dealt(self):
        return self.damage_dealt_dict

    def inc_damage_taken(self, damage_type, amount):
        self.damage_taken_dict[damage_type] += amount
        self.damage_taken_dict['Total'] += amount

    def get_damage_taken(self):
        return self.damage_taken_dict

    def get_dict(self):
        return self.__dict__
