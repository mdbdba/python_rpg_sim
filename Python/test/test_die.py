import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),  '..'))
from Die import Die     # NOQA
from Ctx import Ctx


def test_2():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=2)
    r = d.roll(rolls=1)
    assert(2 >= r >= 1)


def test_2_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=2, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(2 >= r >= 1)


def test_4():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=4)
    r = d.roll(rolls=1)
    assert(4 >= r >= 1)


def test_4_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=4, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(4 >= r >= 1)


def test_d6():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=6)
    r = d.roll(rolls=1)
    assert(6 >= r >= 1)


def test_d6_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=6, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(6 >= r >= 1)


def test_3d6():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=6)
    r = d.roll(rolls=3)
    assert(18 >= r >= 3)


def test_3d6_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=6, debug_ind=True)
    r = d.roll(rolls=4, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 4)
    assert(details.die_total_used == r)
    assert(18 >= r >= 3)


def test_d8():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=8)
    r = d.roll(rolls=1)
    assert(8 >= r >= 1)


def test_d8_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=8, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(8 >= r >= 1)


def test_2d8():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=8)
    r = d.roll(rolls=2)
    assert(16 >= r >= 2)


def test_2d8_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=8, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(16 >= r >= 1)


def test_d10():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=10)
    r = d.roll(rolls=1)
    assert(10 >= r >= 1)


def test_d10_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=10, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(10 >= r >= 1)


def test_d12():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=12)
    r = d.roll(rolls=1)
    assert(12 >= r >= 1)


def test_d12_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=12, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(12 >= r >= 1)


def test_d20():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=20)
    r = d.roll(rolls=1)
    assert(20 >= r >= 1)


def test_d20_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=20, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(20 >= r >= 1)


def test_d100():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=100)
    r = d.roll(rolls=1)
    assert(100 >= r >= 1)


def test_d100_droplowest():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=100, debug_ind=True)
    r = d.roll(rolls=2, droplowest=True)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(100 >= r >= 1)


def test_d20_withadvantage():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=20, debug_ind=True)
    r = d.roll_with_advantage()
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(max(details.base_roll) == r)
    assert(20 >= r >= 1)


def test_d20_withdisadvantage():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=20, debug_ind=True)
    r = d.roll_with_disadvantage()
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 2)
    assert(details.die_total_used == r)
    assert(min(details.base_roll) == r)
    assert(20 >= r >= 1)


def test_4d6_withresistance():
    ctx = Ctx(app_username='Testing')
    d = Die(ctx=ctx, sides=6, debug_ind=True)
    r = d.roll_with_resistance(rolls=4)
    details = d.get_details()[-1]
    assert(len(details.base_roll) == 4)
    assert(details.die_total_used == r)
    assert(12 >= r >= 2)
