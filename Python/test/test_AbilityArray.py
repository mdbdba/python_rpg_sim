import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from AbilityArray import AbilityArray    # NOQA
from Ctx import Ctx


def test_ability_array_default():
    ctx = Ctx(app_username='Testing')
    a = AbilityArray(ctx=ctx)
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_method_last_call_audit(method_name='__init__')['audit_json']['used_array_type'] == 'Common')


def test_ability_array_predefined():
    ctx = Ctx(app_username='Testing')
    comp_array = [8, 12, 15, 14, 13, 10]
    a = AbilityArray(ctx=ctx, array_type="Predefined",
                     raw_array=comp_array)
    b = a.get_array()
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
    assert(a.get_method_last_call_audit(method_name='__init__')['audit_json']['used_array_type'] == 'Predefined')


def test_ability_array_common():
    ctx = Ctx(app_username='Testing')
    a = AbilityArray(ctx=ctx, array_type="Common")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_method_last_call_audit(method_name='__init__')['audit_json']['used_array_type'] == 'Common')


def test_ability_array_common_sorted():
    ctx = Ctx(app_username='Testing')
    comp_array = [15, 14, 13, 12, 10, 8]
    pref_array = [3, 2, 1, 5, 4, 0]
    # [8, 13, 14, 15, 10, 12]
    a = AbilityArray(ctx=ctx, array_type="standard",
                     pref_array=pref_array )
    b = a.get_sorted_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'standard')
    for i in range(0, 6):
        assert(comp_array[i] == b[pref_array[i]])
        assert(comp_array[i] == b[audit['__init__']['methodParams']['pref_array'][i]])


def test_ability_array_strict():
    ctx = Ctx(app_username='Testing')
    a = AbilityArray(ctx=ctx, array_type="strict")
    b = a.get_array()
    for i in range(0, 6):
        assert(18 >= b[i] >= 3)
    assert(a.get_method_last_call_audit(method_name='__init__')['audit_json']['used_array_type'] == 'strict')


def test_ability_array_standard():
    ctx = Ctx(app_username='Testing')
    comp_array = [15, 14, 13, 12, 10, 8]
    pref_array = [0, 2, 1, 4, 5, 3]
    a = AbilityArray(ctx=ctx, array_type="standard",
                     pref_array=pref_array)
    b = a.get_sorted_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'standard')
    for i in range(0, 6):
        assert(comp_array[i] == b[pref_array[i]])
        assert(comp_array[i] == b[audit['__init__']['methodParams']['pref_array'][i]])


def test_ability_array_point_buy_even():
    ctx = Ctx(app_username='Testing')
    comp_array = [13, 13, 13, 12, 12, 12]
    order_comp_array = [12, 12, 12, 13, 13, 13]
    pref_array = [5, 4, 3, 0, 1, 2]
    a = AbilityArray(ctx=ctx, array_type="point_buy_even", pref_array=pref_array)
    b = a.get_raw_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'point_buy_even')
    for i in range(0, 6):
        assert(comp_array[i] == b[i])
        assert(order_comp_array[i] == b[audit['__init__']['audit_json']['used_pref_array'][i]])


def test_ability_array_point_buy_one_max():
    ctx = Ctx(app_username='Testing')
    comp_array = [15, 12, 12, 12, 11, 11]
    a = AbilityArray(ctx=ctx, array_type="point_buy_one_max")
    b = a.get_raw_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'point_buy_one_max')
    for i in range(0, 6):
        assert(comp_array[i] == b[i])

def test_ability_array_point_buy_two_max():
    ctx = Ctx(app_username='Testing')
    comp_array = [15, 15, 11, 10, 10, 10]
    a = AbilityArray(ctx=ctx, array_type="point_buy_two_max")
    b = a.get_raw_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'point_buy_two_max')
    for i in range(0, 6):
        assert(comp_array[i] == b[i])

def test_ability_array_point_buy_three_max():
    ctx = Ctx(app_username='Testing')
    comp_array = [15, 15, 15, 8, 8, 8]
    a = AbilityArray(ctx=ctx, array_type="point_buy_three_max")
    b = a.get_raw_array()
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'point_buy_three_max')
    for i in range(0, 6):
        assert(comp_array[i] == b[i])