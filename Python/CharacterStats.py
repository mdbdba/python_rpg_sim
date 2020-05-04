from dataclasses import dataclass
from dataclasses import field
from typing import Dict   # Others: Set, Tuple, Optional
from typing import List
# from typing import Tuple
from PointInTimeAmount import PointInTime
from PointInTimeAmount import PointInTimeAmount
from PointInTimeAmount import PointInTimeRollAmount
from PointInTimeAmount import PointInTimeAttackRoll
from PointInTimeAmount import PointInTimeDefense


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
    side: str = 'Unknown'
    attack_rolls: List[PointInTimeAttackRoll] = field(default_factory=get_empty_list)
    ranged_attack_attempts: int = 0
    attack_attempts: int = 0
    attack_successes: int = 0
    attack_nat20_count: int = 0
    attack_nat1_count: int = 0
    healing_received: List[PointInTimeAmount] = field(default_factory=get_empty_list)
    total_healing_received: int = 0
    unconscious_list: List[PointInTime] = field(default_factory=get_empty_list)
    death_list: List[PointInTime] = field(default_factory=get_empty_list)
    defense_rolls: List[PointInTimeDefense] = field(default_factory=get_empty_list)
    defense_attempts: int = 0
    defense_successes: int = 0
    defense_nat20_count: int = 0
    defense_nat1_count: int = 0
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

    def print_character_stats(self, primary_delimiter=": ", secondary_delimiter=", "):
        length_to_strip = (len(secondary_delimiter) * -1)
        header = (f"study_instance_id{primary_delimiter}{self.study_instance_id}{secondary_delimiter}"
                  f" series_id{primary_delimiter}{self.series_id}{secondary_delimiter}"
                  f" encounter_id{primary_delimiter}{self.encounter_id}{secondary_delimiter}"
                  f" side{primary_delimiter}{self.side}")
        print(header)
        print(f"character_name{primary_delimiter}{self.character_name}{secondary_delimiter}"
              f"character_id{primary_delimiter}{self.character_id}")
        t_msg = (f"character_race{primary_delimiter}{self.character_race}{secondary_delimiter}"
                 f"character_class{primary_delimiter}: {self.character_class}{secondary_delimiter}"
                 f"lvl{primary_delimiter}{self.character_level}")
        print(t_msg)
        print(f"ranged_attack_attempts{primary_delimiter}{self.ranged_attack_attempts}")
        print(f"attacks{primary_delimiter}{self.attack_successes} / {self.attack_attempts}")
        for u in self.attack_rolls:
            print(f"\trd{primary_delimiter}{u.round}{secondary_delimiter}"
                  f"turn{primary_delimiter}{u.turn}{secondary_delimiter}"
                  f"type{primary_delimiter}{u.attack_type}{secondary_delimiter}"
                  f"attacker{primary_delimiter}{u.attacker_name}{secondary_delimiter}"
                  f"target{primary_delimiter}{u.target_name}{secondary_delimiter}"
                  f"base_roll{primary_delimiter}{u.base_roll}{secondary_delimiter}"
                  f"adjustments{primary_delimiter}{u.adjustment_values}")

        print(f"attack_nat20_count{primary_delimiter}{self.attack_nat20_count}{secondary_delimiter}"
              f"attack_nat1_count{primary_delimiter}{self.attack_nat1_count}")
        print(f"total_healing_received{primary_delimiter}{self.total_healing_received}"
              f"{secondary_delimiter}{self.healing_received}")
        print(f"defense{primary_delimiter}{self.defense_successes} / {self.defense_attempts}")
        for u in self.defense_rolls:
            print(f"\trd{primary_delimiter}{u.round}{secondary_delimiter}"
                  f"turn{primary_delimiter}{u.turn}{secondary_delimiter}"
                  f"type{primary_delimiter}{u.attack_type}{secondary_delimiter}"
                  f"attacker{primary_delimiter}{u.attacker_name}{secondary_delimiter}"
                  f"target{primary_delimiter}{u.target_name}{secondary_delimiter}"
                  f"attack_value{primary_delimiter}{u.attack_value}{secondary_delimiter}"
                  f"armor_class{primary_delimiter}{u.armor_class}{secondary_delimiter}"
                  f"damage{primary_delimiter}{u.damage}")

        print(f"defense_nat20_count{primary_delimiter}{self.defense_nat20_count}{secondary_delimiter}" 
              f"defense_nat1_count{primary_delimiter}{self.defense_nat1_count}")
        tmp_str = ''
        for u in self.unconscious_list:
            tmp_str = (f'{tmp_str}(rd{primary_delimiter}{u.round}{secondary_delimiter}' 
                       f'turn{primary_delimiter}{u.turn}){secondary_delimiter}')

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:length_to_strip]
        print(f'knocked_unconscious{primary_delimiter}{tmp_str}')
        # 'unconscious_list': [PointInTime(round=6, turn=1)],
        tmp_str = ''
        for u in self.death_list:
            tmp_str = (f'{tmp_str}(rd{primary_delimiter}{u.round}{secondary_delimiter}'
                       f'turn{primary_delimiter}{u.turn}){secondary_delimiter}')

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:length_to_strip]
        print(f'died{primary_delimiter}{tmp_str}')
        # 'death_list': [PointInTime(round=7, turn=1)],
        tmp_str = ''
        for u in self.damage_dealt_dict.keys():
            if self.damage_dealt_dict[u] > 0:
                tmp_str = f"{tmp_str} {u}{primary_delimiter}{self.damage_dealt_dict[u]}{secondary_delimiter}"

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:length_to_strip]
        print(f'damage_dealt{primary_delimiter}{tmp_str}')
        # 'damage_dealt_dict': {'Acid': 0, 'Bludgeoning': 0, 'Cold': 0, 'Fire': 0, 'Force': 0, 'Ligtning': 0,
        #  'Necrotic': 0,
        #             'Piercing': 0, 'Poison': 0, 'Psychic': 0, 'Radiant': 0, 'Slashing': 0, 'Thunder': 0,
        #             'Total': 0, 'Unknown': 0},
        tmp_str = ''
        for u in self.damage_taken_dict.keys():
            if self.damage_taken_dict[u] > 0:
                tmp_str = f"{tmp_str} {u}{primary_delimiter}{self.damage_taken_dict[u]}{secondary_delimiter}"

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:length_to_strip]
        print(f'damage_taken{primary_delimiter}{tmp_str}')
        # 'damage_taken_dict': {'Acid': 0, 'Bludgeoning': 0, 'Cold': 0, 'Fire': 0, 'Force': 0, 'Ligtning': 0,
        # 'Necrotic': 0,
        #             'Piercing': 30, 'Poison': 0, 'Psychic': 0, 'Radiant': 0, 'Slashing': 0, 'Thunder': 0,
        #             'Total': 30, 'Unknown': 0},
        print(' ')