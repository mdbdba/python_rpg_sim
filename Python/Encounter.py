
import math
import logging

from operator import itemgetter

from Fieldsector import Fieldsector
from PlayerCharacter import PlayerCharacter
from Foe import Foe

from InvokePSQL import InvokePSQL
from Trace_it import Trace_it




class Encounter(object):
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
                 heroes,
                 opponents,
                 field_size=100,
                 debug_ind=0,
                 tracer=None
                 ):
        """

        :type heroes: list
        :type opponents: list
        :type field_size: int
        :type debug_ind: int
        """
        if not tracer:
            t = Trace_it("encounter")
            self.tracer = t.tracer
        else:
            self.tracer = tracer

        with self.tracer.span(name='encounter'):
            self.debug_ind = debug_ind
            self.Heroes = heroes
            self.Opponents = opponents
            self.active = True
            self.round = 0
            self.winning_list = []
            self.winning_list_name = ""

            if ((self.debug_ind == 1) and
               ((getattr(self, "logger", None)) is None)):
                log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
                logging.basicConfig(format=log_fmt, level=logging.DEBUG)
                self.logger = logging.getLogger(__name__)

            # initialize the field.
            tot_objs: int = field_size * field_size
            self.field_size = field_size
            self.field_map = [Fieldsector() for bogus_val in range(tot_objs)]

            self.initiative = []   # list of lists to iterate over
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
                self.logger.debug(f"Initiative Array: {self.initiative}")

            self.master_loop()

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

    def get_player(self, list_name: str, list_index: int ):
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
            self.logger.debug(msg)
            if not ret_val:
                msg = ( f"Occupied by: {self.field_map[list_index].occupied_by}" 
                        f"[{self.field_map[list_index].occupied_by_index}]")
                self.logger.debug(msg)
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
            self.logger.debug(msg)
        self.field_map[leave_list_ind].leave_sector()
        self.field_map[occupy_list_ind].occupy_sector(identifier_name,
                                                      identifier_index)

    def get_target_distance_array(self, my_x, my_y, target_name):
        # with self.tracer.span(name='get_target_distance_array'):
        dist_list = []
        for fx in range(len(self.field_map)):
            if self.field_map[fx].occupied and self.field_map[fx].occupied_by == target_name:
                tmp_player = self.get_player( self.field_map[fx].occupied_by,
                                              self.field_map[fx].occupied_by_index)
                if tmp_player.alive:
                    fa, fb = self.get_grid_position(fx)
                    dist = self.calculate_distance(my_x, my_y, fa, fb)
                    dist_list.append([dist, fa, fb, self.field_map[fx].occupied_by,
                                      self.field_map[fx].occupied_by_index])
        dist_list = sorted(dist_list, reverse=False, key=itemgetter(0))
        return dist_list

    @staticmethod
    def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
        dist: float = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
        return dist

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

    def wrap_up(self):
        with self.tracer.span(name='wrap_up'):
            if self.debug_ind == 1:
                msg = f"The winner is: {self.winning_list_name} in {self.round} rounds."
                self.logger.debug(msg)
                msg = f"Surviving {self.winning_list_name}:"
                self.logger.debug(msg)
                for i in range(len(self.winning_list)):
                    if self.winning_list[i].alive:
                        msg = self.winning_list[i].get_name()
                        self.logger.debug(msg)
                self.logger.debug("Final field map")
                for x in range(len(self.field_map)):
                    if self.field_map[x].occupied:
                        a, b = self.get_grid_position(x)
                        msg = (f"[{x}] [{a}][{b}] {self.field_map[x].occupied_by}"
                               f"[{self.field_map[x].occupied_by_index}]")
                        self.logger.debug(msg)



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

    def turn(self, initiative_ind, waiting_for):
        with self.tracer.span(name='turn'):
            cur_active = self.get_player(self.initiative[initiative_ind][0],
                                         self.initiative[initiative_ind][1])
            if self.initiative[initiative_ind][0] == "Heroes":
                target_array_name = "Opponents"
            else:
                target_array_name = "Heroes"

            # action_used = False
            # bonusaction_used = False

            if self.debug_ind == 1:
                msg = (f'\nRound: {self.round} turn: {initiative_ind} ' 
                       f'Name: {cur_active.get_name()} ' 
                       f'Grid Pos: [{self.initiative[initiative_ind][4]}]' 
                       f'[{self.initiative[initiative_ind][5]}]')
                self.logger.debug(msg)

            self.remove_waiting_for(initiative_ind, waiting_for)

            dl = (self.get_target_distance_array(
                    self.initiative[initiative_ind][4],
                    self.initiative[initiative_ind][5],
                    target_array_name))

            if self.debug_ind == 1:
                for j in range(len(dl)):
                    self.logger.debug(f"dist: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

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
                self.logger.debug(msg)

            avail_mvmt = self.movement(avail_mvmt,
                                       cur_active,
                                       self.initiative[initiative_ind],
                                       dl)

            if self.debug_ind == 1:
                msg = (f"movement left: {avail_mvmt} " 
                       f"combat pref:   {cur_active.combat_preference} " 
                       f"x loc:         {self.initiative[initiative_ind][4]} " 
                       f"y loc:         {self.initiative[initiative_ind][5]}")
                self.logger.debug(msg)

                for j in range(len(dl)):
                    self.logger.debug(f"dist AFTER: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

            # Action (Bonus or standard)
            # If they don't have a ranged weapon or spell attack
            # they must be a melee fighter.  When not in melee range
            # use action for movement.
            cur_action = cur_active.get_action(dl)
            if cur_action == 'Movement':
                if self.debug_ind == 1:
                    msg = (f"Using {cur_active.get_name()}'s Action for movement.")
                    self.logger.debug(msg)

                avail_mvmt = cur_active.cur_movement / 5
                avail_mvmt = self.movement(avail_mvmt,
                                           cur_active,
                                           self.initiative[
                                              initiative_ind],
                                           dl)
                if self.debug_ind == 1:
                    for j in range(len(dl)):
                        self.logger.debug(f"dist AFTER Action: "
                                          f"{dl[j][0]} {dl[j][1]} {dl[j][2]}")
            elif cur_action == 'Wait on Melee':
                # If an enemy gets into melee range this round, ATTACK!
                if self.debug_ind == 1:
                    self.logger.debug(f"Using {cur_active.get_name()}'s Action waiting " 
                                      f"for an enemy to get into melee range.")
                    self.logger.debug(f"Adding to the waiting list: " 
                                      f"{dl[0][3]}[{dl[0][4]}]")

                waiting_for.append([self.initiative[initiative_ind][0],
                                    self.initiative[initiative_ind][1],
                                    dl[0][3], dl[0][4]])
            elif cur_action == 'Melee':
                if self.debug_ind == 1:
                    self.logger.debug(f"{cur_active.get_name()} is in melee with " 
                                      f"{dl[0][3]}[{dl[0][4]}]")
                # do any superceding actions
                s1 = self.get_waiting_for(initiative_ind, waiting_for)
                for waiting_action in s1:
                    # Melee action happens here.
                    if self.debug_ind == 1:
                        self.logger.debug(f"{waiting_action[0]}[{waiting_action[1]}] " 
                                          f"has been waiting for this!")
                    directed_user = self.get_player(waiting_action[0], waiting_action[1])

                    if directed_user.alive:
                        # this is where the attack would be put.
                        nuke_em = self.get_party_list(self.initiative[initiative_ind][0])
                        for q in range(len(nuke_em)):
                            nuke_em[q].melee_defend(modifier=20,
                                                    possible_damage=(3 * nuke_em[q].hit_points),
                                                    damage_type='Bludgeoning')
                            # nuke_em[q].alive = False
                            # nuke_em[q].cur_hit_points = 0

                if cur_active.cur_hit_points > 0:
                    # this is where the attack would be put.
                    # target = self.get_player(dl[0][3],dl[0][4])
                    nuke_em = self.get_party_list(dl[0][3])
                    for q in range(len(nuke_em)):
                        nuke_em[q].melee_defend(modifier=20,
                                                possible_damage=(3 * nuke_em[q].hit_points),
                                                damage_type='Bludgeoning')
                        # nuke_em[q].alive = False
                        # nuke_em[q].cur_hit_points = 0

            if self.debug_ind == 1:
                self.logger.debug(f"Closest To: {dl[0][0]} {dl[0][1]} {dl[0][2]} {dl[0][3]} {dl[0][4]}")

    def remove_waiting_for(self, initiative_ind, waiting_for):
        # with self.tracer.span(name='remove_waiting_for'):
        if self.debug_ind == 1:
            self.logger.debug(f"Clear any waits for {self.initiative[initiative_ind][0]}" 
                              f"[{self.initiative[initiative_ind][1]}]")
        for sublist in waiting_for:
            if (sublist[0] == self.initiative[initiative_ind][0]
                    and sublist[1] == self.initiative[initiative_ind][1]):
                if self.debug_ind == 1:
                    self.logger.debug(f"removing: {sublist[0]}[{sublist[1]}]")
                waiting_for.remove(sublist)

    def get_waiting_for(self, initiative_ind, waiting_for):
        with self.tracer.span(name='get_waiting_for'):
            if self.debug_ind == 1:
                self.logger.debug(f"Anyone waiting on {self.initiative[initiative_ind][0]}" 
                                  f"[{self.initiative[initiative_ind][1]}]?")
            ret_val = []
            for sublist in waiting_for:
                if (sublist[2] == self.initiative[initiative_ind][0]
                        and sublist[3] == self.initiative[initiative_ind][1]):
                    ret_val.append([sublist[0], sublist[1]])
                    if self.debug_ind == 1:
                        self.logger.debug(f"Yes: {sublist[0]}[{sublist[1]}]")
                    waiting_for.remove(sublist)

            return ret_val

    def movement(self, avail_movement, cur_active, cur_init, dest_list):
        # with self.tracer.span(name='movement'):
        if cur_init[2]:     # if they've figured out what's going on.
            if cur_active.combat_preference == 'Melee':
                # run straight towards closest enemy
                # set destination x and y
                dest_x = int(dest_list[0][1])
                dest_y = int(dest_list[0][2])
                cur_x = int(cur_init[4])
                cur_y = int(cur_init[5])

                if self.debug_ind == 1:
                    self.logger.debug(f"Tracking: {dest_list[0][3]}[{dest_list[0][4]}]")

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
                            self.logger.debug(f"dist_x and dist_y = 0. Somethings wrong.")
                        mvmt = False
                    elif abs_dist_x <= 1 and abs_dist_y <= 1:
                        if self.debug_ind == 1:
                            self.logger.debug(f"*** Is in melee with " 
                                              f"{dest_list[0][3]}[{dest_list[0][4]}].")
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
                                dest_list[0][0] = self.calculate_distance(
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
    db = InvokePSQL()
    Heroes = []
    Opponents = []
    Heroes.append(PlayerCharacter(db, debug_ind=1))
    Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=1))
    e1 = Encounter(Heroes, Opponents, debug_ind=1)
    print(f"The winning party was: {e1.winning_list_name} in {e1.round} rounds.")
    print(f"The surviving {e1.winning_list_name} members:")
    for i in range(len(e1.winning_list)):
        if e1.winning_list[i].alive:
            print(f'{e1.winning_list[i].get_name()}')
