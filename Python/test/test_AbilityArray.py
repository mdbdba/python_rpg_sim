import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from AbilityArray import AbilityArray    # NOQA


def test_ability_array_default():
    a = AbilityArray()
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['debug_ind'] is False)
    assert(a.get_class_eval()[0]['array_type'] == 'Common')


def test_ability_array_predefined():
    comp_array = [8, 12, 15, 14, 13, 10]
    a = AbilityArray(array_type="Predefined",
                     raw_array=comp_array)
    b = a.get_array()
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
    assert(a.get_class_eval()[0]['array_type'] == 'Predefined')


def test_ability_array_common():
    a = AbilityArray(array_type="Common")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['array_type'] == 'Common')


def test_ability_array_common_sorted():
    comp_array = [15, 14, 13, 12, 10, 8]
    pref_array = [3, 2, 1, 5, 4, 0]
    # [8, 13, 14, 15, 10, 12]
    a = AbilityArray(array_type="standard",
                     pref_array=pref_array,
                     debug_ind=True)
    b = a.get_sorted_array()
    assert(a.get_class_eval()[0]['array_type'] == 'standard')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[pref_array[i]])
        assert(comp_array[i] == b[c['preference_array'][i]])


def test_ability_array_strict():
    a = AbilityArray(array_type="strict")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['array_type'] == 'strict')


def test_ability_array_standard():
    comp_array = [15, 14, 13, 12, 10, 8]
    pref_array = [0, 2, 1, 4, 5, 3]
    a = AbilityArray(array_type="standard",
                     pref_array=pref_array,
                     debug_ind=True)
    b = a.get_sorted_array()
    assert(a.get_class_eval()[0]['array_type'] == 'standard')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[pref_array[i]])
        assert(comp_array[i] == b[c['preference_array'][i]])


def test_ability_array_point_buy_even():
    comp_array = [13, 13, 13, 12, 12, 12]
    a = AbilityArray(array_type="point_buy_even",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'point_buy_even')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
        assert(comp_array[i] == c['raw_array'][i])


def test_ability_array_point_buy_one_max():
    comp_array = [15, 12, 12, 12, 11, 11]
    a = AbilityArray(array_type="point_buy_one_max",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'point_buy_one_max')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
        assert(comp_array[i] == c['raw_array'][i])


def test_ability_array_point_buy_two_max():
    comp_array = [15, 15, 11, 10, 10, 10]
    a = AbilityArray(array_type="point_buy_two_max",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'point_buy_two_max')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
        assert(comp_array[i] == c['raw_array'][i])


def test_ability_array_point_buy_three_max():
    comp_array = [15, 15, 15, 8, 8, 8]
    a = AbilityArray(array_type="point_buy_three_max",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'point_buy_three_max')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
        assert(comp_array[i] == c['raw_array'][i])
