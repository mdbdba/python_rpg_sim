
# import logging

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


class Encounter(object):
    ctx: Ctx
    logger: RpgLogging
    Heroes: list
    Opponents: list
    winning_list: list
    winning_list_name: str
    debug_ind: int
    field_size: int
    field_map: list
    h_cnt: int
    o_cnt: int

    def __init__(self,
                 ctx: Ctx,
                 heroes,
                 opponents,
                 field_size=100,
                 debug_ind=0,
                 tracer=None,
                 study_instance_id=-1,
                 series_id=-1,
                 encounter_id=-1
                 ):

        self.stats = EncounterStats(study_instance_id=study_instance_id,
                                    series_id=series_id,
                                    encounter_id=encounter_id)

        if not tracer:
            t = TraceIt("encounter")
            self.tracer = t.tracer
        else:
            self.tracer = tracer

        with self.tracer.span(name='encounter'):
            self.ctx = ctx
            self.debug_ind = debug_ind
            self.Heroes = heroes
            self.Opponents = opponents
            self.active = True
            self.round = 0
            self.winning_list = []
            self.winning_list_name = ""
            # if ((self.debug_ind == 1) and
            #    ((getattr(self, "logger", None)) is None)):
            #     log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
            #     logging.basicConfig(format=log_fmt, level=logging.DEBUG)
            #     self.logger = logging.getLogger(__name__)
            self.logger = RpgLogging(logger_name=__name__)
            # initialize the field.
            tot_objs: int = field_size * field_size
            self.field_size = field_size
            self.field_map = [Fieldsector() for bogus_val in range(tot_objs)]

            self.initiative = []   # list of lists to iterate over
            self.melee_with = {}
            self.h_cnt = len(heroes)

            with self.tracer.span(name='build_initiative_list'):
                for position, Hero in enumerate(heroes):
                    self.add_to_initiative_list(Hero, 'Heroes', position)

                self.o_cnt = len(opponents)
                for position, Opponent in enumerate(opponents):
                    self.add_to_initiative_list(Opponent, 'Opponents', position)
                self.initiative = sorted(self.initiative, reverse=True,
                                         key=itemgetter(3))

            if self.debug_ind == 1:
                self.logger.debug(f"Initiative Array: {self.initiative}", ctx)

            self.master_loop()

    def get_encounter_stats(self):
        return self.stats

    def get_characters_stats(self):
        characters_stats_dict = {'Heroes': [], 'Opponents': []}

        for hero in self.Heroes:
            characters_stats_dict['Heroes'].append(hero.get_character_stats())

        for opponent in self.Opponents:
            characters_stats_dict['Opponents'].append(opponent.get_character_stats())

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

    def sector_is_unoccupied(self, px: int, py: int) -> bool:
        # with self.tracer.span(name='sector_is_unoccupied'):
        list_index: int = self.get_array_index(px, py)
        ret_val: bool = not self.field_map[list_index].occupied

        if self.debug_ind == 1:
            msg = f"Is [{px}][{py}] field_map[{list_index}] available: {ret_val}"
            self.logger.debug(msg, ctx)
            if not ret_val:
                msg = (f"Occupied by: {self.field_map[list_index].occupied_by}" 
                       f"[{self.field_map[list_index].occupied_by_index}]")
                self.logger.debug(msg, ctx)
        return ret_val

    def move(self, identifier_name, identifier_index,
             leave_x, leave_y,
             occupy_x, occupy_y):
        # with self.tracer.span(name='move'):
        leave_list_ind = self.get_array_index(leave_x, leave_y)
        occupy_list_ind = self.get_array_index(occupy_x, occupy_y)
        if self.debug_ind == 1:
            msg = (f"moving {identifier_name}[{identifier_index}] from " 
                   f"[{leave_x}][{leave_y}] ({leave_list_ind}) to " 
                   f"[{occupy_x}][{occupy_y}] ({occupy_list_ind})")
            self.logger.debug(msg, ctx)
        self.field_map[leave_list_ind].leave_sector()
        self.field_map[occupy_list_ind].occupy_sector(identifier_name,
                                                      identifier_index)

    def get_target_distance_array(self, my_x, my_y, target_name):
        # with self.tracer.span(name='get_target_distance_array'):
        dist_list = []
        for fx in range(len(self.field_map)):
            if self.field_map[fx].occupied and self.field_map[fx].occupied_by == target_name:
                tmp_player = self.get_player(self.field_map[fx].occupied_by,
                                             self.field_map[fx].occupied_by_index)
                if tmp_player.alive:
                    fa, fb = self.get_grid_position(fx)
                    dist = calculate_distance(my_x, my_y, fa, fb)
                    dist_list.append([dist, fa, fb, self.field_map[fx].occupied_by,
                                      self.field_map[fx].occupied_by_index])
        dist_list = sorted(dist_list, reverse=False, key=itemgetter(0))
        return dist_list

    def add_to_initiative_list(self, src_single: object, source_list_name: str,
                               source_list_position: int):
        with self.tracer.span(name='add_to_initiative_list'):
            pc = src_single.check('Perception', 'Normal', 10)
            ini = src_single.roll_for_initiative('Normal')
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

    def remove_player_from_field(self, list_name: str, list_index: int):
        xy_loc = self.get_player_location(list_name, list_index)
        loc = self.get_array_index(xy_loc[0], xy_loc[1])
        self.field_map[loc].leave_sector()

    def master_loop(self):
        self.round = 1
        waiting_for = []
        while self.active:
            with self.tracer.span(name='master_loop_iteration'):
                for i in range(len(self.initiative)):
                    if self.active:
                        self.turn(i, waiting_for)
                        self.active = self.still_active()

                if self.active:
                    self.round += 1
                else:
                    self.wrap_up()

                if self.round > 59:
                    self.active = False
                    if self.debug_ind == 1:
                        self.logger.debug("Round Limit Reached.", ctx)
                    for x in range(len(self.field_map)):
                        if self.field_map[x].occupied:
                            a, b = self.get_grid_position(x)
                            msg = (f"[{x}] [{a}][{b}] {self.field_map[x].occupied_by}"
                                   f"[{self.field_map[x].occupied_by_index}]")
                            self.logger.debug(msg, ctx)

    def wrap_up(self):
        with self.tracer.span(name='wrap_up'):
            self.stats.winning_team = self.winning_list_name
            self.stats.duration_rds = self.round
            if self.debug_ind == 1:
                msg = f"The winner is: {self.winning_list_name} in {self.round} rounds."
                self.logger.debug(msg, ctx)
                msg = f"Surviving {self.winning_list_name}:"
                self.logger.debug(msg, ctx)
                for i in range(len(self.winning_list)):
                    if self.winning_list[i].alive:
                        msg = self.winning_list[i].get_name()
                        self.logger.debug(msg, ctx)
                self.logger.debug("Final field map", ctx)
                for x in range(len(self.field_map)):
                    if self.field_map[x].occupied:
                        a, b = self.get_grid_position(x)
                        msg = (f"[{x}] [{a}][{b}] {self.field_map[x].occupied_by}"
                               f"[{self.field_map[x].occupied_by_index}]")
                        self.logger.debug(msg, ctx)

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

    def cleanup_dead_player(self, player, x_loc, y_loc):
        if self.debug_ind == 1:
            self.logger.debug(f"{player.get_name()} is dead. Removing them from melee and field list. ", ctx)

        self.remove_all_from_melee_with(player)
        self.remove_player_from_field(x_loc, y_loc)
        for initiative_rec in self.initiative:
            if (initiative_rec[0] == x_loc and
                    initiative_rec[1] == y_loc):
                if len(initiative_rec) > 4:
                    del initiative_rec[5]
                if len(initiative_rec) > 3:
                    del initiative_rec[4]

    def turn(self, initiative_ind, waiting_for):
        with self.tracer.span(name='turn'):

            # try:
            #     vantage
            # except NameError:
            #     vantage = None

            cur_active = self.get_player(self.initiative[initiative_ind][0],
                                         self.initiative[initiative_ind][1])
            if self.initiative[initiative_ind][0] == "Heroes":
                target_array_name = "Opponents"
            else:
                target_array_name = "Heroes"

            if self.debug_ind == 1:
                msg = (f"\nRound: {self.round} turn: {initiative_ind} " 
                       f"Name: {cur_active.get_name()} ({cur_active.cur_hit_points}) " 
                       f"Unconscious: {cur_active.unconscious_ind} " 
                       f"Alive: {cur_active.alive} ")

                if len(self.initiative[initiative_ind]) == 6:
                    msg = (f'{msg}Grid Pos: [{self.initiative[initiative_ind][4]}]'
                           f'[{self.initiative[initiative_ind][5]}]')
                self.logger.debug(msg, ctx)

            self.remove_waiting_for(initiative_ind, waiting_for)

            if cur_active.alive and cur_active.cur_hit_points > 0:

                dl = (self.get_target_distance_array(
                        self.initiative[initiative_ind][4],
                        self.initiative[initiative_ind][5],
                        target_array_name))

                if self.debug_ind == 1:
                    for j in range(len(dl)):
                        self.logger.debug(f"dist: {dl[j][0]} {dl[j][1]} {dl[j][2]}", ctx)

                if self.debug_ind == 1:
                    self.logger.debug(f"Closest To: {dl[0][0]} {dl[0][1]} {dl[0][2]} {dl[0][3]} {dl[0][4]}", ctx)

                # Do they know why they are there?
                if not self.initiative[initiative_ind][2]:
                    # bonusaction_used = True
                    self.initiative[initiative_ind][2] = cur_active.check('Perception', 'Normal', 10)
                # Move
                # Define an obj for the current active combatant
                #    0 - How many sectors can they move
                #    1 - Combat preference: 'Ranged' or 'Melee'
                #    2 - X axis location
                #    3 - Y axis location
                avail_mvmt = cur_active.cur_movement / 5

                if self.debug_ind == 1:
                    msg = (f"starting mvmt: {avail_mvmt} " 
                           f"combat pref:   {cur_active.combat_preference} "
                           f"x loc:         {self.initiative[initiative_ind][4]} "
                           f"y loc:         {self.initiative[initiative_ind][5]}")
                    self.logger.debug(msg, ctx)

                avail_mvmt = self.movement(avail_mvmt,
                                           cur_active,
                                           self.initiative[initiative_ind],
                                           dl)

                if self.debug_ind == 1:
                    msg = (f"movement left: {avail_mvmt} " 
                           f"combat pref:   {cur_active.combat_preference} " 
                           f"x loc:         {self.initiative[initiative_ind][4]} " 
                           f"y loc:         {self.initiative[initiative_ind][5]}")
                    self.logger.debug(msg, ctx)

                    for j in range(len(dl)):
                        self.logger.debug(f"dist AFTER: {dl[j][0]} {dl[j][1]} {dl[j][2]}", ctx)

                # Action (Bonus or standard)
                # If they don't have a ranged weapon or spell attack
                # they must be a melee fighter.  When not in melee range
                # use action for movement.
                cur_action = cur_active.get_action(dl)

                if cur_action == 'Movement':
                    if self.debug_ind == 1:
                        msg = f"Using {cur_active.get_name()}'s Action for movement."
                        self.logger.debug(msg, ctx)

                    avail_mvmt = cur_active.cur_movement / 5
                    avail_mvmt = self.movement(avail_mvmt,
                                               cur_active,
                                               self.initiative[
                                                  initiative_ind],
                                               dl)
                    if self.debug_ind == 1:
                        for j in range(len(dl)):
                            self.logger.debug(f"dist AFTER Action: "
                                              f"{dl[j][0]} {dl[j][1]} {dl[j][2]}", ctx)
                elif cur_action == 'Wait on Melee':
                    # If an enemy gets into melee range this round, ATTACK!
                    if self.debug_ind == 1:
                        self.logger.debug(f"Using {cur_active.get_name()}'s Action waiting " 
                                          f"for an enemy to get into melee range.", ctx)
                        self.logger.debug(f"Adding to the waiting list: " 
                                          f"{dl[0][3]}[{dl[0][4]}]", ctx)

                    waiting_for.append([self.initiative[initiative_ind][0],
                                        self.initiative[initiative_ind][1],
                                        dl[0][3], dl[0][4]])
                elif cur_action == 'Melee':
                    if self.debug_ind == 1:
                        self.logger.debug(f"{cur_active.get_name()} is in melee with " 
                                          f"{dl[0][3]}[{dl[0][4]}]", ctx)
                    # do any superceding actions
                    s1 = self.get_waiting_for(initiative_ind, waiting_for)
                    for waiting_action in s1:
                        # Melee action happens here.
                        if self.debug_ind == 1:
                            self.logger.debug(f"{waiting_action[0]}[{waiting_action[1]}] " 
                                              f"has been waiting for this!", ctx)
                        directed_user = self.get_player(waiting_action[0], waiting_action[1])

                        if directed_user.cur_hit_points > 0:
                            # save off vantage to reset it.
                            t_vantage = directed_user.get_vantage()
                            # if the cur_active user is unconscious then the attack
                            # is at advantage and auto-crits on hit.
                            if cur_active.alive and cur_active.cur_hit_points < 1:
                                if t_vantage == 'Disadvantage':
                                    t_vantage = 'Normal'
                                else:
                                    t_vantage = 'Advantage'
                            else:
                                t_vantage = 'Normal'
                            directed_attack_tup = directed_user.default_melee_attack(vantage=t_vantage)
                            self.stats.inc_attack_attempts(waiting_action[0])
                            successful_defend = cur_active.melee_defend(attack_value=directed_attack_tup[0],
                                                                        possible_damage=directed_attack_tup[1],
                                                                        damage_type=directed_attack_tup[2])
                            if self.debug_ind == 1:
                                msg = f'{directed_user.get_name()}'
                                if successful_defend:
                                    msg = f'{msg} unsuccessfully'
                                else:
                                    msg = f'{msg} successfully'
                                msg = f'{msg} attacked {cur_active.get_name()}'
                                self.logger.debug(msg, ctx)

                            if not successful_defend:
                                self.stats.inc_attack_successes(waiting_action[0])
                                directed_user.inc_damage_dealt(damage_type=directed_attack_tup[2],
                                                               amount=directed_attack_tup[1])
                                directed_user.attack_success_count += 1

                            if not cur_active.alive:
                                self.cleanup_dead_player(cur_active,
                                                         self.initiative[initiative_ind][0],
                                                         self.initiative[initiative_ind][1])

                    if cur_active.cur_hit_points > 0:
                        target = self.get_player(dl[0][3], dl[0][4])
                        if self.debug_ind == 1:
                            t_msg = (f"{cur_active.get_name()} is attacking {target.get_name()}"
                                     f" ({dl[0][3]}[{dl[0][4]}]). ")
                            self.logger.debug(t_msg, ctx)

                        t_vantage = cur_active.get_vantage()
                        # if the cur_active user is unconscious then the attack is at advantage
                        # and auto-crits on hit.
                        if target.alive and target.unconscious_ind:
                            if t_vantage == 'Disadvantage':
                                t_vantage = 'Normal'
                            else:
                                t_vantage = 'Advantage'
                        else:
                            t_vantage = 'Normal'

                        active_attack_tup = cur_active.default_melee_attack(vantage=t_vantage)
                        self.stats.inc_attack_attempts(self.initiative[initiative_ind][0])
                        successful_defend = target.melee_defend(attack_value=active_attack_tup[0],
                                                                possible_damage=active_attack_tup[1],
                                                                damage_type=active_attack_tup[2])

                        if self.debug_ind == 1:
                            msg = f'{cur_active.get_name()}'
                            if successful_defend:
                                msg = f'{msg} unsuccessfully'
                            else:
                                msg = f'{msg} successfully'
                            msg = f'{msg} attacked {target.get_name()}'
                            self.logger.debug(msg, ctx)

                        if not successful_defend:
                            self.stats.inc_attack_successes(self.initiative[initiative_ind][0])
                            cur_active.inc_damage_dealt(damage_type=active_attack_tup[2], amount=active_attack_tup[1])
                            cur_active.attack_success_count += 1

                        if not target.alive:
                            self.cleanup_dead_player(target, dl[0][3], dl[0][4])

            elif cur_active.alive:  # currently alive but less than 1 hit point
                if self.debug_ind == 1:
                    self.logger.debug(f"{cur_active.get_name()} is unconscious. ", ctx)
                cur_active.death_save()
                if not cur_active.alive:
                    self.cleanup_dead_player(cur_active, self.initiative[initiative_ind][0],
                                             self.initiative[initiative_ind][1])
            else:
                if self.debug_ind == 1:
                    self.logger.debug(f"{cur_active.get_name()} is dead. Their turn is skipped. ", ctx)

    def remove_waiting_for(self, initiative_ind, waiting_for):
        # with self.tracer.span(name='remove_waiting_for'):
        if self.debug_ind == 1:
            self.logger.debug(f"Clear any waits for {self.initiative[initiative_ind][0]}" 
                              f"[{self.initiative[initiative_ind][1]}]", ctx)
        for sublist in waiting_for:
            if (sublist[0] == self.initiative[initiative_ind][0]
                    and sublist[1] == self.initiative[initiative_ind][1]):
                if self.debug_ind == 1:
                    self.logger.debug(f"removing: {sublist[0]}[{sublist[1]}]", ctx)
                waiting_for.remove(sublist)

    def get_waiting_for(self, initiative_ind, waiting_for):
        with self.tracer.span(name='get_waiting_for'):
            if self.debug_ind == 1:
                self.logger.debug(f"Anyone waiting on {self.initiative[initiative_ind][0]}" 
                                  f"[{self.initiative[initiative_ind][1]}]?", ctx)
            ret_val = []
            for sublist in waiting_for:
                if (sublist[2] == self.initiative[initiative_ind][0]
                        and sublist[3] == self.initiative[initiative_ind][1]):
                    ret_val.append([sublist[0], sublist[1]])
                    if self.debug_ind == 1:
                        self.logger.debug(f"Yes: {sublist[0]}[{sublist[1]}]", ctx)
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

    def movement(self, avail_movement, cur_active, cur_init, dest_list):
        # with self.tracer.span(name='movement'):
        if cur_init[2]:     # if they've figured out what's going on.
            if self.is_in_melee(cur_active):
                pass
            elif cur_active.combat_preference == 'Melee':
                # run straight towards closest enemy
                # set destination x and y
                dest_x = int(dest_list[0][1])
                dest_y = int(dest_list[0][2])
                cur_x = int(cur_init[4])
                cur_y = int(cur_init[5])

                if self.debug_ind == 1:
                    self.logger.debug(f"Tracking: {dest_list[0][3]}[{dest_list[0][4]}]", ctx)

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
                        if self.debug_ind == 1:
                            self.logger.debug(f"dist_x and dist_y = 0. Somethings wrong.", ctx)
                        mvmt = False
                    elif abs_dist_x <= 1 and abs_dist_y <= 1:
                        self.add_to_melee_with(cur_active, self.get_player(dest_list[0][3], dest_list[0][4]))
                        if self.debug_ind == 1:
                            self.logger.debug(f"*** Is in melee with " 
                                              f"{dest_list[0][3]}[{dest_list[0][4]}].", ctx)
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
                            if self.sector_is_unoccupied(tl_x[pi], tl_y[pi]):
                                self.move(cur_init[0], cur_init[1],
                                          cur_x, cur_y,
                                          tl_x[pi], tl_y[pi])
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

        return avail_movement


if __name__ == '__main__':
    logger_name='encounter_main_test'
    ctx = Ctx(app_username='encounter_class_init', logger_name=logger_name)
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging()
    db = InvokePSQL()
    Heroes = []
    Opponents = []
    Heroes.append(PlayerCharacter(db, ctx, debug_ind=1))
    Heroes.append(PlayerCharacter(db, ctx, debug_ind=1))
    Opponents.append(Foe(db, ctx, foe_candidate='Skeleton', debug_ind=1))
    Opponents.append(Foe(db, ctx, foe_candidate='Skeleton', debug_ind=1))
    e1 = Encounter(ctx=ctx, heroes=Heroes, opponents=Opponents, debug_ind=1)
    print(f"The winning party was: {e1.winning_list_name} in {e1.round} rounds.")
    print(f"The surviving {e1.winning_list_name} members:")
    for i in range(len(e1.winning_list)):
        if e1.winning_list[i].alive:
            print(f'{e1.winning_list[i].get_name()}')
