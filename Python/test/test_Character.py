import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from PlayerCharacter import PlayerCharacter    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from CommonFunctions import arrayToString, stringToArray    # NOQA
from CommonFunctions import compareArrays    # NOQA


def test_Character_Default():
    db = InvokePSQL()
    a1 = PlayerCharacter(db)
    assert(a1)
    assert(a1.getName())
    assert(a1.ability_base_array)
    assert(a1.level)
    assert(a1.getHeight())
    assert(a1.getWeight())
    assert(a1.getAlignmentStr())
    assert(a1.getAlignmentAbbrev())
    assert(a1.getSkinTone())
    assert(a1.getHairColor())
    assert(a1.getHairType())
    assert(a1.getEyeColor())
    assert(a1.blinded_ind is False)
    assert(a1.charmed_ind is False)
    assert(a1.deafend_ind is False)
    assert(a1.fatigued_ind is False)
    assert(a1.frightened_ind is False)
    assert(a1.grappled_ind is False)
    assert(a1.incapacitated_ind is False)
    assert(a1.invisible_ind is False)
    assert(a1.paralyzed_ind is False)
    assert(a1.petrified_ind is False)
    assert(a1.poisoned_ind is False)
    assert(a1.prone_ind is False)
    assert(a1.stunned_ind is False)
    assert(a1.unconcious_ind is False)
    assert(a1.exhaustion_level == 0)
    assert(a1.cur_movement > 10)


def test_Character_Strict():
    db = InvokePSQL()
    a1 = PlayerCharacter(db, abilityArrayStr="Strict")
    assert(a1)
    assert(a1.ability_base_array)


def test_Race_Standard_Array():
    db = InvokePSQL()
#    compArray = [15, 14, 13, 12, 10, 8]
    found15 = False
    found14 = False
    found13 = False
    found12 = False
    found10 = False
    found8 = False

    a1 = PlayerCharacter(db, abilityArrayStr="Standard")
    assert(a1)
    for i in range(0, 6):
        if a1.ability_base_array[i] == 15:
            found15 = True
        elif a1.ability_base_array[i] == 14:
            found14 = True
        elif a1.ability_base_array[i] == 13:
            found13 = True
        elif a1.ability_base_array[i] == 12:
            found12 = True
        elif a1.ability_base_array[i] == 10:
            found10 = True
        elif a1.ability_base_array[i] == 8:
            found8 = True

    assert(found15)
    assert(found14)
    assert(found13)
    assert(found12)
    assert(found10)
    assert(found8)
    # assert(compArray[i] == a1.ability_base_array[i])


def test_Character_Dwarf_Barbarian():
    db = InvokePSQL()
    a1 = PlayerCharacter(db,
                         raceCandidate="Mountain dwarf",
                         classCandidate="Barbarian")
    assert(a1)
    assert(a1.getRace() == "Mountain dwarf")
    assert(a1.getClass() == "Barbarian")
    assert(a1.classObj.hit_die == 12)
    assert(a1.getName())
    assert(a1.ability_base_array)
    assert(a1.level)
    assert(a1.getHeight())
    assert(a1.getWeight())
    assert(a1.getAlignmentStr())
    assert(a1.getAlignmentAbbrev())
    assert(a1.getSkinTone())
    assert(a1.getHairColor())
    assert(a1.getHairType())
    assert(a1.getEyeColor())
    assert(a1.melee_weapon_obj.name == 'Greataxe')
    assert(a1.ranged_weapon_obj.name == 'Javelin')


def test_Character_Halfling_Bard():
    db = InvokePSQL()
    a1 = PlayerCharacter(db,
                         raceCandidate="Stout halfling",
                         classCandidate="Bard")
    assert(a1)
    assert(a1.getRace() == "Stout halfling")
    assert(a1.getClass() == "Bard")
    assert(a1.classObj.hit_die == 8)
    assert(a1.getName())
    assert(a1.ability_base_array)
    assert(a1.level)
    assert(a1.getHeight())
    assert(a1.getWeight())
    assert(a1.getAlignmentStr())
    assert(a1.getAlignmentAbbrev())
    assert(a1.getSkinTone())
    assert(a1.getHairColor())
    assert(a1.getHairType())
    assert(a1.getEyeColor())
    assert(a1.melee_weapon_obj.name == 'Rapier')


def test_RandomGen_Retrieve():
    db = InvokePSQL()
    a1 = PlayerCharacter(db)
    b1 = PlayerCharacter(db, characterId=a1.character_id)
    assert(a1)
    assert(b1)
    assert(a1.level == b1.level)
    assert(a1.getRace() == b1.getRace())
    assert(a1.getClass() == b1.getClass())
    assert(a1.getGender() == b1.getGender())
    assert(a1.TTA == b1.TTA)
    assert(a1.getName() == b1.getName())
    assert(a1.armor_class == b1.armor_class)

    assert(compareArrays(a1.ability_base_array, b1.ability_base_array))
    assert(compareArrays(a1.ability_array, b1.ability_array))
    assert(compareArrays(a1.ability_modifier_array, b1.ability_modifier_array))
    assert(compareArrays(a1.ability_array_obj.ability_label_array,
                         b1.ability_array_obj.ability_label_array))

    assert(a1.hit_points == b1.hit_points)
    assert(a1.temp_hit_points == b1.temp_hit_points)
    assert(a1.cur_hit_points == b1.cur_hit_points)
    assert(a1.getHeight() == b1.getHeight())
    assert(a1.getWeight() == b1.getWeight())
    assert(a1.getAlignmentStr() == b1.getAlignmentStr())
    assert(a1.getAlignmentAbbrev() == b1.getAlignmentAbbrev())
    assert(a1.getSkinTone() == b1.getSkinTone())
    assert(a1.getHairColor() == b1.getHairColor())
    assert(a1.getHairType() == b1.getHairType())
    assert(a1.getEyeColor() == b1.getEyeColor())


def test_Character_Poison_Resistance():
    db = InvokePSQL()
    a1 = PlayerCharacter(db,
                         raceCandidate="Mountain Dwarf",
                         classCandidate="Barbarian")
    assert(a1)
    assert(a1.getRace() == "Mountain dwarf")
    assert(a1.getClass() == "Barbarian")
    assert(a1.classObj.hit_die == 12)
    assert(a1.damage_adj['Poison'] == 'resistant')
    a1.Damage(6, 'Poison')
    assert(a1.cur_hit_points == (a1.hit_points - 3))


def test_Character_Death():
    db = InvokePSQL()
    a1 = PlayerCharacter(db,
                         abilityArrayStr="18,12,12,10,10,8",
                         raceCandidate="Mountain Dwarf",
                         classCandidate="Barbarian")
    assert(a1)
    assert(a1.getRace() == "Mountain dwarf")
    assert(a1.getClass() == "Barbarian")
    assert(a1.classObj.hit_die == 12)
    a1.meleeDefend(modifier=13, possibleDamage=a1.hit_points,
                   damageType='Bludgeoning')

    assert(a1.alive is True)
    assert(a1.stabilized is False)
    a1.Heal(10)
    assert(a1.cur_hit_points == 10)
    assert(a1.alive is True)
    assert(a1.stabilized is True)
    a1.meleeDefend(modifier=13, possibleDamage=(2 * a1.hit_points),
                   damageType='Bludgeoning')
    assert(a1.alive is False)


def test_Character_Checks():
    db = InvokePSQL()
    a1 = PlayerCharacter(db,
                         abilityArrayStr="18,12,12,10,10,8",
                         raceCandidate="Mountain Dwarf",
                         classCandidate="Barbarian")
    assert(a1)
    assert(a1.getRace() == "Mountain dwarf")
    assert(a1.getClass() == "Barbarian")
    assert(a1.finesse_ability_mod == 'Strength')
    assert(a1.classObj.hit_die == 12)
    res = a1.Check('Strength', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Strength', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Strength', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Dexterity', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Dexterity', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Dexterity', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Constitution', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Constitution', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Constitution', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Intelligence', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Intelligence', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Intelligence', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Wisdom', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Wisdom', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Wisdom', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Charisma', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Charisma', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Charisma', 'Disadvantage', 10)

    assert(res is True or res is False)
    res = a1.Check('Athletics', 'Normal', 5)
    assert(res is True or res is False)
    res = a1.Check('Athletics', 'Advantage', 15)
    assert(res is True or res is False)
    res = a1.Check('Athletics', 'Disadvantage', 10)


