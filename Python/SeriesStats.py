from dataclasses import dataclass  # , field
# from typing import List   # Others: Dict, Set, Tuple, Optional
from EncounterStats import EncounterStats
from datetime import datetime


def get_empty_list():
    return []


@dataclass
class SeriesStats:
    study_instance_id: int
    series_id: int
    starting_timestamp: datetime = datetime.now()
    update_timestamp: datetime = datetime.now()
    series_heroes_attack_attempts: int = -1
    series_heroes_attack_successes: int = -1
    series_opponents_attack_attempts: int = -1
    series_opponents_attack_successes: int = -1
    series_total_attack_attempts: int = -1
    series_total_attack_successes: int = -1
#    encounters: List[EncounterStats] = field(default_factory=get_empty_list)

    def update_totals(self, encounter_stats: EncounterStats):
        if self.series_heroes_attack_attempts == -1:
            self.series_heroes_attack_attempts = 0
        if self.series_heroes_attack_successes == -1:
            self.series_heroes_attack_successes = 0
        if self.series_opponents_attack_attempts == -1:
            self.series_opponents_attack_attempts = 0
        if self.series_opponents_attack_successes == -1:
            self.series_opponents_attack_successes = 0
        if self.series_total_attack_attempts == -1:
            self.series_total_attack_attempts = 0
        if self.series_total_attack_successes == -1:
            self.series_total_attack_successes = 0
        self.update_timestamp = datetime.now()

        # for encounter in  self.encounters:
        #     encounter.update_totals()
        self.series_heroes_attack_attempts += encounter_stats.heroes_attack_attempts
        self.series_heroes_attack_successes += encounter_stats.heroes_attack_successes
        self.series_opponents_attack_attempts += encounter_stats.opponents_attack_attempts
        self.series_opponents_attack_successes += encounter_stats.opponents_attack_successes
        self.series_total_attack_attempts += encounter_stats.heroes_attack_attempts
        self.series_total_attack_attempts += encounter_stats.opponents_attack_attempts
        self.series_total_attack_successes += encounter_stats.heroes_attack_successes
        self.series_total_attack_successes += encounter_stats.opponents_attack_successes

    def get_dict(self):
        return self.__dict__
    # def __repr__(self):
    #     out_str = (f'"study_instance_id": "{self.study_instance_id}", '
    #                f'"series_id":  "{self.series_id}", '
    #                f'"starting_timestamp": "{str(self.starting_timestamp)}", '
    #                f'"update_timestamp": "{str(self.update_timestamp)}", '
    #                f'"series_heroes_attack_attempts": {self.series_heroes_attack_attempts}, '
    #                f'"series_heroes_attack_successes": {self.series_heroes_attack_successes}, '
    #                f'"series_opponents_attack_attempts": {self.series_opponents_attack_attempts}, '
    #                f'"series_opponents_attack_successes": {self.series_opponents_attack_successes}, '
    #                f'"series_total_attack_attempts": {self.series_total_attack_attempts}, '
    #                f'"series_total_attack_successes": {self.series_total_attack_successes}, ')
    #     return out_str
