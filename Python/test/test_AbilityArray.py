import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from AbilityArray import AbilityArray    # NOQA


def test_AbilityArray_Default():
    a = AbilityArray()
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['debug_ind'] is False)
    assert(a.get_class_eval()[0]['array_type'] == 'Common')


def test_AbilityArray_Predefined():
    compArray = [8, 12, 15, 14, 13, 10]
    a = AbilityArray(array_type="Predefined",
                     raw_array=compArray)
    b = a.get_array()
    for i in range(0, 6):
        assert(compArray[i] == b[i])
    assert(a.get_class_eval()[0]['array_type'] == 'Predefined')


def test_AbilityArray_Common():
    a = AbilityArray(array_type="Common")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['array_type'] == 'Common')


def test_AbilityArray_Common_Sorted():
    compArray = [15, 14, 13, 12, 10, 8]
    prefArray = [3, 2, 1, 5, 4, 0]
    # [8, 13, 14, 15, 10, 12]
    a = AbilityArray(array_type="Standard",
                     pref_array=prefArray,
                     debug_ind=True)
    b = a.get_sorted_array()
    assert(a.get_class_eval()[0]['array_type'] == 'Standard')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[prefArray[i]])
        assert(compArray[i] == b[c['preference_array'][i]])


def test_AbilityArray_Strict():
    a = AbilityArray(array_type="Strict")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_class_eval()[0]['array_type'] == 'Strict')


def test_AbilityArray_Standard():
    compArray = [15, 14, 13, 12, 10, 8]
    prefArray = [0, 2, 1, 4, 5, 3]
    a = AbilityArray(array_type="Standard",
                     pref_array=prefArray,
                     debug_ind=True)
    b = a.get_sorted_array()
    assert(a.get_class_eval()[0]['array_type'] == 'Standard')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[prefArray[i]])
        assert(compArray[i] == b[c['preference_array'][i]])


def test_AbilityArray_PointBuy_Even():
    compArray = [13, 13, 13, 12, 12, 12]
    a = AbilityArray(array_type="PointBuy_Even",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'PointBuy_Even')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[i])
        assert(compArray[i] == c['raw_array'][i])


def test_AbilityArray_PointBuy_OneMax():
    compArray = [15, 12, 12, 12, 11, 11]
    a = AbilityArray(array_type="PointBuy_OneMax",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'PointBuy_OneMax')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[i])
        assert(compArray[i] == c['raw_array'][i])


def test_AbilityArray_PointBuy_TwoMax():
    compArray = [15, 15, 11, 10, 10, 10]
    a = AbilityArray(array_type="PointBuy_TwoMax",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'PointBuy_TwoMax')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[i])
        assert(compArray[i] == c['raw_array'][i])


def test_AbilityArray_PointBuy_ThreeMax():
    compArray = [15, 15, 15, 8, 8, 8]
    a = AbilityArray(array_type="PointBuy_ThreeMax",
                     debug_ind=True)
    b = a.get_raw_array()
    assert(a.get_class_eval()[0]['array_type'] == 'PointBuy_ThreeMax')
    c = a.get_class_eval()[-1]
    for i in range(0, 6):
        assert(compArray[i] == b[i])
        assert(compArray[i] == c['raw_array'][i])
