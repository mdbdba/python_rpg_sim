import random
import sys
import traceback
from InvokePSQL import InvokePSQL
#  Others typing: List, Set, Tuple, Optional
from typing import Dict
from Party import Party
from Foe import Foe
from Encounter import Encounter
from TraceIt import TraceIt
from SeriesStats import SeriesStats
# from EncounterStats import EncounterStats
from CharacterStats import CharacterStats

from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging


class Series(object):
    @ctx_decorator
    def __init__(self, db: InvokePSQL, ctx: Ctx,
                 series_id: int,
                 study_instance_id: int,
                 encounter_repetitions: int,
                 encounter_param_dict: Dict,
                 tracer: TraceIt,
                 debug_ind: int = 0):
        self.db = db
        self.study_instance_id = study_instance_id
        self.series_id = series_id
        self.stats = SeriesStats(study_instance_id=self.study_instance_id, series_id=self.series_id)
        self.t = tracer
        self.encounter_repetitions = encounter_repetitions
        self.encounter_param_dict = encounter_param_dict
        self.party_name_param = None
        self.heroes = []
        self.hero_party_size_param = None
        self.opponent_party_size_param = None
        self.opponents = []
        self.debug_ind_param = debug_ind
        self.debug_ind = debug_ind
        self.series_stats = []
        self.encounter_stats = []
        self.character_stats = []
        self.assign_encounter_params(ctx=ctx)
        print(f"study_instance_id={study_instance_id} " 
              f"series_id={self.series_id} "
              f"encounter_repetitions={encounter_repetitions} "
              f"encounter_param_dict={encounter_param_dict} "
              f"debug_ind={debug_ind}")
        self.run_series(ctx=ctx)

    @ctx_decorator
    def assign_encounter_params(self, ctx):
        if 'party_name' in self.encounter_param_dict.keys():
            self.party_name_param = self.encounter_param_dict['party_name']
        if 'hero_party_size' in self.encounter_param_dict.keys():
            self.hero_party_size_param = self.encounter_param_dict['hero_party_size']
        if 'opponent_party_size' in self.encounter_param_dict.keys():
            self.opponent_party_size_param = self.encounter_param_dict['opponent_party_size']
        if 'opponent_candidate' in self.encounter_param_dict.keys():
            self.opponent_candidate_param = self.encounter_param_dict['opponent_candidate']
        if 'debug_ind' in self.encounter_param_dict.keys():
            self.debug_ind_param = self.encounter_param_dict['debug_ind']

    @ctx_decorator
    def get_named_party(self, ctx):
        p = []
        sql = f"select count(name) from dnd_5e.party where name = '{self.party_name_param}'"
        res = self.db.query(sql)
        hero_party_size = int(res[0][0])
        if hero_party_size == 0:
            raise Exception(f'Party {self.party_name_param} could not be found.')
        full_party = Party(db=self.db, ctx=ctx, name=self.party_name_param, debug_ind=self.debug_ind_param)
        for tmp_char in full_party.get_party():
            p.append(tmp_char)
        return p

    @ctx_decorator
    def get_foes(self, ctx):
        f = []

        for opponent_counter in range(int(self.opponent_party_size_param)):
            if self.opponent_candidate_param:
                show_counter = opponent_counter + 1
                t_name = f"{self.opponent_candidate_param}({show_counter})"
            else:
                t_name = None
            f.append(Foe(db=self.db, ctx=ctx,
                         foe_candidate=self.opponent_candidate_param,
                         foe_name=t_name,
                         debug_ind=self.debug_ind_param))
        return f

    @ctx_decorator
    def run_series(self, ctx):
        for series_counter in range(self.encounter_repetitions):
            display_repetition = series_counter + 1
            print(f"Encounter Repetition: {display_repetition}")
            heroes = self.get_named_party(ctx=ctx)
            opponents = self.get_foes(ctx=ctx)
            for Hero in heroes:
                print(f"  {Hero.get_name()}")
            print(f"Against:")
            for Opponent in opponents:
                print(f"  {Opponent.get_name()}")
            e = Encounter(ctx=ctx,
                          heroes=heroes,
                          opponents=opponents,
                          debug_ind=self.debug_ind_param,
                          tracer=self.t.tracer,
                          study_instance_id=self.study_instance_id,
                          series_id=self.series_id,
                          encounter_id=series_counter)
            # t_encounter_stats.winning_team = e.winning_list_name
            # t_encounter_stats.duration = e.round
            self.encounter_stats.append(e.get_encounter_stats())
            print(f"The winning party was: {e.winning_list_name} in {e.round} rounds.")
            print(f"The surviving {e.winning_list_name} members:")
            for i in range(len(e.winning_list)):
                if e.winning_list[i].alive:
                    print(f'{e.winning_list[i].get_name()}')
            print(f"Character damage info:")
            for Hero in heroes:
                t_char_stats = CharacterStats(study_instance_id=self.study_instance_id,
                                              series_id=self.series_id,
                                              encounter_id=series_counter,
                                              character_id=Hero.character_id,
                                              character_name=Hero.get_name(),
                                              character_class=Hero.get_class(),
                                              character_race=Hero.get_race(),
                                              character_level=Hero.level,
                                              attack_rolls= Hero.attack_rolls,
                                              attack_attempts=Hero.attack_roll_count,
                                              attack_successes=Hero.attack_success_count,
                                              attack_nat20_count=Hero.attack_roll_nat20_count,
                                              attack_nat1_count=Hero.attack_roll_nat1_count,
                                              damage_dealt_dict=Hero.get_damage_dealt(ctx=ctx),
                                              damage_taken_dict=Hero.get_damage_taken(ctx=ctx))

                # t_encounter_stats.heroes.append(t_char_stats)
                t_dict = Hero.get_damage_dealt(ctx=ctx)
                print(f"  {Hero.get_name()} attacks: {Hero.attack_success_count}/{Hero.attack_roll_count}"
                      f" nat20s:{Hero.attack_roll_nat20_count} nat1s: {Hero.attack_roll_nat1_count}")
                print(Hero.attack_rolls)
                print(f"  {Hero.get_name()} damage dealt ({t_dict['Total']}): {Hero.get_damage_dealt(ctx=ctx)}")
                t_dict = Hero.get_damage_taken(ctx=ctx)
                print(f"  {Hero.get_name()} damage taken ({t_dict['Total']}): {Hero.get_damage_taken(ctx=ctx)}")
            for Opponent in opponents:
                t_char_stats = CharacterStats(study_instance_id=self.study_instance_id,
                                              series_id=self.series_id,
                                              encounter_id=series_counter,
                                              character_id=-1,
                                              character_name=Opponent.get_name(),
                                              character_class='Foe',
                                              character_race=Opponent.get_race(),
                                              character_level=Opponent.level,
                                              attack_rolls=Opponent.attack_rolls,
                                              attack_attempts=Opponent.attack_roll_count,
                                              attack_successes=Opponent.attack_success_count,
                                              attack_nat20_count=Opponent.attack_roll_nat20_count,
                                              attack_nat1_count=Opponent.attack_roll_nat1_count,
                                              damage_dealt_dict=Opponent.get_damage_dealt(ctx=ctx),
                                              damage_taken_dict=Opponent.get_damage_taken(ctx=ctx)
                                              )
                # t_encounter_stats.opponents.append(t_char_stats)
                t_dict = Opponent.get_damage_dealt(ctx=ctx)
                print(f"  {Opponent.get_name()} attacks: {Opponent.attack_success_count}/{Opponent.attack_roll_count}"
                      f" nat20s: {Opponent.attack_roll_nat20_count} nat1s: {Opponent.attack_roll_nat1_count}")
                print(Opponent.attack_rolls)
                print(f"  {Opponent.get_name()} damage dealt ({t_dict['Total']}): {Opponent.get_damage_dealt(ctx=ctx)}")
                t_dict = Opponent.get_damage_taken(ctx=ctx)
                print(f"  {Opponent.get_name()} damage taken ({t_dict['Total']}): {Opponent.get_damage_taken(ctx=ctx)}")

            print(e.get_characters_stats(ctx=ctx))
            # self.stats.update_totals()

        print(self.stats)


if __name__ == '__main__':
    series_id = random.randrange(0, 100000, 2)
    # logger_name = f'Series: series_main_{series_id}'
    logger_name = f'series_main_{series_id}'
    ctx = Ctx(app_username='series_class_init', logger_name=logger_name)
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging()
    try:
        db = InvokePSQL()
        series_dict = {
            "opponent_party_size": "4",
            "opponent_candidate": "Skeleton",
            "debug_ind": "1",
            "party_name": "AvgJoes_5"
        }

        t = TraceIt("series")

        a1 = Series(db=db, ctx=ctx, series_id=series_id, study_instance_id=1,
                    encounter_repetitions=2,
                    encounter_param_dict=series_dict, tracer=t)

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f'Context Information:\n\t'
              f'App_username:      {ctx.app_username}\n\t'
              f'Full Name:         {ctx.fullyqualified}\n\t'
              f'Logger Name:       {ctx.logger_name}\n\t' 
              f'Trace Id:          {ctx.trace_id}\n\t' 
              f'Study Instance Id: {ctx.study_instance_id}\n\t' 
              f'Study Name:        {ctx.study_name}\n\t' 
              f'Series Id:         {ctx.series_id}\n\t' 
              f'Encounter Id:      {ctx.encounter_id}\n\t' 
              f'Round:             {ctx.round}\n\t' 
              f'Turn:              {ctx.turn}\n')

        for line in ctx.crumbs:
            print(line)

        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print(line)