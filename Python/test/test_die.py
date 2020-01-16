import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),  '..'))
from Die import Die     # NOQA


def test_2():
    d = Die(2)
    r = d.roll(1)
    assert(2 >= r >= 1)


def test_2_droplowest():
    d = Die(2, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(2 >= r >= 1)


def test_4():
    d = Die(4)
    r = d.roll(1)
    assert(4 >= r >= 1)


def test_4_droplowest():
    d = Die(4, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(4 >= r >= 1)


def test_d6():
    d = Die(6)
    r = d.roll(1)
    assert(6 >= r >= 1)


def test_d6_droplowest():
    d = Die(6, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(6 >= r >= 1)


def test_3d6():
    d = Die(6)
    r = d.roll(3)
    assert(18 >= r >= 3)


def test_3d6_droplowest():
    d = Die(6, True)
    r = d.roll(4, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 4)
    assert(details.die_total_used == r)
    assert(18 >= r >= 3)


def test_d8():
    d = Die(8)
    r = d.roll(1)
    assert(8 >= r >= 1)


def test_d8_droplowest():
    d = Die(8, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(8 >= r >= 1)


def test_2d8():
    d = Die(8)
    r = d.roll(2)
    assert(16 >= r >= 2)


def test_2d8_droplowest():
    d = Die(8, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(16 >= r >= 1)


def test_d10():
    d = Die(10)
    r = d.roll(1)
    assert(10 >= r >= 1)


def test_d10_droplowest():
    d = Die(10, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(10 >= r >= 1)


def test_d12():
    d = Die(12)
    r = d.roll(1)
    assert(12 >= r >= 1)


def test_d12_droplowest():
    d = Die(12, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(12 >= r >= 1)


def test_d20():
    d = Die(20)
    r = d.roll(1)
    assert(20 >= r >= 1)


def test_d20_droplowest():
    d = Die(20, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(20 >= r >= 1)


def test_d100():
    d = Die(100)
    r = d.roll(1)
    assert(100 >= r >= 1)


def test_d100_droplowest():
    d = Die(100, True)
    r = d.roll(2, True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(100 >= r >= 1)


def test_d20_withadvantage():
    d = Die(20, True)
    r = d.roll_with_advantage()
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(max(details.base_roll) == r)
    assert(20 >= r >= 1)


def test_d20_withdisadvantage():
    d = Die(20, True)
    r = d.roll_with_disadvantage()
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(min(details.base_roll) == r)
    assert(20 >= r >= 1)


def test_4d6_withresistance():
    d = Die(6, True)
    r = d.roll_with_resistance(4)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 4)
    assert(details.die_total_used == r)
    assert(12 >= r >= 2)
