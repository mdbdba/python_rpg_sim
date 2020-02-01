import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PlayerCharacterClass import PlayerCharacterClass    # NOQA
from Ctx import Ctx   # NOQA
from BardPCClass import BardPCClass    # NOQA
from BarbarianPCClass import BarbarianPCClass    # NOQA
from ClericPCClass import ClericPCClass    # NOQA
from DruidPCClass import DruidPCClass    # NOQA
from FighterPCClass import FighterPCClass    # NOQA
from MonkPCClass import MonkPCClass    # NOQA
from PaladinPCClass import PaladinPCClass    # NOQA
from RangerPCClass import RangerPCClass    # NOQA
from RoguePCClass import RoguePCClass    # NOQA
from SorcererPCClass import SorcererPCClass    # NOQA
from WarlockPCClass import WarlockPCClass    # NOQA
from WizardPCClass import WizardPCClass    # NOQA
from InvokePSQL import InvokePSQL    # NOQA


def test_class_default():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = PlayerCharacterClass(db=db, ctx=ctx)
    assert(len(a.name) > 3)


def test_class_barbarian():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = BarbarianPCClass(db=db, ctx=ctx)
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
    assert(a.background == "Outlander")


def test_class_bard():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = BardPCClass(db=db, ctx=ctx)
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
    assert(a.background == "Entertainer")


def test_class_cleric():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = ClericPCClass(db=db, ctx=ctx)
    assert(a.name == 'Cleric')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [4, 2, 0, 1, 5, 3])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Divine Domain')
    assert(a.ranged_weapon == "Crossbow, light")
    assert(a.melee_weapon == "Warhammer")
    assert(a.ranged_ammunition_type == "Bolt")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor == "Scale mail")
    assert(a.shield == "Shield")
    assert(a.background == "Acolyte")


def test_class_druid():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = DruidPCClass(db=db, ctx=ctx)
    assert(a.name == 'Druid')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [4, 2, 1, 3, 5, 0])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Druid Circle')
    assert(a.ranged_weapon is None)
    assert(a.melee_weapon == "Scimitar")
    assert(a.ranged_ammunition_type is None)
    assert(a.ranged_ammunition_amt == 0)
    assert(a.armor == "Leather")
    assert(a.shield == "Shield")
    assert(a.background == "Hermit")


def test_class_fighter():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = FighterPCClass(db=db, ctx=ctx)
    assert(a.name == 'Fighter')
    assert(a.hit_die == 10)
    assert(a.ability_sort_array == [0, 2, 1, 5, 4, 3])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Martial Archetype')
    assert(a.ranged_weapon == "Crossbow, light")
    assert(a.melee_weapon == "Glaive")
    assert(a.ranged_ammunition_type == "Bolt")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor == "Chain mail")
    assert(a.shield is None)
    assert(a.background == "Soldier")


def test_class_monk():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = MonkPCClass(db=db, ctx=ctx)
    assert(a.name == 'Monk')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [1, 4, 2, 0, 3, 5])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Monastic Tradition')
    assert(a.ranged_weapon == "Dart")
    assert(a.melee_weapon == "Shortsword")
    assert(a.ranged_ammunition_type == "Dart")
    assert(a.ranged_ammunition_amt == 10)
    assert(a.armor is None)
    assert(a.shield is None)
    assert(a.background == "Hermit")


def test_class_paladin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = PaladinPCClass(db=db, ctx=ctx)
    assert(a.name == 'Paladin')
    assert(a.hit_die == 10)
    assert(a.ability_sort_array == [0, 5, 2, 4, 1, 3])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Sacred Oath')
    assert(a.ranged_weapon == "Javelin")
    assert(a.melee_weapon == "Greataxe")
    assert(a.ranged_ammunition_type == "Javelin")
    assert(a.ranged_ammunition_amt == 5)
    assert(a.armor == "Chain mail")
    assert(a.shield is None)
    assert(a.background == "Noble")


def test_class_ranger():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = RangerPCClass(db=db, ctx=ctx)
    assert(a.name == 'Ranger')
    assert(a.hit_die == 10)
    assert(a.ability_sort_array == [1, 4, 2, 0, 3, 5])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Ranger Archetype')
    assert(a.ranged_weapon == "Longbow")
    assert(a.melee_weapon == "Shortsword")
    assert(a.melee_weapon_offhand == "Shortsword")
    assert(a.ranged_ammunition_type == "Arrow")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor == "Leather")
    assert(a.shield is None)
    assert(a.background == "Outlander")


def test_class_rogue():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = RoguePCClass(db=db, ctx=ctx)
    assert(a.name == 'Rogue')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [1, 5, 2, 3, 0, 4])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Roguish Archetype')
    assert(a.ranged_weapon == "Shortbow")
    assert(a.melee_weapon == "Rapier")
    assert(a.melee_weapon_offhand == "Dagger")
    assert(a.ranged_ammunition_type == "Arrow")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor == "Leather")
    assert(a.background == "Charlatan")
    assert(a.shield is None)


def test_class_sorcerer():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = SorcererPCClass(db=db, ctx=ctx)
    assert(a.name == 'Sorcerer')
    assert(a.hit_die == 6)
    assert(a.ability_sort_array == [5, 2, 1, 4, 3, 0])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Sorcerous Origin')
    assert(a.ranged_weapon == "Crossbow, light")
    assert(a.melee_weapon == "Dagger")
    assert(a.melee_weapon_offhand == "Dagger")
    assert(a.ranged_ammunition_type == "Bolt")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor is None)
    assert(a.shield is None)
    assert(a.background == "Hermit")


def test_class_warlock():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = WarlockPCClass(db=db, ctx=ctx)
    assert(a.name == 'Warlock')
    assert(a.hit_die == 8)
    assert(a.ability_sort_array == [5, 2, 1, 4, 3, 0])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Otherworldly Patron')
    assert(a.ranged_weapon == "Crossbow, light")
    assert(a.melee_weapon == "Dagger")
    assert(a.melee_weapon_offhand == "Dagger")
    assert(a.ranged_ammunition_type == "Bolt")
    assert(a.ranged_ammunition_amt == 20)
    assert(a.armor == "Leather")
    assert(a.shield is None)
    assert(a.background == "Charlatan")


def test_class_wizard():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = WizardPCClass(db=db, ctx=ctx)
    assert(a.name == 'Wizard')
    assert(a.hit_die == 6)
    assert(a.ability_sort_array == [3, 1, 2, 4, 0, 5])
    assert(a.source_material == 'SRD5')
    assert(a.archetype_label == 'Arcane Tradition')
    assert(a.ranged_weapon is None)
    assert(a.melee_weapon == "Dagger")
    assert(a.ranged_ammunition_type is None)
    assert(a.ranged_ammunition_amt == 0)
    assert(a.armor is None)
    assert(a.shield is None)
    assert(a.background == "Sage")
