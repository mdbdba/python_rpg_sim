from dataclasses import dataclass  # , field
from typing import List   # Others: Dict, Set, Tuple, Optional
# from CharacterStats import CharacterStats
from datetime import datetime


VALID_ENCOUNTER_SIDES = {'Heroes', 'Opponents'}


def init_char_stats():
    return []


@dataclass
class EncounterStats:
    study_instance_id: int
    series_id: int
    encounter_id: int
    winning_team: str = None
    duration_rds: int = None
    starting_timestamp: datetime = datetime.now()
    update_timestamp: datetime = datetime.now()
    heroes_attack_attempts: int = -1
    heroes_attack_successes: int = -1
    opponents_attack_attempts: int = -1
    opponents_attack_successes: int = -1

#    def update_totals(self, heroes: List, opponents: List):
#        if self.heroes_attack_attempts == -1:
#            self.heroes_attack_attempts = 0
#        if self.heroes_attack_successes == -1:
#            self.heroes_attack_successes = 0
#        if self.opponents_attack_attempts == -1:
#            self.opponents_attack_attempts = 0
#        if self.opponents_attack_successes == -1:
#            self.opponents_attack_successes = 0
#        self.update_timestamp = datetime.now()
#        for hero in heroes:
#            self.heroes_attack_attempts += hero.attack_attempts
#            self.heroes_attack_successes += hero.attack_successes
#        for opponent in opponents:
#            self.opponents_attack_attempts += opponent.attack_attempts
#            self.opponents_attack_successes += opponent.attack_successes

    def inc_attack_attempts(self, encounter_side):
        if encounter_side not in VALID_ENCOUNTER_SIDES:
            raise ValueError(f"encounter_side: {encounter_side} not found.")
        if encounter_side == 'Heroes':
            self.heroes_attack_attempts += 1
        else:
            self.opponents_attack_attempts += 1
        self.update_timestamp = datetime.now()

    def inc_attack_successes(self, encounter_side):
        if encounter_side not in VALID_ENCOUNTER_SIDES:
            raise ValueError(f"encounter_side: {encounter_side} not found.")
        if encounter_side == 'Heroes':
            self.heroes_attack_successes += 1
        else:
            self.opponents_attack_successes += 1
        self.update_timestamp = datetime.now()

    def print_encounter_stats(self, primary_delimiter=": ", secondary_delimiter=", "):
        header = (f"study_instance_id{primary_delimiter}{self.study_instance_id}{secondary_delimiter}"
                  f" series_id{primary_delimiter}{self.series_id}{secondary_delimiter}"
                  f" encounter_id{primary_delimiter}{self.encounter_id}")
        print(header)
        print(f'winning_team{primary_delimiter}{self.winning_team}')
        print(f'duration_rds{primary_delimiter}{self.duration_rds}')
        print(f'starting_timestamp{primary_delimiter}{self.starting_timestamp}')
        print(f'update_timestamp{primary_delimiter}{self.update_timestamp}')
        print(f'heroes_attack_attempts{primary_delimiter}{self.heroes_attack_attempts}')
        print(f'heroes_attack_successes{primary_delimiter}{self.heroes_attack_successes}')
        print(f'opponents_attack_attempts{primary_delimiter}{self.opponents_attack_attempts}')
        print(f'opponents_attack_successes{primary_delimiter}{self.opponents_attack_successes}')
