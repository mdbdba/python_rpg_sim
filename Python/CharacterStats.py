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

    def print_character_stats(self):
        header = (f"study_instance_id: {self.study_instance_id} |"
                  f" series_id: {self.series_id} |"
                  f" encounter_id: {self.encounter_id} |"
                  f" side: {self.side}")
        print(header)
        print(f"character_name: {self.character_name} character_id: {self.character_id}")
        t_msg = (f"character_race: {self.character_race} character_class: {self.character_class} "
                 f"lvl: {self.character_level}")
        print(t_msg)
        print(f"ranged_attack_attempts: {self.ranged_attack_attempts}")
        print(f"attacks: {self.attack_successes}/{self.attack_attempts}")
        for u in self.attack_rolls:
            print(f"\trd: {u.round}, turn: {u.turn}, type: {u.attack_type}, attacker: {u.attacker_name}, "
                  f"target: {u.target_name}, base_roll: {u.base_roll}, adjustments: {u.adjustment_values}")

        print(f"attack_nat20_count: {self.attack_nat20_count} attack_nat1_count: {self.attack_nat1_count}")
        print(f"total_healing_received: {self.total_healing_received} {self.healing_received}")
        print(f"defense: {self.defense_successes} / {self.defense_attempts}")
        for u in self.defense_rolls:
            print(f"\trd: {u.round}, turn: {u.turn}, type: {u.attack_type}, attacker: {u.attacker_name}, "
                  f"target: {u.target_name}, attack_value: {u.attack_value}, armor_class: {u.armor_class} "
                  f"damage: {u.damage}")

        print(f"defense_nat20_count: {self.defense_nat20_count}")
        print(f"defense_nat1_count: {self.defense_nat1_count}")
        tmp_str = ''
        for u in self.unconscious_list:
            tmp_str = f'{tmp_str}(rd {u.round}, turn: {u.turn}), '

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:-2]
        print(f'knocked_unconscious: {tmp_str}')
        # 'unconscious_list': [PointInTime(round=6, turn=1)],
        tmp_str = ''
        for u in self.death_list:
            tmp_str = f'{tmp_str}(rd {u.round}, turn: {u.turn}), '

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:-2]
        print(f'died: {tmp_str}')
        # 'death_list': [PointInTime(round=7, turn=1)],
        tmp_str = ''
        for u in self.damage_dealt_dict.keys():
            if self.damage_dealt_dict[u] > 0:
                tmp_str = f"{tmp_str} {u}: {self.damage_dealt_dict[u]}, "

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:-2]
        print(f'damage_dealt: {tmp_str}')
        # 'damage_dealt_dict': {'Acid': 0, 'Bludgeoning': 0, 'Cold': 0, 'Fire': 0, 'Force': 0, 'Ligtning': 0,
        #  'Necrotic': 0,
        #             'Piercing': 0, 'Poison': 0, 'Psychic': 0, 'Radiant': 0, 'Slashing': 0, 'Thunder': 0,
        #             'Total': 0, 'Unknown': 0},
        tmp_str = ''
        for u in self.damage_taken_dict.keys():
            if self.damage_taken_dict[u] > 0:
                tmp_str = f"{tmp_str} {u}: {self.damage_taken_dict[u]}, "

        if len(tmp_str) > 2:
            tmp_str = tmp_str[:-2]
        print(f'damage_taken: {tmp_str}')
        # 'damage_taken_dict': {'Acid': 0, 'Bludgeoning': 0, 'Cold': 0, 'Fire': 0, 'Force': 0, 'Ligtning': 0,
        # 'Necrotic': 0,
        #             'Piercing': 30, 'Poison': 0, 'Psychic': 0, 'Radiant': 0, 'Slashing': 0, 'Thunder': 0,
        #             'Total': 30, 'Unknown': 0},
        print(' ')