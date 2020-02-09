import math
import os
import fnmatch
import sys

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
                (((urandom_bytes & bitmask) >> (i * 6)) + (0b111111 * i)) % 576 ]
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

