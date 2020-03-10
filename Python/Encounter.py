import sys
import traceback
import random
import os

from operator import itemgetter

from Fieldsector import Fieldsector
from PlayerCharacter import PlayerCharacter
from Foe import Foe
from CommonFunctions import calculate_distance
from EncounterStats import EncounterStats

from InvokePSQL import InvokePSQL
from TraceIt import TraceIt
from Ctx import RpgLogging
from Ctx import Ctx
from Ctx import ctx_decorator
from PointInTimeAmount import PointInTime


class Encounter(object):
    ctx: Ctx
    logger: RpgLogging
    Heroes: list
    Opponents: list
    winning_list: list
    winning_list_name: str
    field_size: int
    field_map: list
    h_cnt: int
    o_cnt: int

    def __init__(self,
                 ctx: Ctx,
                 heroes,
                 opponents,
                 field_size=100,
                 tracer=None,
                 # study_instance_id=-1,
                 # series_id=-1,
                 encounter_id=-1
                 ):

        self.ctx = ctx
        self.ctx.encounter_id = encounter_id
        self.stats = EncounterStats(study_instance_id=self.ctx.study_instance_id,
                                    series_id=self.ctx.series_id,
                                    encounter_id=encounter_id)

        if not tracer:
            t = TraceIt("encounter")
            self.tracer = t.tracer
        else:
            self.tracer = tracer

        with self.tracer.span(name='encounter'):
            # self.debug_ind = debug_ind
            self.round_summary_filename = f'{ctx.log_file_dir}/{ctx.logger_name}_round_summary.log'
            self.round_summary_file = open(self.round_summary_filename, 'w')
            self.round_audits = []  # keep list with all the activity for the encounter by round.
            self.method_last_call_audit = {}
            self.Heroes = heroes
            self.Opponents = opponents
            self.active = True
            self.ctx.round = 0
            self.ctx.turn = 0
            self.winning_list = []
            self.winning_list_name = ""
            self.logger = RpgLogging(logger_name=ctx.logger_name)
            # initialize the field.
            tot_objs: int = field_size * field_size
            self.field_size = field_size
            self.field_map = [Fieldsector() for bogus_val in range(tot_objs)]

            self.initiative = []   # list of lists to iterate over
            self.melee_with = {}
            self.h_cnt = len(heroes)

            self.summary_entry(f"Let's get ready to rumble!")
            self.summary_entry(f"Encounter: {encounter_id}")
            self.summary_entry("Between:")
            with self.tracer.span(name='build_initiative_list'):
                t_str = ''
                self.h_cnt = len(heroes)
                for position, Hero in enumerate(heroes):
                    self.add_to_initiative_list(src_single=Hero,
                                                source_list_name='Heroes',
                                                source_list_position=position)
                    t_str = f'{t_str}, {position}) {Hero.get_name()}'
                t_str = t_str[2:]
                self.summary_entry(f"\tHeroes ({self.h_cnt}): {t_str}")

                t_str = ''
                self.o_cnt = len(opponents)
                for position, Opponent in enumerate(opponents):
                    self.add_to_initiative_list(src_single=Opponent,
                                                source_list_name='Opponents',
                                                source_list_position=position)
                    t_str = f'{t_str}, {position}) {Opponent.get_name()}'

                t_str = t_str[2:]
                self.summary_entry(f"\tOpponents ({self.o_cnt}): {t_str}")

                self.initiative = sorted(self.initiative, reverse=True,
                                         key=itemgetter(3))
                # init_dict = {}
                # item_count = 0
                # for item in self.initiative:
                #     init_dict[item_count] = self.initiative[item_count]

            self.logger.info(msg="initiative_array", json_dict=self.initiative, ctx=ctx)

            try:
                self.master_loop()
            except:
                raise
            finally:
                self.round_summary_file.close()

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    def get_encounter_stats(self):
        return self.stats

    @ctx_decorator
    def get_characters_stats(self):
        characters_stats_dict = {'Heroes': [], 'Opponents': []}

        for hero in self.Heroes:
            t_id = {"name": hero.get_name(),
                    "side": "Heroes"}
            t_stats = hero.get_character_stats()
            characters_stats_dict['Heroes'].append({**t_id, **t_stats})

        for opponent in self.Opponents:
            t_id = {"name": opponent.get_name(),
                    "side": "Opponents"}
            t_stats = opponent.get_character_stats()
            characters_stats_dict['Opponents'].append({**t_id, **t_stats})

        return characters_stats_dict

    def get_hero_count(self):
        return self.h_cnt

    def get_opponent_count(self):
        return self.o_cnt

    def get_party_list(self, list_name: str):
        if list_name == "Heroes":
            ret_val = self.Heroes
        else:
            ret_val = self.Opponents

        return ret_val

    def get_player(self, list_name: str, list_index: int):
        t = self.get_party_list(list_name)
        return t[list_index]

    def get_grid_position(self, array_index: int) -> tuple:
        ret_val: tuple = divmod(array_index, self.field_size)
        return ret_val

    def get_array_index(self, px: int, py: int) -> int:
        """
        Return the location in the field_size list of an X, Y coordinate.
        """
        ret_val: int = (px * self.field_size) + py
        return ret_val

    def location_eval(self, x_loc, y_loc, bounds_dict):
        if x_loc > bounds_dict['max_x']:
            bounds_dict['max_x'] = x_loc
        if x_loc < bounds_dict['min_x']:
            bounds_dict['min_x'] = x_loc

        if y_loc > bounds_dict['max_y']:
            bounds_dict['max_y'] = y_loc
        if y_loc < bounds_dict['min_y']:
            bounds_dict['min_y'] = y_loc

    def field_snapshot(self):
        divider = "\n---------------------------------------------------------------"
        self.summary_entry(divider)
        display_range_dict = {
            'h': {
                'min_x': self.field_size,
                'min_y': self.field_size,
                'max_x': 0,
                'max_y': 0
            },
            'o': {
                'min_x': self.field_size,
                'min_y': self.field_size,
                'max_x': 0,
                'max_y': 0
            },
            't': {
                'min_x': self.field_size,
                'min_y': self.field_size,
                'max_x': 0,
                'max_y': 0
            },

        }
        location_list = []
        for i in self.initiative:
            if self.get_player(i[0], i[1]).alive:
                if i[0] == "Heroes":
                    self.location_eval(i[4], i[5], display_range_dict['h'])
                else:
                    self.location_eval(i[4], i[5], display_range_dict['o'])
                self.location_eval(i[4], i[5], display_range_dict['t'])
                pid = f"{(i[0])[0]}{i[1]}"
                location_list.append([pid, i[4], i[5], self.get_array_index(i[4], i[5])])

        location_list = sorted(location_list, key=itemgetter(3))

        # print(display_range_dict)
        # print(location_list)

        if (display_range_dict['o']['min_x'] - display_range_dict['h']['max_x']) > 15:
            split_map_ind = True
        else:
            split_map_ind = False

        # x range
        x_header = "|   |"
        x_skip_ids = []
        # x_range_list = []

        if split_map_ind:
            if display_range_dict['h']['min_x'] < 5:
                t_min = display_range_dict['h']['min_x']
            else:
                t_min = display_range_dict['h']['min_x'] - 3

            if display_range_dict['h']['max_x'] > 95:
                t_max = display_range_dict['h']['max_x'] + 1
            else:
                t_max = display_range_dict['h']['max_x'] + 3

            if t_min != 1:
                x_skip_ids.append(t_min)

            x_range_list = list(range(t_min, t_max))

            if display_range_dict['o']['min_x'] < 5:
                t_min = display_range_dict['o']['min_x']
            else:
                t_min = display_range_dict['o']['min_x'] - 3

            if display_range_dict['o']['max_x'] > 95:
                t_max = display_range_dict['o']['max_x'] + 1
            else:
                t_max = display_range_dict['o']['max_x'] + 3

            if t_min != 1:
                x_skip_ids.append(t_min)

            x_range_list = x_range_list + list(range(t_min, t_max))

        else:
            if display_range_dict['t']['min_x'] < 5:
                t_min = display_range_dict['t']['min_x']
            else:
                t_min = display_range_dict['t']['min_x'] - 3

            if display_range_dict['t']['max_x'] > 95:
                t_max = display_range_dict['t']['max_x'] + 1
            else:
                t_max = display_range_dict['t']['max_x'] + 3

            if t_min != 1:
                x_skip_ids.append(t_min)

            x_range_list = list(range(t_min, t_max))

        for i in x_range_list:
            if i in x_skip_ids:
                x_header = f"{x_header}...|"

            if i < 10:
                si = f"0{i} |"
            else:
                si = f"{i} |"
            x_header = f"{x_header}{si}"

        self.summary_entry(x_header)
        # y range

        if display_range_dict['t']['min_y'] < 5:
            t_min = display_range_dict['t']['min_y']
        else:
            t_min = display_range_dict['t']['min_y'] - 3

        if display_range_dict['t']['max_y'] > 95:
            t_max = display_range_dict['t']['max_y']
        else:
            t_max = display_range_dict['t']['max_y'] + 3

        if t_max != 99:
            self.summary_entry("|...|")
        for y in range(t_max, t_min, -1):
            if y < 10:
                si = f"|0{y} |"
            else:
                si = f"|{y} |"

            for x in x_range_list:
                if x in x_skip_ids:
                    si = f"{si}   |"
                found = False
                for p in location_list:
                    if p[1] == x and p[2] == y:
                        si = f"{si}{p[0]} |"
                        found = True
                if not found:
                    si = f"{si}   |"

            self.summary_entry(si)

    def sector_is_unoccupied(self, px: int, py: int) -> bool:
        # with self.tracer.span(name='sector_is_unoccupied'):
        list_index: int = self.get_array_index(px, py)
        ret_val: bool = not self.field_map[list_index].occupied

        if not ret_val:
            jdict = {"field_location": f"[{px}][{py}]",
                     "occupied_by":  self.get_player(self.field_map[list_index].occupied_by,
                                                     self.field_map[list_index].occupied_by_index).get_name()}
            self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return ret_val

    def move(self, identifier_name, identifier_index,
             leave_x, leave_y,
             occupy_x, occupy_y):
        leave_list_ind = self.get_array_index(leave_x, leave_y)
        occupy_list_ind = self.get_array_index(occupy_x, occupy_y)
        self.field_map[leave_list_ind].leave_sector()
        self.field_map[occupy_list_ind].occupy_sector(identifier_name,
                                                      identifier_index)

    @ctx_decorator
    def get_target_distance_array(self, my_x, my_y, target_name):
        # with self.tracer.span(name='get_target_distance_array'):
        dist_list = []
        jdict = {"starting_point": f"[{my_x}][{my_y}]"}
        t_cnt = 1
        for fx in range(len(self.field_map)):
            if self.field_map[fx].occupied and self.field_map[fx].occupied_by == target_name:
                tmp_player = self.get_player(self.field_map[fx].occupied_by,
                                             self.field_map[fx].occupied_by_index)
                t_namestr = (f"{tmp_player.get_name()} {self.field_map[fx].occupied_by}"
                             f" {self.field_map[fx].occupied_by_index}")
                jdict[f"occupied_by_{t_cnt}"] = t_namestr
                if tmp_player.alive:
                    fa, fb = self.get_grid_position(fx)
                    dist = calculate_distance(my_x, my_y, fa, fb)
                    jdict[f"point_{t_cnt}"] = f"[{fa}][{fb}]"
                    jdict[f"distance_{t_cnt}"] = dist
                    dist_list.append([dist, fa, fb, self.field_map[fx].occupied_by,
                                      self.field_map[fx].occupied_by_index])
        dist_list = sorted(dist_list, reverse=False, key=itemgetter(0))
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return dist_list

    @ctx_decorator
    def add_to_initiative_list(self, src_single, source_list_name: str,
                               source_list_position: int):
        with self.tracer.span(name='add_to_initiative_list'):
            pc = src_single.check(skill='Perception', vantage='Normal', dc=10)
            ini = src_single.roll_for_initiative(vantage='Normal')
            field_max = self.field_size - 1

            if source_list_name == 'Heroes':
                map_loc_x = 1
            else:
                map_loc_x = field_max

            if source_list_position == 0:
                map_loc_y = int(field_max/2)
            elif source_list_position % 2 == 0:
                map_loc_y = (int(field_max/2) + int(source_list_position / 2)
                             + (source_list_position % 2 > 0))
            else:
                map_loc_y = (int(field_max/2) - int((source_list_position / 2)
                             + (source_list_position % 2 > 0)))

            pos = self.get_array_index(map_loc_x, map_loc_y)
            self.field_map[pos].occupy_sector(source_list_name,
                                              source_list_position)

            self.initiative.append([source_list_name, source_list_position,
                                    pc, ini,
                                    map_loc_x, map_loc_y])

    def get_player_location(self, list_name: str, list_index: int) -> tuple:
        ret_val: tuple = ()
        for initiative_rec in self.initiative:
            if initiative_rec[0] == list_name and initiative_rec[1] == list_index:
                ret_val = (initiative_rec[4], initiative_rec[5])
                # pos = self.get_array_index(initiative_rec[4], initiative_rec[5])
        return ret_val

    @ctx_decorator
    def remove_player_from_field_by_index(self, list_name: str, list_index: int):
        xy_loc = self.get_player_location(list_name, list_index)
        loc = self.get_array_index(xy_loc[0], xy_loc[1])
        self.field_map[loc].leave_sector()

    @ctx_decorator
    def remove_player_from_field(self, x_loc: int, y_loc: int):
        loc = self.get_array_index(x_loc, y_loc)
        self.field_map[loc].leave_sector()

    def summary_entry(self, msg):
        self.round_summary_file.write(msg)
        self.round_summary_file.write('\n')

    @ctx_decorator
    def master_loop(self):
        self.ctx.round = 1
        self.field_snapshot()
        waiting_for = []

        while self.active:
            self.summary_entry(f"\n* * * * R O U N D  {self.ctx.round} * * * * *")
            turn_audits = []
            with self.tracer.span(name='master_loop_iteration'):
                for i in range(len(self.initiative)):
                    if self.active:
                        self.ctx.turn = i
                        turn_audits.append(self.turn(initiative_ind=i, waiting_for=waiting_for))
                        self.active = self.still_active()

                self.round_audits.append(turn_audits)

                if self.active:
                    self.ctx.round += 1
                    self.field_snapshot()
                else:
                    self.wrap_up()

                if self.ctx.round > 59:
                    self.active = False
                    self.logger.info(msg="last_round_audit", json_dict=turn_audits, ctx=self.ctx)
                    self.logger.info(msg="round_limit_reached.", ctx=self.ctx)

    @ctx_decorator
    def wrap_up(self):
        with self.tracer.span(name='wrap_up'):
            self.logger.info(msg='round_audits', json_dict=self.round_audits, ctx=self.ctx)
            self.stats.winning_team = self.winning_list_name
            self.stats.duration_rds = self.ctx.round
            jdict = {"winner": self.winning_list_name,
                     "result_round": self.ctx.round,
                     "result_turn": self.ctx.turn,
                     "surviving_members": [],
                     "final_field_map": []}
            for i in range(len(self.winning_list)):
                if self.winning_list[i].alive:
                    jdict["surviving_members"].append(self.winning_list[i].get_name())

            for x in range(len(self.field_map)):
                if self.field_map[x].occupied:
                    a, b = self.get_grid_position(x)
                    occupied_loc = [self.get_player(self.field_map[x].occupied_by,
                                    self.field_map[x].occupied_by_index).get_name(),
                                    self.field_map[x].occupied_by, x, a, b]
                    jdict["final_field_map"].append(occupied_loc)
            self.logger.info(msg='encounter_result', json_dict=jdict, ctx=self.ctx)
            self.logger.info(msg='character_stats', json_dict=self.get_characters_stats(), ctx=self.ctx)

    @ctx_decorator
    def still_active(self):
        with self.tracer.span(name='still_active'):
            ret_val = False
            sub_val1 = False
            sub_val2 = False
            if any(Hero.alive for Hero in self.Heroes):
                sub_val1 = True
            if any(Opponent.alive for Opponent in self.Opponents):
                sub_val2 = True

            if sub_val1 and sub_val2:
                ret_val = True
            else:
                if sub_val1:
                    self.winning_list_name = "Heroes"
                    self.winning_list = self.Heroes
                else:
                    self.winning_list_name = "Opponents"
                    self.winning_list = self.Opponents

            return ret_val

    @ctx_decorator
    def cleanup_dead_player(self, player, list_name: str, list_index: int):
        death_rec = PointInTime(self.ctx.round, self.ctx.turn)
        player.stats.death_list.append(death_rec)
        xy_loc = self.get_player_location(list_name=list_name, list_index=list_index)
        x_loc = int(xy_loc[0])
        y_loc = int(xy_loc[1])
        self.remove_all_from_melee_with(player=player)
        self.remove_player_from_field(x_loc=x_loc, y_loc=y_loc)
        for initiative_rec in self.initiative:
            if (initiative_rec[0] == x_loc and
                    initiative_rec[1] == y_loc):
                if len(initiative_rec) > 4:
                    del initiative_rec[5]
                if len(initiative_rec) > 3:
                    del initiative_rec[4]

    def get_name_str(self, side_array_name, side_array_index):
        return (f"{self.get_player(side_array_name, side_array_index).get_name()} "
                f"{side_array_name[0]}{side_array_index}")

    @ctx_decorator
    def turn(self, initiative_ind, waiting_for):
        with self.tracer.span(name='turn'):
            self.summary_entry(f"\n  T U R N  {self.ctx.turn}")
            summary_indent = "    "
            turn_audit = {"round": self.ctx.round, "turn": initiative_ind}
            cur_active = self.get_player(self.initiative[initiative_ind][0],
                                         self.initiative[initiative_ind][1])
            # cur_active_name_str = (f"{cur_active.get_name()} {(self.initiative[initiative_ind][0])[0]}"
            #                        f"{self.initiative[initiative_ind][1]}")
            cur_active_name_str = self.get_name_str(self.initiative[initiative_ind][0],
                                                    self.initiative[initiative_ind][1])
            if self.initiative[initiative_ind][0] == "Heroes":
                target_array_name = "Opponents"
            else:
                target_array_name = "Heroes"

            turn_audit['character'] = cur_active.get_name()
            turn_audit['party_array'] = self.initiative[initiative_ind][0]
            turn_audit['party_array_index'] = self.initiative[initiative_ind][1]

            # print(f"\nRound: {self.ctx.round} turn: {initiative_ind} "
            #       f"Name: {cur_active.get_name()} ({cur_active.cur_hit_points}) "
            #       f"Unconscious: {cur_active.unconscious_ind} "
            #       f"Alive: {cur_active.alive} ")

            self.remove_waiting_for(initiative_ind=initiative_ind, waiting_for=waiting_for)

            if cur_active.alive and cur_active.cur_hit_points > 0:

                dl = (self.get_target_distance_array(my_x=self.initiative[initiative_ind][4],
                                                     my_y=self.initiative[initiative_ind][5],
                                                     target_name=target_array_name))

                turn_audit["closest_opponent_distance"] = dl[0][0]
                turn_audit["target_location"] = f"[{dl[0][1]}][{dl[0][2]}]"
                t_tmp = self.get_player(dl[0][3], dl[0][4])
                turn_audit["target_name"] = t_tmp.get_name()
                target_name_str = self.get_name_str(dl[0][3], dl[0][4])
                msg = (f"{summary_indent}{cur_active_name_str} targeted {target_name_str}"
                       f" {turn_audit['target_location']}, distance: {turn_audit['closest_opponent_distance']}")
                self.summary_entry(msg)

                turn_audit["passed_perception_test"] = self.initiative[initiative_ind][2]
                # Do they know why they are there?
                if not self.initiative[initiative_ind][2]:
                    # bonusaction_used = True
                    self.initiative[initiative_ind][2] = cur_active.check(skill='Perception',
                                                                          vantage='Normal', dc=10)
                    msg = (f"{summary_indent}{cur_active_name_str} used their bonus action to attempt"
                           f" the perception check needed to participate. "
                           f"(Passed: {self.initiative[initiative_ind][2]})")
                    self.summary_entry(msg)
                # Move
                # Define an obj for the current active combatant
                #    0 - How many sectors can they move
                #    1 - Combat preference: 'Ranged' or 'Melee'
                #    2 - X axis location
                #    3 - Y axis location
                avail_mvmt = cur_active.cur_movement / 5

                turn_audit["movement_available"] = avail_mvmt
                turn_audit["combat_preference"] = cur_active.get_combat_preference()
                turn_audit["movement_starting_location"] = (
                    f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")

                dl_in_melee = []
                for p in dl:
                    if self.is_in_melee(self.get_player(p[3], p[4])):
                        q = True
                    else:
                        q = False
                    dl_in_melee.append(q)
                dl_in_ranged = []
                for p in dl:
                    if self.get_player(p[3], p[4]).stats.ranged_attack_attempts > 0:
                        q = True
                    else:
                        q = False
                    dl_in_ranged.append(q)

                avail_mvmt = self.movement(avail_movement=avail_mvmt,
                                           cur_active=cur_active,
                                           cur_init=self.initiative[initiative_ind],
                                           dest_list=dl,
                                           melee_list = dl_in_melee)
                if turn_audit["movement_available"] != avail_mvmt:
                    msg = (f"{summary_indent}{cur_active_name_str} moved from "
                           f"{turn_audit['movement_starting_location']} to "
                           f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")
                else:
                    msg = (f"{summary_indent}{cur_active_name_str} did not move from "
                           f"{turn_audit['movement_starting_location']}")
                self.summary_entry(msg)
                turn_audit["movement_left"] = avail_mvmt
                turn_audit["movement_end_location"] = (
                    f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")
                turn_audit["movement_turn_end_location"] = (
                    f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")

                # Action (Bonus or standard)
                # If they don't have a ranged weapon or spell attack
                # they must be a melee fighter.  When not in melee range
                # use action for movement.
                cur_action = cur_active.get_action(dist_list=dl,
                                                   melee_list=dl_in_melee,
                                                   ranged_list=dl_in_ranged)

                turn_audit['action'] = cur_action
                turn_audit["action_waiting"] = False
                turn_audit["in_melee"] = False
                turn_audit["being_waited_for"] = False
                turn_audit["knocked_unconscious_in_turn"] = False
                turn_audit["died_in_turn"] = False
                turn_audit["target_knocked_unconscious_in_turn"] = False
                turn_audit["target_died_in_turn"] = False
                turn_audit["performed_death_save_in_turn"] = False
                turn_audit["died_before_turn"] = False

                if cur_action == 'Movement':
                    avail_mvmt = cur_active.cur_movement / 5
                    turn_audit["movement_as_action_available"] = avail_mvmt

                    mvmt_from = f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]"

                    avail_mvmt = self.movement(avail_movement=avail_mvmt,
                                               cur_active=cur_active,
                                               cur_init=self.initiative[initiative_ind],
                                               dest_list=dl,
                                               melee_list = dl_in_melee)

                    msg = (f"{summary_indent}{cur_active_name_str} chose movement as their action. "
                           f"Moving from {mvmt_from} to "
                           f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")
                    self.summary_entry(msg)
                    turn_audit["movement_as_action_left"] = avail_mvmt
                    turn_audit["movement_as_action_end_location"] = (
                        f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")
                    turn_audit["movement_turn_end_location"] = (
                        f"[{self.initiative[initiative_ind][4]}][{self.initiative[initiative_ind][5]}]")

                elif cur_action == 'Wait on Melee':
                    # If an enemy gets into melee range this round, ATTACK!
                    t_player_name_str = self.get_name_str(dl[0][3], dl[0][4])
                    msg = (f"{summary_indent}{cur_active_name_str} chose to attack "
                           f"{t_player_name_str} if they come into range later this round.")
                    self.summary_entry(msg)
                    turn_audit["action_waiting"] = True
                    turn_audit["action_waiting_on"] = self.get_player(dl[0][3], dl[0][4]).get_name()

                    waiting_for.append([self.initiative[initiative_ind][0],
                                        self.initiative[initiative_ind][1],
                                        dl[0][3], dl[0][4]])
                elif cur_action == 'Melee':
                    turn_audit["in_melee"] = True
                    turn_audit["in_melee_with"] = self.get_player(dl[0][3], dl[0][4]).get_name()
                    # do any superseding actions
                    s1 = self.get_waiting_for(initiative_ind=initiative_ind, waiting_for=waiting_for)
                    t_cnt = 1
                    for waiting_action in s1:
                        a_x, a_y = self.get_player_location(waiting_action[0], waiting_action[1])
                        t_x, t_y = self.get_player_location(self.initiative[initiative_ind][0],
                                                            self.initiative[initiative_ind][1])
                        waiting_dist = calculate_distance(a_x, a_y, t_x, t_y)
                        directed_user = self.get_player(waiting_action[0], waiting_action[1])
                        attacker_name_str = self.get_name_str(waiting_action[0], waiting_action[1])
                        target_name_str = self.get_name_str(self.initiative[initiative_ind][0],
                                                            self.initiative[initiative_ind][1])
                        turn_audit[f"being_waited_for_{t_cnt}"] = True
                        turn_audit[f"waited_for_by_{t_cnt}"] = directed_user.get_name()
                        msg = f"{summary_indent}{attacker_name_str} was waiting for {target_name_str}"

                        if waiting_dist < 10:
                            self.handle_turn_attack_action(turn_audit=turn_audit,
                                                           attacker_side=waiting_action[0],
                                                           attacker_index=waiting_action[1],
                                                           attack_type='Melee',
                                                           target_side=self.initiative[initiative_ind][0],
                                                           target_index=self.initiative[initiative_ind][1],
                                                           audit_key_prefix="waiting_",
                                                           audit_key_suffix=f"_{t_cnt}")
                        else:
                            msg = f"{msg}, but they were not in range: {waiting_dist}"
                            turn_audit[f"waiting_missed_max_distance_{t_cnt}"] = waiting_dist

                        self.summary_entry(msg)
                        t_cnt += 1
                    if cur_active.cur_hit_points > 0:
                        self.handle_turn_attack_action(turn_audit=turn_audit,
                                                       attacker_side=self.initiative[initiative_ind][0],
                                                       attacker_index=self.initiative[initiative_ind][1],
                                                       attack_type='Melee',
                                                       target_side=dl[0][3], target_index=dl[0][4])
                elif cur_action == 'Ranged':
                    t_range = cur_active.get_ranged_range()
                    turn_audit["ranged_attack"] = True
                    if cur_active.cur_hit_points > 0:
                        m_cnt = 0
                        working_ranged_index = None
                        for m in dl_in_melee:
                            if (working_ranged_index is None and
                                    m is False and
                                    (t_range >= dl[m_cnt][0] > 8)):
                                working_ranged_index = m_cnt
                            m_cnt += 1
                        turn_audit["targeting"] = self.get_player(dl[working_ranged_index][3],
                                                                  dl[working_ranged_index][4]).get_name()
                        self.handle_turn_attack_action(turn_audit=turn_audit,
                                                       attacker_side=self.initiative[initiative_ind][0],
                                                       attacker_index=self.initiative[initiative_ind][1],
                                                       attack_type='Ranged',
                                                       target_side=dl[working_ranged_index][3],
                                                       target_index=dl[working_ranged_index][4])

            elif cur_active.alive:  # currently alive but less than 1 hit point
                t_death_save_passed_cnt = cur_active.death_save_passed_cnt
                cur_active.death_save()
                turn_audit["performed_death_save_in_turn"] = True
                msg = f"{summary_indent}{cur_active_name_str} performed a death save "
                if (t_death_save_passed_cnt > cur_active.death_save_passed_cnt
                        and not cur_active.unconscious_ind):
                    turn_audit["death_save_status"] = "Character Stabilized by death save success."
                    msg = f"{msg} and was stabilized by death save success."
                else:
                    ds_status_str = f"({cur_active.death_save_passed_cnt} / {cur_active.death_save_failed_cnt})"
                    turn_audit["death_save_status"] = ds_status_str
                    msg = f"{msg} {ds_status_str}"
                self.summary_entry(msg)

                if not cur_active.alive:
                    turn_audit["died_in_turn"] = True
                    self.cleanup_dead_player(player=cur_active, list_name=self.initiative[initiative_ind][0],
                                             list_index=self.initiative[initiative_ind][1])
                    msg = f"{summary_indent}{cur_active_name_str} died."
                    self.summary_entry(msg)
            else:
                turn_audit["died_before_turn"] = True
                msg = f"{summary_indent}{cur_active_name_str} died earlier."
                self.summary_entry(msg)

        return turn_audit

    @ctx_decorator
    def handle_turn_attack_action(self, turn_audit, attacker_side, attacker_index, target_side,
                                  target_index, attack_type, audit_key_prefix="", audit_key_suffix=""):
        attacker = self.get_player(attacker_side, attacker_index)
        attacker_name_str = self.get_name_str(attacker_side, attacker_index)
        target = self.get_player(target_side, target_index)
        target_name_str = self.get_name_str(target_side, target_index)
        summary_indent = "    "
        if attacker.cur_hit_points > 0:
            turn_audit[f"{audit_key_prefix}target{audit_key_suffix}"] = target.get_name()

            t_vantage = attacker.get_vantage()
            # if the cur_active user is unconscious then the attack is at advantage
            # and auto-crits on hit.
            if target.unconscious_ind or target.prone_ind:
                if t_vantage == 'Disadvantage':
                    t_vantage = 'Normal'
                else:
                    t_vantage = 'Advantage'
            else:
                t_vantage = 'Normal'

            if attack_type == 'Melee':
                active_attack = attacker.default_melee_attack(vantage=t_vantage)
            else:  # attack_type == 'Ranged':
                active_attack = attacker.default_ranged_attack(vantage=t_vantage)

            msg = (f"with a {attack_type} attack on "
                   f"{target_name_str} using a {active_attack.weapon_name}")
            self.stats.inc_attack_attempts(attacker_side)

            log_if_unconscious = False
            if not target.unconscious_ind:
                log_if_unconscious = True

            hit_points_before = target.cur_hit_points
            successful_defend = target.defend(attack_obj=active_attack)

            random_choice = random.randint(1, 3)  # randomly make the choice to use luck.  1/3 chance
            if (successful_defend and
                    active_attack.natural_value < 20 and  # if a crit failed, there's no way luck would help.
                    attacker.lucky_uses_available > 0 and  # if the attacker has luck, they could try again.
                    random_choice == 1):
                attacker.lucky_uses_available -= 1
                turn_audit[f"{audit_key_prefix}luck_was_used{audit_key_suffix}"] = True
                msg = f"{msg} failed, but lucky caused a retry which"
                if attack_type == 'Melee':
                    active_attack = attacker.default_melee_attack(vantage=t_vantage, luck_retry=True)
                else:  # attack_type == 'Ranged':
                    active_attack = attacker.default_ranged_attack(vantage=t_vantage, luck_retry=True)
                successful_defend = target.defend(attack_obj=active_attack)

            if successful_defend:  # successful defend means the attack failed...
                t_suc = "failed "
            else:
                t_suc = "succeeded "
            msg = f"{summary_indent}{attacker_name_str} {t_suc}{msg}"

            turn_audit[f"{audit_key_prefix}{attack_type}_attack_defense_successful{audit_key_suffix}"] = successful_defend

            hp_impact = (hit_points_before - target.cur_hit_points)
            if not successful_defend:
                turn_audit[f"{audit_key_prefix}{attack_type}_attack_damage{audit_key_suffix}"] = active_attack.possible_damage
                turn_audit[f"{audit_key_prefix}hit_point_impact{audit_key_suffix}"] = hp_impact
                turn_audit[f"{audit_key_prefix}hit_points_after_attack{audit_key_suffix}"] = target.cur_hit_points
                self.stats.inc_attack_successes(attacker_side)
                attacker.inc_damage_dealt(damage_type=active_attack.damage_type,
                                          amount=active_attack.possible_damage)
                attacker.stats.attack_successes += 1

            if target.unconscious_ind:
                if log_if_unconscious:
                    msg = f"{msg} knocking them unconscious"
                    p = PointInTime(self.ctx.round, self.ctx.turn)
                    target.stats.unconscious_list.append(p)
                    turn_audit[f"{audit_key_prefix}target_knocked_unconscious_in_turn{audit_key_suffix}"] = True
                elif not successful_defend:
                    msg = (f"{msg} inflicting two failed death saves " 
                           f"{target.death_save_passed_cnt} / {target.death_save_failed_cnt}")
                    turn_audit[f"{audit_key_prefix}death_save_status{audit_key_suffix}"] = (
                        f"{target.death_save_passed_cnt} / {target.death_save_failed_cnt}")
            else:
                if not successful_defend:
                    msg = f"{msg} for relative damage {hp_impact} HP leaving {target.cur_hit_points} HP"

            if not target.alive:
                msg = f"{msg} killing them"
                turn_audit[f"{audit_key_prefix}target_died_in_turn{audit_key_suffix}"] = True
                self.cleanup_dead_player(player=target, list_name=target_side, list_index=target_index)
        elif target.unconscious_ind:
            msg = (f"{summary_indent}{attacker_name_str} is unconscious. Death saves: " 
                   f"({target.death_save_passed_cnt} / {target.death_save_failed_cnt})")
            turn_audit[f"{audit_key_prefix}death_save_status{audit_key_suffix}"] = (
                f"{target.death_save_passed_cnt} / {target.death_save_failed_cnt}")
        else:
            msg = f"{summary_indent}{attacker_name_str} died earlier"

        self.summary_entry(msg)

    def remove_waiting_for(self, initiative_ind, waiting_for):
        # with self.tracer.span(name='remove_waiting_for'):
        for sublist in waiting_for:
            if (sublist[0] == self.initiative[initiative_ind][0]
                    and sublist[1] == self.initiative[initiative_ind][1]):
                waiting_for.remove(sublist)

    def get_waiting_for(self, initiative_ind, waiting_for):
        ret_val = []
        for sublist in waiting_for:
            if (sublist[2] == self.initiative[initiative_ind][0]
                    and sublist[3] == self.initiative[initiative_ind][1]):
                ret_val.append([sublist[0], sublist[1]])
                waiting_for.remove(sublist)

        return ret_val

    def is_in_melee(self, player):
        if player.get_name() in self.melee_with.keys():
            if len(self.melee_with[player.get_name()]) > 0:
                ret_val = True
            else:
                ret_val = False
        else:
            ret_val = False
        return ret_val

    def get_melee_with(self, player):
        return self.melee_with[player.get_name()]

    @ctx_decorator
    def add_to_melee_with(self, player, the_target_player):
        if player.get_name() in self.melee_with.keys():
            if (any(the_target_player.get_name() in sublist
                    for sublist in self.melee_with[player.get_name()])):
                self.melee_with[player.get_name()].append(the_target_player.get_name())
        else:
            self.melee_with[player.get_name()] = [the_target_player.get_name()]

        if the_target_player.get_name() in self.melee_with.keys():
            if (any(player.get_name() in sublist
                    for sublist in self.melee_with[the_target_player.get_name()])):
                self.melee_with[the_target_player.get_name()].append(player.get_name())
        else:
            self.melee_with[the_target_player.get_name()] = [player.get_name()]

    def remove_all_from_melee_with(self, player):
        # remove all references for this player from melee_with.  Whether key or value
        self.melee_with[player.get_name()] = []
        for subname in self.melee_with.keys():
            if any(player.get_name() in sublist for sublist in self.melee_with[subname]):
                self.melee_with[subname].remove(player.get_name())

    def remove_from_melee_with(self, player, the_target_player):
        if player.get_name() in self.melee_with.keys():
            if (any(the_target_player.get_name() in sublist
                    for sublist in self.melee_with[player.get_name()])):
                self.melee_with[player.get_name()].remove(the_target_player.get_name())

        if the_target_player.get_name() in self.melee_with.keys():
            if (any(player.get_name() in sublist
                    for sublist in self.melee_with[the_target_player.get_name()])):
                self.melee_with[the_target_player.get_name()].remove(player.get_name())

    @ctx_decorator
    def movement(self, avail_movement, cur_active, cur_init, dest_list, melee_list):
        player_combat_preference = cur_active.get_combat_preference()

        jdict = {"character": cur_active.get_name(),
                 "class": cur_active.get_class(),
                 "perception_check_passed": cur_init[2],
                 "player_combat_preference": player_combat_preference}
        # with self.tracer.span(name='movement'):
        if cur_init[2]:     # if they've figured out what's going on.
            op_dist = dest_list[0][0]
            t_range = cur_active.get_ranged_range()
            if cur_active.ranged_ammunition_amt is None:
                ranged_ammunition_amt = 0
            else:
                ranged_ammunition_amt = cur_active.ranged_ammunition_amt

            if (player_combat_preference == 'Mixed'
                    and (op_dist > t_range or
                         ranged_ammunition_amt == 0 or
                         all(melee_list) is True)):  # if all opponents are in melee, move.
                conditional_mvmt = True
            else:
                conditional_mvmt = False

            if (player_combat_preference != 'Melee'
                    and op_dist <= t_range):
                ranged_hold = True
            else:
                ranged_hold = False

            jdict["opponent_distance"] = op_dist
            jdict["ranged_range"] = t_range
            jdict["ranged_ammunition_amt"] = ranged_ammunition_amt
            jdict["conditional_mvmt"] = conditional_mvmt
            jdict["ranged_hold"] = ranged_hold

            player_in_melee = self.is_in_melee(player=cur_active)
            jdict["player_in_melee"] = player_in_melee

            if player_in_melee or ranged_hold:
                # if the character is diagonally positioned,
                # move them so that they are square to the target
                if 10 > dest_list[0][0] > 5:
                    cur_x = int(cur_init[4])
                    cur_y = int(cur_init[5])
                    tgt_x = int(dest_list[0][1])
                    tgt_y = int(dest_list[0][2])
                    # to be lined up, either the x or y point need to match
                    # and the other would be different by 1.
                    # since we know these are diagonal, swapping x or y
                    # should get us two spots to check.
                    coordinates_to_use = []
                    if self.sector_is_unoccupied(px=cur_x, py=tgt_y):
                        coordinates_to_use.append(cur_x)
                        coordinates_to_use.append(tgt_y)
                    elif self.sector_is_unoccupied(px=tgt_x, py=cur_y):
                        coordinates_to_use.append(tgt_x)
                        coordinates_to_use.append(cur_y)
                    if len(coordinates_to_use) > 0:
                        self.move(identifier_name=cur_init[0], identifier_index=cur_init[1],
                                  leave_x=cur_x, leave_y=cur_y,
                                  occupy_x=coordinates_to_use[0],
                                  occupy_y=coordinates_to_use[1])
                        cur_x = coordinates_to_use[0]
                        cur_y = coordinates_to_use[1]
                        avail_movement -= 1
                        dest_list[0][0] = calculate_distance(
                            cur_x, cur_y, tgt_x, tgt_y)
                        cur_init[4] = cur_x
                        cur_init[5] = cur_y
                        self.add_to_melee_with(player=cur_active,
                                               the_target_player=self.get_player(dest_list[0][3],
                                                                                 dest_list[0][4]))

            else:
                cur_x = int(cur_init[4])
                cur_y = int(cur_init[5])

                if player_combat_preference == 'Melee' or conditional_mvmt:
                    # run straight towards closest enemy
                    # set destination x and y
                    dest_x = int(dest_list[0][1])
                    dest_y = int(dest_list[0][2])
                else:
                    # try to stay in ranged range distance.
                    # set destination x and y
                    t_x = int(dest_list[0][1])
                    t_dist_x = t_x - cur_x
                    abs_t_dist_x = abs(t_dist_x)
                    if abs_t_dist_x < 12:
                        dest_x = int(dest_list[0][1])
                    else:
                        t_dir_x = 1 if (t_dist_x >= 0) else -1
                        dest_x = t_x + (t_dir_x * t_range)
                    dest_y = int(dest_list[0][2])

                if avail_movement > 0 and dest_list[0][0] > 5:
                    mvmt = True
                else:
                    mvmt = False

                while mvmt:
                    dist_x = dest_x - cur_x
                    dir_x = 1 if (dist_x >= 0) else -1
                    abs_dist_x = abs(dist_x)

                    dist_y = dest_y - cur_y
                    dir_y = 1 if (dist_y >= 0) else -1
                    abs_dist_y = abs(dist_y)

                    pref_ang_axis = ''
                    pref_ang_dist = 0

                    if dist_x == 0 and dist_y == 0:
                        mvmt = False
                    elif abs_dist_x <= 1 and abs_dist_y <= 1:
                        self.add_to_melee_with(player=cur_active,
                                               the_target_player=self.get_player(dest_list[0][3], dest_list[0][4]))
                        mvmt = False
                    elif abs_dist_x > abs_dist_y:
                        pref_ang_axis = 'Y'
                        pref_ang_dist = dist_y
                    else:
                        pref_ang_axis = 'X'
                        pref_ang_dist = dist_x

                    if mvmt:
                        tl_x = [-1, -1, -1]
                        tl_y = [-1, -1, -1]
                        if pref_ang_dist == 0:
                            if pref_ang_axis == 'X':
                                tl_x[0] = cur_x
                                tl_x[1] = cur_x + 1
                                tl_x[2] = cur_x - 1
                                tl_y[0] = cur_y + dir_y
                                tl_y[1] = cur_y + dir_y
                                tl_y[2] = cur_y + dir_y
                            else:
                                tl_x[0] = cur_x + dir_x
                                tl_x[1] = cur_x + dir_x
                                tl_x[2] = cur_x + dir_x
                                tl_y[0] = cur_y
                                tl_y[1] = cur_y + 1
                                tl_y[2] = cur_y - 1
                        else:
                            tmp_x = cur_x + dir_x
                            tmp_y = cur_y + dir_y
                            if pref_ang_axis == 'X':
                                tl_x[0] = tmp_x
                                tl_x[1] = cur_x
                                tl_x[2] = tmp_x
                                tl_y[0] = tmp_y
                                tl_y[1] = tmp_y
                                tl_y[2] = cur_y
                            else:
                                tl_x[0] = tmp_x
                                tl_x[1] = tmp_x
                                tl_x[2] = cur_x
                                tl_y[0] = tmp_y
                                tl_y[1] = cur_y
                                tl_y[2] = tmp_y

                        move_success = False
                        for pi in range(3):
                            if self.sector_is_unoccupied(px=tl_x[pi], py=tl_y[pi]):
                                self.move(identifier_name=cur_init[0], identifier_index=cur_init[1],
                                          leave_x=cur_x, leave_y=cur_y,
                                          occupy_x=tl_x[pi], occupy_y=tl_y[pi])
                                cur_x = tl_x[pi]
                                cur_y = tl_y[pi]
                                avail_movement -= 1
                                mvmt = False if (avail_movement == 0) else True
                                dest_list[0][0] = calculate_distance(
                                                    cur_x, cur_y, dest_x, dest_y)
                                move_success = True
                                break

                        if move_success:
                            cur_init[4] = cur_x
                            cur_init[5] = cur_y
                        else:
                            mvmt = False

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)
        return avail_movement


if __name__ == '__main__':
    logger_name = 'encounter_main_test'
    ctx = Ctx(app_username='encounter_class_init', logger_name=logger_name)
    ctx.log_file_dir = os.path.expanduser('~/rpg/logs')
    logger = RpgLogging(logger_name=logger_name, level_threshold='info')
    logger.setup_logging(log_dir=ctx.log_file_dir)
    try:
        db = InvokePSQL()
        Heroes = []
        Opponents = []
        Heroes.append(PlayerCharacter(db=db, ctx=ctx, race_candidate='Half-orc'))
        # Heroes.append(PlayerCharacter(db=db, ctx=ctx, class_candidate='Rogue'))
        Heroes.append(PlayerCharacter(db=db, ctx=ctx, class_candidate='Ranger'))
        Opponents.append(Foe(db=db, ctx=ctx, foe_candidate='Skeleton'))
        Opponents.append(Foe(db=db, ctx=ctx, foe_candidate='Skeleton'))
        e1 = Encounter(ctx=ctx, heroes=Heroes, opponents=Opponents)
        print(f"The winning party was: {e1.winning_list_name} in {e1.ctx.round} rounds.")
        print(f"The surviving {e1.winning_list_name} members:")
        for i in range(len(e1.winning_list)):
            if e1.winning_list[i].alive:
                print(f'{e1.winning_list[i].get_name()}')

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(ctx)
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
            print(f'\tclass:        {line.className}\n\t' 
                  f'method:       {line.methodName}\n\t'
                  f'timestamp:    {line.timestamp}\n')
            for mhd in line.methodParams.keys():
                if mhd != 'ctx':
                    print(f'{mhd}: {line.methodParams[mhd]}')

        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print(line)
