import math
import os
import fnmatch
import sys
import datetime
import json

from os import urandom
from random import randint
from string import ascii_uppercase, digits


# Masks for extracting the numbers we want from the maximum possible
# length of `urandom_bytes`.
bitmasks = [(0b111111 << (i * 6), i) for i in range(20)]
allowed_chars = (ascii_uppercase + digits).encode() * 16  # 576 chars long


def get_random_key():
    desired_length = randint(12, 20)
    bytes_needed = (((desired_length * 6) - 1) // 8) + 1
    urandom_bytes = int.from_bytes(urandom(bytes_needed), 'big')

    candidate = bytes([
        allowed_chars[
                (((urandom_bytes & bitmask) >> (i * 6)) + (0b111111 * i)) % 576]
        for bitmask, i in bitmasks
        ][:desired_length])

    return candidate.decode()


def array_to_string(src_array):
    outstr = ""
    for a in range(len(src_array)):
        outstr = f"{outstr}{src_array[a]},"
    outstr = outstr[:-1]

    return outstr


def string_to_string_array(src_str, delimiter=","):
    str_array = src_str.split(delimiter)
    return str_array


def string_to_array(src_str, delimiter=","):
    str_array = src_str.split(delimiter)
    out_array = []
    for a in range(len(str_array)):
        out_array.append(int(str_array[a].strip()))

    return out_array


def compare_arrays(array1, array2):
    return_value = True
    if len(array1) != len(array2):
        return_value = False
    for a in range(len(array1)):
        if array1[a] != array2[a]:
            return_value = False

    return return_value


def inches_to_feet(inches):
    feet = inches // 12
    remainder = inches % 12
    return f"{feet}ft. {remainder}in."


def dict_to_string(src_dict, linebreaks=False, left_justify=0):
    return_string = ""
    if linebreaks:
        el = '\n'
    else:
        el = ", "
    for key, value in src_dict.items():
        return_string = f"{return_string}{str(key).ljust(left_justify)}: {value}{el}"

    if not linebreaks:
        return_string = return_string[:-2]

    return return_string


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    dist: float = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
    return dist


def calculate_area_of_effect(player_location_x, player_location_y, field_range, aoe_type):
    map_squares = int(field_range / 5)
    return_list = []
    tmp_loc_x = player_location_x
    tmp_loc_y = player_location_y
    if aoe_type == "Line":
        tmp_loc_x += 1
        while tmp_loc_x <= player_location_x + map_squares:
            return_list.append((tmp_loc_x, tmp_loc_y))
            tmp_loc_x += 1
    elif aoe_type == "Cone":
        tmp_loc_x += 1
        tmp_width = 1
        while tmp_loc_x <= player_location_x + map_squares:
            for z in range(tmp_width):
                # range(1) makes a z = 0 only need one append in that case.
                if z > 0:
                    return_list.append((tmp_loc_x, (tmp_loc_y - z)))
                return_list.append((tmp_loc_x, (tmp_loc_y + z)))
            tmp_loc_x += 1
            tmp_width += 1

    elif aoe_type == "Cube":
        tmp_loc_x += 1
        while tmp_loc_x <= player_location_x + map_squares:
            for z in range(map_squares):
                if z > 0:  # range(1) makes a z = 0 only need one append in that case.
                    return_list.append((tmp_loc_x, (tmp_loc_y - z)))
                return_list.append((tmp_loc_x, (tmp_loc_y + z)))
            tmp_loc_x += 1
    elif aoe_type == "Sphere":
        # since the player will be at the center of a sphere, we expect the map_squares to be an odd number
        # or we will subtract one.
        if map_squares % 2 == 1:
            map_squares -= 1

        rad_width = (map_squares - 1) / 2
        tmp_loc_x -= rad_width
        while tmp_loc_x <= player_location_x + rad_width:
            for x in range(rad_width):
                for y in range(rad_width):
                    if y > 0 and x > 0:
                        return_list.append(((tmp_loc_x - x), (tmp_loc_y - y)))
                        return_list.append(((tmp_loc_x - x), (tmp_loc_y + y)))
                        return_list.append(((tmp_loc_x + x), (tmp_loc_y - y)))
                        return_list.append(((tmp_loc_x + x), (tmp_loc_y + y)))
                    elif y == 0 and x == 0:
                        return_list.append((tmp_loc_x, tmp_loc_y))
                    if y == 0 and x > 0:
                        return_list.append(((tmp_loc_x - x), tmp_loc_y))
                        return_list.append(((tmp_loc_x + x), tmp_loc_y))
                    if y > 0 and x == 0:
                        return_list.append((tmp_loc_x, (tmp_loc_y - y)))
                        return_list.append((tmp_loc_x, (tmp_loc_y + y)))
            tmp_loc_x += 1
    # Hemisphere
    # Radius
    # Cylinder
    return return_list


def find_file(file_name: str) -> str:
    curpath = os.path.abspath(os.path.dirname(__file__))
    for root, dirs, files in os.walk(curpath):
        for name in files:
            if fnmatch.fnmatch(name, file_name):
                return os.path.join(root, name)

    curpath = sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    print(curpath)
    for file in os.listdir(curpath):
        if fnmatch.fnmatch(file, file_name):
            return os.path.join(curpath, file)


def fix_date_for_json(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def fix_dict_for_json(d):
    return json.loads(json.dumps(d, default=fix_date_for_json))
