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
    # heroes: List[CharacterStats] = field(default_factory=init_char_stats)
    # opponents: List[CharacterStats] = field(default_factory=init_char_stats)

    # def update_totals(self):
    #     self.heroes_attack_attempts = 0
    #     self.heroes_attack_successes = 0
    #     self.opponents_attack_attempts = 0
    #     self.opponents_attack_successes = 0
    #     self.update_timestamp = datetime.now()
    #     for hero in self.heroes:
    #         self.heroes_attack_attempts += hero.attack_attempts
    #         self.heroes_attack_successes += hero.attack_successes
    #     for opponent in self.opponents:
    #         self.opponents_attack_attempts += opponent.attack_attempts
    #         self.opponents_attack_successes += opponent.attack_successes
    def update_totals(self, heroes: List, opponents: List):
        if self.heroes_attack_attempts == -1:
            self.heroes_attack_attempts = 0
        if self.heroes_attack_successes == -1:
            self.heroes_attack_successes = 0
        if self.opponents_attack_attempts == -1:
            self.opponents_attack_attempts = 0
        if self.opponents_attack_successes == -1:
            self.opponents_attack_successes = 0
        self.update_timestamp = datetime.now()
        for hero in heroes:
            self.heroes_attack_attempts += hero.attack_attempts
            self.heroes_attack_successes += hero.attack_successes
        for opponent in opponents:
            self.opponents_attack_attempts += opponent.attack_attempts
            self.opponents_attack_successes += opponent.attack_successes

    def inc_attack_attempts(self, encounter_side):
        if encounter_side not in VALID_ENCOUNTER_SIDES:
            raise ValueError(f"encounter_side: {encounter_side} not found.")
        if encounter_side == 'heroes':
            self.heroes_attack_attempts += 1
        else:
            self.opponents_attack_attempts += 1
        self.update_timestamp = datetime.now()

    def inc_attack_successes(self, encounter_side):
        if encounter_side not in VALID_ENCOUNTER_SIDES:
            raise ValueError(f"encounter_side: {encounter_side} not found.")
        if encounter_side == 'heroes':
            self.heroes_attack_successes += 1
        else:
            self.opponents_attack_successes += 1
        self.update_timestamp = datetime.now()
