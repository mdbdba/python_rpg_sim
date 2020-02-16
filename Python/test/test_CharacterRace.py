import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from CharacterRace import CharacterRace    # NOQA
from InvokePSQL import InvokePSQL    # NOQA
from Ctx import Ctx    # NOQA


# add tests for random racial traits here
def test_getAlignment():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx)
    alignmentObj = a.get_alignment(db=db)
    assert(len(a.race) > 3)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)


# add tests for specific race types below, including random
def test_Race_Default():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx)
    assert(len(a.race) > 3)
    assert(any([v != 0 for v in a.ability_bonuses]))


def test_Race_Default_noRASM():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Random', use_rasm_ind=False)
    assert(all([v == 0 for v in a.ability_bonuses]))


def test_Race_Case():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='high elf')
    assert(a.race == 'High elf')


def test_Race_Highelf():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='High elf')
    assert(a.race == 'High elf')
    darkvision_ind = 0
    fey_ancestry_ind = 0
    cantrip_ind = 0
    extra_language_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Fey Ancestry'):
            fey_ancestry_ind = 1
        if (b.trait_name == 'Cantrip'):
            cantrip_ind = 1
        if (b.trait_name == 'Extra Language'):
            extra_language_ind = 1
    assert(darkvision_ind == 1)
    assert(fey_ancestry_ind == 1)
    assert(cantrip_ind == 1)
    assert(extra_language_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Hilldwarf():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Hill dwarf')
    assert(a.race == 'Hill dwarf')
    darkvision_ind = 0
    dwarven_resillience_ind = 0
    dwarven_toughness_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Dwarven Resilience'):
            dwarven_resillience_ind = 1
        if (b.trait_name == 'Dwarven Toughness'):
            dwarven_toughness_ind = 1
    assert(darkvision_ind == 1)
    assert(dwarven_resillience_ind == 1)
    assert(dwarven_toughness_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Lightfoothalfling():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Lightfoot halfling')
    assert(a.race == 'Lightfoot halfling')
    brave_ind = 0
    halfling_nimbleness_ind = 0
    lucky_ind = 0
    naturally_stealthy_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Brave'):
            brave_ind = 1
        if (b.trait_name == 'Halfling Nimbleness'):
            halfling_nimbleness_ind = 1
        if (b.trait_name == 'Lucky'):
            lucky_ind = 1
        if (b.trait_name == 'Naturally Stealthy'):
            naturally_stealthy_ind = 1
    assert(brave_ind == 1)
    assert(halfling_nimbleness_ind == 1)
    assert(lucky_ind == 1)
    assert(naturally_stealthy_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Mountaindwarf():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Mountain dwarf')
    assert(a.race == 'Mountain dwarf')
    darkvision_ind = 0
    dwarven_resillience_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Dwarven Resilience'):
            dwarven_resillience_ind = 1
    assert(darkvision_ind == 1)
    assert(dwarven_resillience_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Woodelf():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Wood elf')
    assert(a.race == 'Wood elf')
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Stouthalfling():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Stout halfling')
    assert(a.race == 'Stout halfling')
    brave_ind = 0
    halfling_nimbleness_ind = 0
    lucky_ind = 0
    stout_resilience_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Brave'):
            brave_ind = 1
        if (b.trait_name == 'Halfling Nimbleness'):
            halfling_nimbleness_ind = 1
        if (b.trait_name == 'Lucky'):
            lucky_ind = 1
        if (b.trait_name == 'Stout Resilience'):
            stout_resilience_ind = 1
    assert(brave_ind == 1)
    assert(halfling_nimbleness_ind == 1)
    assert(lucky_ind == 1)
    assert(stout_resilience_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Halfelf():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Half-Elf')
    assert(a.race == 'Half-Elf')
    darkvision_ind = 0
    fey_ancestry_ind = 0
    skill_versatility_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Fey Ancestry'):
            fey_ancestry_ind = 1
        if (b.trait_name == 'Skill Versatility'):
            skill_versatility_ind = 1
    assert(darkvision_ind == 1)
    assert(fey_ancestry_ind == 1)
    assert(skill_versatility_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


# test the case that a random subrace will be chosen
def test_Race_Dragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Dragonborn')
    assert(a.race.find('dragonborn'))
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Blackdragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Black dragonborn')
    assert(a.race == 'Black dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Black'):
                draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Bluedragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Blue dragonborn')
    assert(a.race == 'Blue dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Blue'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Brassdragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Brass dragonborn')
    assert(a.race == 'Brass dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Brass'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Bronzedragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Bronze dragonborn')
    assert(a.race == 'Bronze dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Bronze'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Copperdragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Copper dragonborn')
    assert(a.race == 'Copper dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Copper'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Golddragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Gold dragonborn')
    assert(a.race == 'Gold dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Gold'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Greendragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Green dragonborn')
    assert(a.race == 'Green dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Green'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Reddragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Red dragonborn')
    assert(a.race == 'Red dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Red'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Silverdragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Silver dragonborn')
    assert(a.race == 'Silver dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - Silver'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Whitedragonborn():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='White dragonborn')
    assert(a.race == 'White dragonborn')
    draconic_ancestry_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Draconic Ancestry'
           and b.affected_name == 'Dragonborn Breath Weapon - White'):
            draconic_ancestry_ind = 1
    assert(draconic_ancestry_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Rockgnome():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Rock gnome')
    assert(a.race == 'Rock gnome')
    darkvision_ind = 0
    gnome_cunning_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Gnome Cunning'):
            gnome_cunning_ind = 1
    assert(darkvision_ind == 1)
    assert(gnome_cunning_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_HalfOrc():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Half-Orc')
    assert(a.race == 'Half-Orc')
    darkvision_ind = 0
    relentless_ind = 0
    savage_attacks_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Relentless'):
            relentless_ind = 1
        if (b.trait_name == 'Savage Attacks'):
            savage_attacks_ind = 1
    assert(darkvision_ind == 1)
    assert(relentless_ind == 1)
    assert(savage_attacks_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Tiefling():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Tiefling')
    assert(a.race == 'Tiefling')
    darkvision_ind = 0
    hellish_resistance_ind = 0
    infernal_legacy_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Hellish Resistance'):
            hellish_resistance_ind = 1
        if (b.trait_name == 'Infernal Legacy'):
            infernal_legacy_ind = 1
    assert(darkvision_ind == 1)
    assert(hellish_resistance_ind == 1)
    assert(infernal_legacy_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Centaur():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Centaur')
    assert(a.race == 'Centaur')
    charge_ind = 0
    hybrid_nature_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Charge'):
            charge_ind = 1
        if (b.trait_name == 'Hybrid Nature'):
            hybrid_nature_ind = 1
    assert(charge_ind == 1)
    assert(hybrid_nature_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Blackbearkin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Black bearkin')
    assert(a.race == 'Black bearkin')
    darkvision_ind = 0
    keen_smell_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Keen Smell'):
            keen_smell_ind = 1
    assert(darkvision_ind == 1)
    assert(keen_smell_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Brownbearkin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Brown bearkin')
    assert(a.race == 'Brown bearkin')
    keen_smell_ind = 0
    protector_ind = 0
    powerful_build_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Keen Smell'):
            keen_smell_ind = 1
        if (b.trait_name == 'Protector'):
            protector_ind = 1
        if (b.trait_name == 'Powerful Build'):
            powerful_build_ind = 1
    assert(keen_smell_ind == 1)
    assert(protector_ind == 1)
    assert(powerful_build_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Koalabearkin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Koala bearkin')
    assert(a.race == 'Koala bearkin')
    keen_smell_ind = 0
    bear_drop_ind = 0
    iron_tummy_ind = 0
    tree_born_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Keen Smell'):
            keen_smell_ind = 1
        if (b.trait_name == 'Bear Drop'):
            bear_drop_ind = 1
        if (b.trait_name == 'Iron Tummy'):
            iron_tummy_ind = 1
        if (b.trait_name == 'Tree Born'):
            tree_born_ind = 1
    assert(keen_smell_ind == 1)
    assert(bear_drop_ind == 1)
    assert(iron_tummy_ind == 1)
    assert(tree_born_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Pandabearkin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Panda bearkin')
    assert(a.race == 'Panda bearkin')
    keen_smell_ind = 0
    plant_spirit_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Keen Smell'):
            keen_smell_ind = 1
        if (b.trait_name == 'Plant Spirit'):
            plant_spirit_ind = 1
    assert(keen_smell_ind == 1)
    assert(plant_spirit_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Polarbearkin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Polar bearkin')
    assert(a.race == 'Polar bearkin')
    keen_smell_ind = 0
    winter_hide_ind = 0
    history_of_violence_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Keen Smell'):
            keen_smell_ind = 1
        if (b.trait_name == 'Winter Hide'):
            winter_hide_ind = 1
        if (b.trait_name == 'History of Violence'):
            history_of_violence_ind = 1
    assert(keen_smell_ind == 1)
    assert(winter_hide_ind == 1)
    assert(history_of_violence_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Burrowskobold():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Burrows kobold')
    assert(a.race == 'Burrows kobold')
    darkvision_ind = 0
    pack_tactics_ind = 0
    slim_build_ind = 0
    sunlight_sensitivity_ind = 0
    ambusher_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Pack Tactics'):
            pack_tactics_ind = 1
        if (b.trait_name == 'Slim Build'):
            slim_build_ind = 1
        if (b.trait_name == 'Sunlight Sensitivity'):
            sunlight_sensitivity_ind = 1
        if (b.trait_name == 'Ambusher'):
            ambusher_ind = 1
    assert(darkvision_ind == 1)
    assert(pack_tactics_ind == 1)
    assert(slim_build_ind == 1)
    assert(sunlight_sensitivity_ind == 1)
    assert(ambusher_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Loredrakekobold():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Loredrake kobold')
    assert(a.race == 'Loredrake kobold')
    darkvision_ind = 0
    pack_tactics_ind = 0
    slim_build_ind = 0
    sunlight_sensitivity_ind = 0
    sorcerous_initiate_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Pack Tactics'):
            pack_tactics_ind = 1
        if (b.trait_name == 'Slim Build'):
            slim_build_ind = 1
        if (b.trait_name == 'Sunlight Sensitivity'):
            sunlight_sensitivity_ind = 1
        if (b.trait_name == 'Sorcerous Initiate'):
            sorcerous_initiate_ind = 1
    assert(darkvision_ind == 1)
    assert(pack_tactics_ind == 1)
    assert(slim_build_ind == 1)
    assert(sunlight_sensitivity_ind == 1)
    assert(sorcerous_initiate_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Wingedkobold():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Winged kobold')
    assert(a.race == 'Winged kobold')
    darkvision_ind = 0
    pack_tactics_ind = 0
    slim_build_ind = 0
    sunlight_sensitivity_ind = 0
    flying_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Pack Tactics'):
            pack_tactics_ind = 1
        if (b.trait_name == 'Slim Build'):
            slim_build_ind = 1
        if (b.trait_name == 'Sunlight Sensitivity'):
            sunlight_sensitivity_ind = 1
        if (b.trait_name == 'Flying'):
            flying_ind = 1
    assert(darkvision_ind == 1)
    assert(pack_tactics_ind == 1)
    assert(slim_build_ind == 1)
    assert(sunlight_sensitivity_ind == 1)
    assert(flying_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Greenskingoblin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Greenskin goblin')
    assert(a.race == 'Greenskin goblin')
    darkvision_ind = 0
    nimble_escape_ind = 0
    mud_slinger_ind = 0
    run_for_it_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Nimble Escape'):
            nimble_escape_ind = 1
        if (b.trait_name == 'Mud Slinger'):
            mud_slinger_ind = 1
        if (b.trait_name == 'Run For It'):
            run_for_it_ind = 1
    assert(darkvision_ind == 1)
    assert(nimble_escape_ind == 1)
    assert(mud_slinger_ind == 1)
    assert(run_for_it_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Boggartgoblin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Boggart goblin')
    assert(a.race == 'Boggart goblin')
    darkvision_ind = 0
    nimble_escape_ind = 0
    swamp_immunity_ind = 0
    bog_swimmer_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Nimble Escape'):
            nimble_escape_ind = 1
        if (b.trait_name == 'Swamp Immunity'):
            swamp_immunity_ind = 1
        if (b.trait_name == 'Bog Swimmer'):
            bog_swimmer_ind = 1
    assert(darkvision_ind == 1)
    assert(nimble_escape_ind == 1)
    assert(swamp_immunity_ind == 1)
    assert(bog_swimmer_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Gremlingoblin():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Gremlin goblin')
    assert(a.race == 'Gremlin goblin')
    darkvision_ind = 0
    nimble_escape_ind = 0
    dangerous_tinker_ind = 0
    almost_fire_proof_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Nimble Escape'):
            nimble_escape_ind = 1
        if (b.trait_name == 'Dangerous Tinker'):
            dangerous_tinker_ind = 1
        if (b.trait_name == 'Almost Fire Proof'):
            almost_fire_proof_ind = 1
    assert(darkvision_ind == 1)
    assert(nimble_escape_ind == 1)
    assert(dangerous_tinker_ind == 1)
    assert(almost_fire_proof_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))


def test_Race_Dryad():
    ctx = Ctx(app_username='Testing')
    db = InvokePSQL()
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Dryad')
    assert(a.race == 'Dryad')
    darkvision_ind = 0
    speak_with_beasts_and_plants_ind = 0
    fey_blessing_ind = 0
    woodland_magic_ind = 0
    forest_step_ind = 0
    treebound_armor_ind = 0
    for b in a.traitContainer.traits:
        if (b.trait_name == 'Darkvision'):
            darkvision_ind = 1
        if (b.trait_name == 'Speak with Beasts and Plants'):
            speak_with_beasts_and_plants_ind = 1
        if (b.trait_name == 'Fey Blessing'):
            fey_blessing_ind = 1
        if (b.trait_name == 'Woodland Magic'):
            woodland_magic_ind = 1
        if (b.trait_name == 'Forest Step'):
            forest_step_ind = 1
        if (b.trait_name == 'Treebound Armor'):
            treebound_armor_ind = 1

    assert(darkvision_ind == 1)
    assert(speak_with_beasts_and_plants_ind == 1)
    assert(fey_blessing_ind == 1)
    assert(woodland_magic_ind == 1)
    assert(forest_step_ind == 1)
    assert(treebound_armor_ind == 1)
    assert(any([v != 0 for v in a.ability_bonuses]))
    alignmentObj = a.get_alignment(db=db)
    assert('abbreviation' in alignmentObj)
    assert('alignment' in alignmentObj)
    assert(a.get_skin_tone(db=db))
    assert(a.get_hair_color(db=db))
    assert(a.get_hair_type(db=db))
    assert(a.get_eye_color(db=db))
    assert(a.get_name(db=db, gender='U'))
