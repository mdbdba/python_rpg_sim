import random
from InvokePSQL import InvokePSQL
from RacialTraits import RacialTraits
from Die import Die


class CharacterRace(object):
    def __init__(self, db, raceCandidate="Random", useRASMInd=True):
        self.use_rasm_ind = useRASMInd
        self.race = ""
        self.subrace_of = ""
        self.maturity_age = -999
        self.avg_max_age = -999
        self.base_walking_speed = -999
        self.height_min_inches = -999
        self.height_modifier_multiplier = -999
        self.height_modifier_die = -999
        self.height_modifier_adj = -999
        self.weight_min_pounds = -999
        self.weight_modifier_multiplier = -999
        self.weight_modifier_die = -999
        self.weight_modifier_adj = -999
        self.size = ""
        self.source_material = ""
        self.source_credit_url = ""
        self.source_credit_comment = ""
        self.traitContainer = []
        self.proficient = []
        self.proficient_source = []
        self.languages = []
        # Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
        self.ability_bonuses = [0, 0, 0, 0, 0, 0]

        self.name = None
        self.alignment = None
        self.skinTone = None
        self.hairColor = None
        self.hairType = None
        self.eyeColor = None
        self.height = None
        self.weight = None

        if raceCandidate == "Random":
            raceCandidate = self.getRandomRaceName(db)

        if self.validRaceName(raceCandidate, db):
            self.populateDetails(raceCandidate, db)
        else:
            if self.validParentRaceName(raceCandidate, db):
                raceCandidate = self.getRandomRaceName(db, raceCandidate)
                self.populateDetails(raceCandidate, db)
            else:
                raise Exception(f'Could not find race: {raceCandidate}')

    def getRandomRaceName(self, db, parentRace="None"):
        if parentRace == "None":
            sql = (f"with tb as (select distinct (case "
                   f"when subrace_of is null then race else subrace_of "
                   f"end) as race "
                   f"from lu_race) "
                   f"select race "
                   f"from tb "
                   f"order by random() "
                   f"limit 1")
        else:
            sql = (f"select count(race) from dnd_5e.lu_race "
                   f"where lower(subrace_of) = lower('{parentRace}')")

            results = db.query(sql)
            result = results[0][0]
            if (result > 1):
                randNbr = random.randint(1, result)
            else:
                randNbr = 1
            sql = (f"with tb as (select race, row_number() "
                   f"over (order by race) "
                   f"as orderBy from dnd_5e.lu_race "
                   f"where lower(subrace_of) = lower('{parentRace}')"
                   f") select race, orderby from tb "
                   f"where orderby = {randNbr}")

        results = db.query(sql)
        return results[0][0]

    def validRaceName(self, raceCandidate, db):
        sql = (f"select count(race) from dnd_5e.lu_race where "
               f"lower(race) = lower('{raceCandidate}');")
        results = db.query(sql)
        raceCnt = results[0][0]
        if raceCnt == 1:
            return True
        else:
            return False

    def validParentRaceName(self, raceCandidate, db):
        sql = (f"select count(subrace_of) from dnd_5e.lu_race where "
               f"lower(subrace_of) = lower('{raceCandidate}');")
        results = db.query(sql)
        raceCnt = results[0][0]
        if raceCnt >= 1:
            return True
        else:
            return False

    def getAlignment(self, db):
        """
        Preferred racial alignment is based on a percentage. So, generate
            a random percentage and pick the alignment that percentage belongs
            in.
        """
        d = Die(100)
        rndPct = d.roll()
        sql = (f"select count(alignment) from dnd_5e.v_alignment_preference "
               f"where race = '{self.race}';")
        cntResult = db.query(sql)
        if cntResult[0][0] > 0:
            useRace = self.race
        else:
            useRace = self.subrace_of

        sql = (f"select count(alignment) from dnd_5e.v_alignment_preference "
               f"where race = '{useRace}';")
        cntResult = db.query(sql)
        if cntResult[0][0] > 0:
            sql = (f"select b.abbreviation, b.value as alignment "
                   f"from dnd_5e.v_alignment_preference as a "
                   f"join lu_alignment as b on a.alignment = b.abbreviation "
                   f"where race = '{useRace}' "
                   f"and lowerbound < {rndPct} and upperbound >= {rndPct};")
            alignmentResults = db.query(sql)
            return {"abbreviation": alignmentResults[0][0],
                    "alignment": alignmentResults[0][1]}

    def tableRefRandom(self, db, tablename, columnname, value, gender="N"):
        sql = (f"select count({columnname}) from {tablename} "
               f"where {columnname} = '{value}'")
        if gender != "N":
            if gender == "U":
                genderstr = " = 'U'"
            else:
                genderstr = (f" in ('{gender}','U')")
            sql = (f"{sql} and gender {genderstr} ;")
        else:
            sql = (f"{sql};")
        results = db.query(sql)
        rMax = results[0][0]
        return random.randint(1, rMax)

    def getSkinTone(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_skin_tone "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        rNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_skin_tone',
                                   'race', tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_skin_tone "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {rNbr};")
        sRes = db.query(sql)
        return sRes[0][0]

    def getHairColor(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_hair_color "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        rNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_hair_color',
                                   'race', tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_hair_color "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {rNbr};")
        sRes = db.query(sql)
        return sRes[0][0]

    def getHairType(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_hair_type "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        rNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_hair_type',
                                   'race', tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_hair_type "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {rNbr};")
        sRes = db.query(sql)
        return sRes[0][0]

    def getEyeColor(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_eye_color "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        rNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_eye_color',
                                   'race', tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_eye_color "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {rNbr};")
        sRes = db.query(sql)
        return sRes[0][0]

    def getName(self, db, gender):
        firstName = ""
        d = Die(2)

        if self.race == 'Half-Elf':
            rndpick = d.roll()
            if rndpick == 1:
                tmprace = 'Human'
            else:
                tmprace = 'Elf'
        else:
            sql = (f"select count(id) from dnd_5e.lu_racial_first_name "
                   f"where race = '{self.race}' ")
            results = db.query(sql)
            if results[0][0] > 0:
                tmprace = self.race
            else:
                tmprace = self.subrace_of

        fNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_first_name',
                                   'race', tmprace, gender)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_first_name "
               f"where lower(race) = lower('{tmprace}') ")
        if gender == "U":
            genderstr = " = 'U'"
        else:
            genderstr = (f" in ('{gender}','U')")

        sql = (f"{sql} and gender {genderstr} )"
               f"select value, orderby from tb where orderby = {fNbr};")

        fRes = db.query(sql)
        firstName = fRes[0][0]

        if self.race == 'Half-Elf':
            rndpick = d.roll()
            if rndpick == 1:
                tmprace = 'Elf'
            else:
                tmprace = 'Human'

        lNbr = self.tableRefRandom(db, 'dnd_5e.lu_racial_last_name',
                                   'race', tmprace, gender)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_last_name "
               f"where lower(race) = lower('{tmprace}') ")
        if gender == "U":
            genderstr = " = 'U'"
        else:
            genderstr = (f" in ('{gender}','U')")

        sql = (f"{sql} and gender {genderstr} )"
               f"select value, orderby from tb where orderby = {lNbr};")

        lres = db.query(sql)
        if (lres[0][0] == "None"):
            retstr = firstName
        else:
            retstr = (f"{firstName} {lres[0][0]}")

        return retstr

    def setRandoms(self, db=None,
                   name=None,
                   alignment=None,
                   skinTone=None,
                   hairColor=None,
                   hairType=None,
                   eyeColor=None,
                   gender=None):
        if (gender):
            self.name = self.getName(db, gender)
            self.alignment = self.getAlignment(db)
            self.skinTone = self.getSkinTone(db)
            self.hairColor = self.getHairColor(db)
            self.hairType = self.getHairType(db)
            self.eyeColor = self.getEyeColor(db)
        else:
            self.name = name
            self.alignment = alignment
            self.skinTone = skinTone
            self.hairColor = hairColor
            self.hairType = hairType
            self.eyeColor = eyeColor

    def populateDetails(self, raceCandidate, db):
        sql = (f"select race, subrace_of, maturity_age, avg_max_age, "
               f"base_walking_speed, height_min_inches, "
               f"height_modifier_multiplier, height_modifier_die, "
               f"height_modifier_adj, weight_min_pounds, "
               f"weight_modifier_multiplier, weight_modifier_die, "
               f'weight_modifier_adj, "size", source_material, '
               f"source_credit_url, source_credit_comment "
               f"from dnd_5e.lu_race where "
               f"lower(race) = lower('{raceCandidate}');")
        results = db.query(sql)
        self.race = results[0][0] if results[0][0] else None
        self.subrace_of = results[0][1] if results[0][1] else None
        self.maturity_age = results[0][2] if results[0][2] else None
        self.avg_max_age = results[0][3] if results[0][3] else None
        self.base_walking_speed = results[0][4] if results[0][4] else None
        self.height_min_inches = results[0][5] if results[0][5] else None
        self.height_modifier_multiplier = results[0][6] if results[0][6] \
            else None
        self.height_modifier_die = results[0][7] if results[0][7] \
            else None
        self.height_modifier_adj = results[0][8] if results[0][8] \
            else None
        self.weight_min_pounds = results[0][9] if results[0][9] \
            else None
        self.weight_modifier_multiplier = results[0][10] if results[0][10] \
            else None
        self.weight_modifier_die = results[0][11] if results[0][11] \
            else None
        self.weight_modifier_adj = results[0][12] if results[0][12] \
            else None
        self.size = results[0][13] if results[0][13] \
            else None
        self.source_material = results[0][14] if results[0][14] \
            else None
        self.source_credit_url = results[0][15] if results[0][15] \
            else None
        self.source_credit_comment = results[0][16] if results[0][16] \
            else None

        langSql = (f"select language from dnd_5e.lu_racial_language "
                   f"where lower(race) = lower('{self.race}') ")

        rasmSql = (f"select ability, modifier from "
                   f"dnd_5e.lu_racial_ability_score_modifier "
                   f"where lower(race) = lower('{self.race}') ")

        if self.subrace_of:
            self.traitContainer = RacialTraits(db, self.race, self.subrace_of)
            langSql = (f"{langSql} or lower(race) = "
                       f"lower('{self.subrace_of}') ")
            rasmSql = (f"{rasmSql} or lower(race) = "
                       f"lower('{self.subrace_of}') ")
        else:
            self.traitContainer = RacialTraits(db, self.race)

        if self.use_rasm_ind:
            rasm = db.query(rasmSql)
            for r in rasm:
                if r[0] == "Strength":
                    self.ability_bonuses[0] = r[1]
                if r[0] == "Dexterity":
                    self.ability_bonuses[1] = r[1]
                if r[0] == "Constitution":
                    self.ability_bonuses[2] = r[1]
                if r[0] == "Intelligence":
                    self.ability_bonuses[3] = r[1]
                if r[0] == "Wisdom":
                    self.ability_bonuses[4] = r[1]
                if r[0] == "Charisma":
                    self.ability_bonuses[5] = r[1]

        langs = db.query(langSql)
        for l in langs:
            self.languages.append(l[0])

        dh = Die(self.height_modifier_die)
        self.height = dh.getSum(self.height_min_inches,
                                self.height_modifier_multiplier)
        dw = Die(self.weight_modifier_die)
        self.weight = dw.getSum(self.weight_min_pounds,
                                self.weight_modifier_multiplier)

    def getRace(self):
        return self.race

    def __str__(self):
        outstr = (f'\nObject: {self.__class__.__name__}('
                  f'\n   Race:                       {self.race},'
                  f'\n   subrace_of:                 {self.subrace_of},'
                  f'\n   maturity_age:               {self.maturity_age},'
                  f'\n   avg_max_age:                {self.avg_max_age},'
                  f'\n   base_walking_speed:         '
                  f'{self.base_walking_speed},'
                  f'\n   height_min_inches:          {self.height_min_inches},'
                  f'\n   height_modifier_multiplier: '
                  f'{self.height_modifier_multiplier},'
                  f'\n   height_modifier_die:        '
                  f'{self.height_modifier_die},'
                  f'\n   height_modifier_adj:        '
                  f'{self.height_modifier_adj},'
                  f'\n   weight_min_pounds:          {self.weight_min_pounds},'
                  f'\n   weight_modifier_multiplier: '
                  f'{self.weight_modifier_multiplier},'
                  f'\n   weight_modifier_die:        '
                  f'{self.weight_modifier_die},'
                  f'\n   weight_modifier_adj:        '
                  f'{self.weight_modifier_adj},'
                  f'\n   size:                       {self.size},'
                  f'\n   source_material:            '
                  f'{self.source_material}')
        if self.source_credit_url:
            outstr = (f'{outstr},\n   source_credit_url:          '
                      f'{self.source_credit_url}')
        if self.source_credit_comment:
            outstr = (f'{outstr},\n   source_credit_comment:      '
                      f'{self.source_credit_comment}')

        if self.languages:
            outstr = (f'{outstr}\n\n   Languages:')
            for l in self.languages:
                outstr = (f'{outstr}\n       {l}')

        if self.traitContainer.proficient:
            outstr = (f'{outstr}\n\n   Proficiencies:')

            for p in range(len(self.traitContainer.proficient)):
                tmpprofstr = self.traitContainer.proficient[p].ljust(23)
                tmpsrcstr = self.traitContainer.proficient_source[p]
                outstr = (f'{outstr}\n       {tmpprofstr}'
                          f' ({tmpsrcstr})')

        for b in self.traitContainer.traits:
                if b.category != "Proficiency Skill":
                    outstr = (f'{outstr}\n {b}')

        outstr = (f'{outstr}\n)\n')
        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    a = CharacterRace(db, 'Dryad')
    alignmentObj = a.getAlignment(db)
    a.setRandoms(db=db, gender='M')
    print(a.race)
    print(alignmentObj)
    print(a.getSkinTone(db))
    print(a.getHairColor(db))
    print(a.getHairType(db))
    print(a.getEyeColor(db))
    print(a.getName(db, 'U'))
    for b in a.traitContainer.traits:
        print(b)

    print(a.name)
    print(a.alignment)
    print(a.skinTone)
    print(a.hairColor)
    print(a.hairType)
    print(a.eyeColor)
    print(a.height)
    print(a.weight)
