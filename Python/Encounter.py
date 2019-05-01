
import math

from operator import itemgetter
# from typing import List, Any

from Fieldsector import Fieldsector
from PlayerCharacter import PlayerCharacter
from Foe import Foe

from InvokePSQL import InvokePSQL


class Encounter(object):
    Heroes: list
    Opponents: list
    winning_list: list
    winning_list_name: str
    field_size: int
    field_map: list
    h_cnt: int
    o_cnt: int

    def __init__(self,
                 heroes,
                 opponents,
                 field_size=100
                 ):
        """

        :type heroes: list
        :type opponents: list
        :type field_size: int
        """
        self.Heroes = heroes
        self.Opponents = opponents
        self.active = True
        self.round = 0
        self.winning_list = []
        self.winning_list_name = ""

        # initialize the field.
        tot_objs: int = field_size * field_size
        self.field_size = field_size
        self.field_map = [Fieldsector() for bogus_val in range(tot_objs)]

        self.initiative = []   # list of lists to iterate over
        self.h_cnt = len(heroes)

        for position, Hero in enumerate(heroes):
            self.add_to_initiative_list(Hero, 'Heroes', position)

        self.o_cnt = len(opponents)
        for position, Opponent in enumerate(opponents):
            self.add_to_initiative_list(Opponent, 'Opponents', position)
        self.initiative = sorted(self.initiative, reverse=True,
                                 key=itemgetter(3))
        self.master_loop()

    def get_hero_count(self):
        return self.h_cnt

    def get_opponent_count(self):
        return self.o_cnt

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
        list_index: int = self.get_array_index(px, py)
        ret_val: bool = not self.field_map[list_index].occupied
        print(f"Is [{px}][{py}] field_map[{list_index}] available: {ret_val}")
        if not ret_val:
            print(f"Occupied by: {self.field_map[list_index].occupied_by}"
                  f"[{self.field_map[list_index].occupied_by_index}]")
        return ret_val

    def move(self, identifier_name, identifier_index,
             leave_x, leave_y,
             occupy_x, occupy_y):
        leave_list_ind = self.get_array_index(leave_x, leave_y)
        occupy_list_ind = self.get_array_index(occupy_x, occupy_y)
        print(f"moving {identifier_name}[{identifier_index}] from "
              f"[{leave_x}][{leave_y}] ({leave_list_ind}) to "
              f"[{occupy_x}][{occupy_y}] ({occupy_list_ind})")
        self.field_map[leave_list_ind].leave_sector()
        self.field_map[occupy_list_ind].occupy_sector(identifier_name,
                                                      identifier_index)

    def get_target_distance_array(self, my_x, my_y, target_name):
        dist_list = []
        for fx in range(self.field_size * self.field_size):
            if self.field_map[fx].occupied and self.field_map[fx].occupied_by == target_name:
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
            for i in range(len(self.initiative)):
                if self.active:
                    self.turn(i, waiting_for)
                    self.active = self.still_active()
            if self.active:
                self.round += 1
            else:
                self.wrap_up()

    def wrap_up(self):
        print(f"The winner is: {self.winning_list_name} in {self.round} rounds.")
        print(f"Surviving {self.winning_list_name}:")
        for i in range(len(self.winning_list)):
            if self.winning_list[i].alive:
                print(self.winning_list[i].get_name())

    def still_active(self):
        ret_val = False
        sub_val1 = False
        sub_val2 = False
        for i in range(len(self.Heroes)):
            if self.Heroes[i].alive:
                sub_val1 = True
                break
        for i in range(len(self.Opponents)):
            if self.Opponents[i].alive:
                sub_val2 = True
                break

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
        if self.initiative[initiative_ind][0] == "Heroes":
            cur_active = self.Heroes[self.initiative[initiative_ind][1]]
            target_array_name = "Opponents"
        else:
            cur_active = (self.Opponents[
                            self.initiative[initiative_ind][1]])
            target_array_name = "Heroes"

        # action_used = False
        # bonusaction_used = False

        print(f'\nRound: {self.round} turn: {initiative_ind} '
              f'Name: {cur_active.get_name()} '
              f'Grid Pos: [{self.initiative[initiative_ind][4]}]'
              f'[{self.initiative[initiative_ind][5]}]')

        self.remove_waiting_for(initiative_ind, waiting_for)

        dl = (self.get_target_distance_array(
                self.initiative[initiative_ind][4],
                self.initiative[initiative_ind][5],
                target_array_name))

        for j in range(len(dl)):
            print(f"dist: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

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
        print(f"starting mvmt: {avail_mvmt} "
              f"combat pref:   {cur_active.combat_preference} "
              f"x loc:         {self.initiative[initiative_ind][4]} "
              f"y loc:         {self.initiative[initiative_ind][5]}")
        avail_mvmt = self.movement(avail_mvmt,
                                   cur_active,
                                   self.initiative[initiative_ind],
                                   dl)
        print(f"movement left: {avail_mvmt} "
              f"combat pref:   {cur_active.combat_preference} "
              f"x loc:         {self.initiative[initiative_ind][4]} "
              f"y loc:         {self.initiative[initiative_ind][5]}")

        for j in range(len(dl)):
            print(f"dist AFTER: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

        # Action (Bonus or standard)
        # If they don't have a ranged weapon or spell attack
        # they must be a melee fighter.  When not in melee range
        # use action for movement.
        cur_action = cur_active.get_action(dl)
        if cur_action == 'Movement':
            print(f"Using {cur_active.get_name()}'s Action for "
                  f"movement.")
            avail_mvmt = cur_active.cur_movement / 5
            avail_mvmt = self.movement(avail_mvmt,
                                       cur_active,
                                       self.initiative[
                                          initiative_ind],
                                       dl)
            for j in range(len(dl)):
                print(f"dist AFTER Action: {dl[j][0]} {dl[j][1]} "
                      f"{dl[j][2]}")
        elif cur_action == 'Wait on Melee':
            # If an enemy gets into melee range this round, ATTACK!
            print(f"Using {cur_active.get_name()}'s Action waiting "
                  f"for an enemy to get into melee range.")
            print(f"adding to the waiting list: "
                  f"{dl[0][3]}[{dl[0][4]}]")
            waiting_for.append([self.initiative[initiative_ind][0],
                                self.initiative[initiative_ind][1],
                                dl[0][3], dl[0][4]])
        elif cur_action == 'Melee':
            print(f"{cur_active.get_name()} is in melee with "
                  f"{dl[0][3]}[{dl[0][4]}]")
            # do any superceding actions
            s1 = self.get_waiting_for(initiative_ind, waiting_for)
            for waiting_action in s1:
                # Melee action happens here.
                print(f"{waiting_action[0]}[{waiting_action[1]}] "
                      f"has been waiting for this!")
                if waiting_action[0] == "Heroes":
                    directed_user = self.Heroes[waiting_action[1]]
                else:
                    directed_user = (self.Opponents[waiting_action[1]])

                if directed_user.alive:
                    cur_active.alive = False
                    cur_active.cur_hit_points = 0

            if cur_active.cur_hit_points > 0:
                if dl[0][3] == "Heroes":
                    target = self.Heroes[dl[0][4]]
                else:
                    target = self.Opponents[dl[0][4]]

                target.alive = False
                target.cur_hit_points = 0

        print(f"Closest To: {dl[0][0]} {dl[0][1]} {dl[0][2]}")

    def remove_waiting_for(self, initiative_ind, waiting_for):
        print(f"Clear any waits for {self.initiative[initiative_ind][0]}"
              f"[{self.initiative[initiative_ind][1]}]")
        for sublist in waiting_for:
            if (sublist[0] == self.initiative[initiative_ind][0]
                    and sublist[1] == self.initiative[initiative_ind][1]):
                print(f"removing: {sublist[0]}[{sublist[1]}]")
                waiting_for.remove(sublist)

    def get_waiting_for(self, initiative_ind, waiting_for):
        print(f"Anyone waiting on {self.initiative[initiative_ind][0]}"
              f"[{self.initiative[initiative_ind][1]}]?")
        ret_val = []
        for sublist in waiting_for:
            if (sublist[2] == self.initiative[initiative_ind][0]
                    and sublist[3] == self.initiative[initiative_ind][1]):
                ret_val.append([sublist[0], sublist[1]])
                print(f"Yes: {sublist[0]}[{sublist[1]}]")
                waiting_for.remove(sublist)

        return ret_val

    def movement(self, avail_movement, cur_active, cur_init, dest_list):
        if cur_init[2]:     # if they've figured out what's going on.
            if cur_active.combat_preference == 'Melee':
                # run straight towards closest enemy
                # set destination x and y
                dest_x = int(dest_list[0][1])
                dest_y = int(dest_list[0][2])
                cur_x = int(cur_init[4])
                cur_y = int(cur_init[5])

                print(f"Tracking: {dest_list[0][3]}[{dest_list[0][4]}]")

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
                        print(f"dist_x and dist_y = 0. Somethings wrong.")
                        mvmt = False
                    elif abs_dist_x == 1 or abs_dist_y == 1:
                        print(f"*** Is in melee with "
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
                        for i in range(3):
                            if self.sector_is_unoccupied(tl_x[i], tl_y[i]):
                                self.move(cur_init[0], cur_init[1],
                                          cur_x, cur_y,
                                          tl_x[i], tl_y[i])
                                cur_x = tl_x[i]
                                cur_y = tl_y[i]
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
    e1 = Encounter(Heroes, Opponents)
    print(e1.initiative)
    for x in range(e1.field_size * e1.field_size):
        if e1.field_map[x].occupied:
            a, b = e1.get_grid_position(x)
            print(f"[{x}] [{a}][{b}] {e1.field_map[x].occupied_by}"
                  f"[{e1.field_map[x].occupied_by_index}]")

#     print(f'[0,10],[0,11] {e1.calculate_distance(0,10, 0,11)} feet')
#     print(f'[0,10],[99,11] {e1.calculate_distance(0,10, 99,11)} feet')
