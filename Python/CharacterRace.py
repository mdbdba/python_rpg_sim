import random
from InvokePSQL import InvokePSQL
from RacialTraits import RacialTraits
from Die import Die
from Ctx import Ctx
from Ctx import ctx_decorator

class CharacterRace(object):
    @ctx_decorator
    def __init__(self, db, ctx, race_candidate="Random", use_rasm_ind=True):
        self.ctx = ctx
        self.use_rasm_ind = use_rasm_ind
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
        # self.traitContainer = []
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

        if race_candidate == "Random":
            race_candidate = self.get_random_race_name(db=db)

        if self.valid_race_name(db=db, race_candidate=race_candidate):
            self.populate_details(db=db, race_candidate=race_candidate)
        else:
            if self.valid_parent_race_name(db=db, race_candidate=race_candidate):
                race_candidate = self.get_random_race_name(db=db, parent_race=race_candidate)
                self.populate_details(db=db, race_candidate=race_candidate)
            else:
                raise Exception(f'Could not find race: {race_candidate}')

    @ctx_decorator
    def get_random_race_name(self, db, parent_race="None"):
        if parent_race == "None":
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
                   f"where lower(subrace_of) = lower('{parent_race}')")

            results = db.query(sql)
            result = results[0][0]
            if result > 1:
                rand_nbr = random.randint(1, result)
            else:
                rand_nbr = 1
            sql = (f"with tb as (select race, row_number() "
                   f"over (order by race) "
                   f"as orderBy from dnd_5e.lu_race "
                   f"where lower(subrace_of) = lower('{parent_race}')"
                   f") select race, orderby from tb "
                   f"where orderby = {rand_nbr}")

        results = db.query(sql)
        return results[0][0]

    @ctx_decorator
    def valid_race_name(self, db, race_candidate):
        sql = (f"select count(race) from dnd_5e.lu_race where "
               f"lower(race) = lower('{race_candidate}');")
        results = db.query(sql)
        race_cnt = results[0][0]
        if race_cnt == 1:
            return True
        else:
            return False

    @ctx_decorator
    def valid_parent_race_name(self, db, race_candidate):
        sql = (f"select count(subrace_of) from dnd_5e.lu_race where "
               f"lower(subrace_of) = lower('{race_candidate}');")
        results = db.query(sql)
        race_cnt = results[0][0]
        if race_cnt >= 1:
            return True
        else:
            return False

    @ctx_decorator
    def get_alignment(self, db):
        """
        Preferred racial alignment is based on a percentage. So, generate
            a random percentage and pick the alignment that percentage belongs
            in.
        """
        d = Die(ctx=self.ctx, sides=100)
        rnd_pct = d.roll()
        sql = (f"select count(alignment) from dnd_5e.v_alignment_preference "
               f"where race = '{self.race}';")
        cnt_result = db.query(sql)
        if cnt_result[0][0] > 0:
            use_race = self.race
        else:
            use_race = self.subrace_of

        sql = (f"select count(alignment) from dnd_5e.v_alignment_preference "
               f"where race = '{use_race}';")
        cnt_result = db.query(sql)
        if cnt_result[0][0] > 0:
            sql = (f"select b.abbreviation, b.value as alignment "
                   f"from dnd_5e.v_alignment_preference as a "
                   f"join lu_alignment as b on a.alignment = b.abbreviation "
                   f"where race = '{use_race}' "
                   f"and lowerbound < {rnd_pct} and upperbound >= {rnd_pct};")
            alignment_results = db.query(sql)
            return {"abbreviation": alignment_results[0][0],
                    "alignment": alignment_results[0][1]}

    @ctx_decorator
    def table_ref_random(self, db, tablename, columnname, value, gender="N"):
        sql = (f"select count({columnname}) from {tablename} "
               f"where {columnname} = '{value}'")
        if gender != "N":
            if gender == "U":
                genderstr = " = 'U'"
            else:
                genderstr = f" in ('{gender}','U')"
            sql = f"{sql} and gender {genderstr} ;"
        else:
            sql = f"{sql};"
        results = db.query(sql)
        r_max = results[0][0]
        return random.randint(1, r_max)

    @ctx_decorator
    def get_skin_tone(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_skin_tone "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        r_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_skin_tone',
                                      columnname='race', value=tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_skin_tone "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {r_nbr};")
        s_res = db.query(sql)
        return s_res[0][0]

    @ctx_decorator
    def get_hair_color(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_hair_color "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        r_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_hair_color',
                                      columnname='race', value=tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_hair_color "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {r_nbr};")
        s_res = db.query(sql)
        return s_res[0][0]

    @ctx_decorator
    def get_hair_type(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_hair_type "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        r_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_hair_type',
                                      columnname='race', value=tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_hair_type "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {r_nbr};")
        s_res = db.query(sql)
        return s_res[0][0]

    @ctx_decorator
    def get_eye_color(self, db):
        sql = (f"select count(id) from dnd_5e.lu_racial_eye_color "
               f"where race = '{self.race}' ")
        results = db.query(sql)
        if results[0][0] > 0:
            tmprace = self.race
        else:
            tmprace = self.subrace_of

        r_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_eye_color',
                                      columnname='race', value=tmprace)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_eye_color "
               f"where lower(race) = lower('{tmprace}') )"
               f"select value, orderby from tb where orderby = {r_nbr};")
        s_res = db.query(sql)
        return s_res[0][0]

    @ctx_decorator
    def get_name(self, db, gender):
        d = Die(ctx=self.ctx, sides=2)

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

        f_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_first_name',
                                      columnname='race', value=tmprace, gender=gender)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_first_name "
               f"where lower(race) = lower('{tmprace}') ")
        if gender == "U":
            genderstr = " = 'U'"
        else:
            genderstr = f" in ('{gender}','U')"

        sql = (f"{sql} and gender {genderstr} )"
               f"select value, orderby from tb where orderby = {f_nbr};")

        f_res = db.query(sql)
        first_name = f_res[0][0]

        if self.race == 'Half-Elf':
            rndpick = d.roll()
            if rndpick == 1:
                tmprace = 'Elf'
            else:
                tmprace = 'Human'

        l_nbr = self.table_ref_random(db=db, tablename='dnd_5e.lu_racial_last_name',
                                      columnname='race', value=tmprace, gender=gender)
        sql = (f"with tb as (select value, row_number() over "
               f"(partition by race order by id) "
               f"as orderBy from dnd_5e.lu_racial_last_name "
               f"where lower(race) = lower('{tmprace}') ")
        if gender == "U":
            genderstr = " = 'U'"
        else:
            genderstr = f" in ('{gender}','U')"

        sql = (f"{sql} and gender {genderstr} )"
               f"select value, orderby from tb where orderby = {l_nbr};")

        lres = db.query(sql)
        if lres[0][0] == "None":
            retstr = first_name
        else:
            retstr = f"{first_name} {lres[0][0]}"

        return retstr

    @ctx_decorator
    def set_randoms(self, db=None,
                    name=None,
                    alignment=None,
                    skin_tone=None,
                    hair_color=None,
                    hair_type=None,
                    eye_color=None,
                    gender=None):
        if gender:
            self.name = self.get_name(db=db, gender=gender)
            self.alignment = self.get_alignment(db=db)
            self.skinTone = self.get_skin_tone(db=db)
            self.hairColor = self.get_hair_color(db=db)
            self.hairType = self.get_hair_type(db=db)
            self.eyeColor = self.get_eye_color(db=db)
        else:
            self.name = name
            self.alignment = alignment
            self.skinTone = skin_tone
            self.hairColor = hair_color
            self.hairType = hair_type
            self.eyeColor = eye_color

    @ctx_decorator
    def populate_details(self, db, race_candidate):
        sql = (f"select race, subrace_of, maturity_age, avg_max_age, "
               f"base_walking_speed, height_min_inches, "
               f"height_modifier_multiplier, height_modifier_die, "
               f"height_modifier_adj, weight_min_pounds, "
               f"weight_modifier_multiplier, weight_modifier_die, "
               f'weight_modifier_adj, "size", source_material, '
               f"source_credit_url, source_credit_comment "
               f"from dnd_5e.lu_race where "
               f"lower(race) = lower('{race_candidate}');")
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

        lang_sql = (f"select language from dnd_5e.lu_racial_language "
                    f"where lower(race) = lower('{self.race}') ")

        rasm_sql = (f"select ability, modifier from "
                    f"dnd_5e.lu_racial_ability_score_modifier "
                    f"where lower(race) = lower('{self.race}') ")

        if self.subrace_of:
            self.traitContainer = RacialTraits(db, self.race, self.subrace_of)
            lang_sql = (f"{lang_sql} or lower(race) = "
                        f"lower('{self.subrace_of}') ")
            rasm_sql = (f"{rasm_sql} or lower(race) = "
                        f"lower('{self.subrace_of}') ")
        else:
            self.traitContainer = RacialTraits(db, self.race)

        if self.use_rasm_ind:
            rasm = db.query(rasm_sql)
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

        langs = db.query(lang_sql)
        for l in langs:
            self.languages.append(l[0])

        dh = Die(ctx=self.ctx, sides=self.height_modifier_die)
        self.height = dh.get_sum(startingval=self.height_min_inches,
                                 multiplier=self.height_modifier_multiplier)
        dw = Die(ctx=self.ctx, sides=self.weight_modifier_die)
        self.weight = dw.get_sum(startingval=self.weight_min_pounds,
                                 multiplier=self.weight_modifier_multiplier)

    def get_race(self):
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
            outstr = f'{outstr}\n\n   Languages:'
            for l in self.languages:
                outstr = f'{outstr}\n       {l}'

        if self.traitContainer.proficient:
            outstr = f'{outstr}\n\n   Proficiencies:'

            for p in range(len(self.traitContainer.proficient)):
                tmpprofstr = self.traitContainer.proficient[p].ljust(23)
                tmpsrcstr = self.traitContainer.proficient_source[p]
                outstr = (f'{outstr}\n       {tmpprofstr}'
                          f' ({tmpsrcstr})')

        for b in self.traitContainer.traits:
            if b.category != "Proficiency Skill":
                outstr = f'{outstr}\n {b}'

        outstr = f'{outstr}\n)\n'
        return outstr


if __name__ == '__main__':
    db = InvokePSQL()
    ctx = Ctx(app_username='CharacterRace_main')
    a = CharacterRace(db=db, ctx=ctx, race_candidate='Dryad')
    alignmentObj = a.get_alignment(db=db)
    a.set_randoms(db=db, gender='M')
    print(a.race)
    print(alignmentObj)
    print(a.get_skin_tone(db=db))
    print(a.get_hair_color(db=db))
    print(a.get_hair_type(db=db))
    print(a.get_eye_color(db=db))
    print(a.get_name(db=db, gender='U'))
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
