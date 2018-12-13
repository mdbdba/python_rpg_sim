import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PlayerCharacterClass import PlayerCharacterClass    # NOQA
#from Common.InvokePSQL import InvokePSQL    # NOQA
from PlayerCharacterClass import BardClass    # NOQA
from PlayerCharacterClass import BarbarianClass    # NOQA
from InvokePSQL import InvokePSQL    # NOQA


def test_Class_Default():
    db = InvokePSQL()
    a = PlayerCharacterClass(db)
    assert(len(a.name) > 3)


def test_Class_Barbarian():
    db = InvokePSQL()
    a = BarbarianClass(db)
    assert(a.name == 'Barbarian')
    assert(a.hit_die == 12)
    assert(a.ability_sort_array == [0, 2, 1, 4, 5, 3])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Primal Path')
    assert(a.ranged_weapon == "Javelin")
    assert(a.melee_weapon == "Greataxe")
    assert(a.ranged_ammunition_type == "Javelin")
    assert(a.ranged_ammunition_amt == 4)
    assert(a.armor is None)
    assert(a.shield is None)


def test_Class_Bard():
    db = InvokePSQL()
    a = BardClass(db)
    assert(a.name == 'Bard')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [5, 1, 2, 0, 4, 3])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Bard College')
    assert(a.ranged_weapon == "Dagger")
    assert(a.melee_weapon == "Rapier")
    assert(a.ranged_ammunition_type == "Dagger")
    assert(a.ranged_ammunition_amt == 1)
    assert(a.armor == "Leather")
    assert(a.shield is None)
