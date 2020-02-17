from InvokePSQL import InvokePSQL


class Trait(object):
    def __init__(self, race, trait_name, trait_orderby, category,
                 affected_name, affected_multiplier, affected_die,
                 affected_adj, affect, recharge_on,
                 variable_recharge_multiplier, variable_recharge_die,
                 variable_recharge_adj, description):

        self.race = race
        self.trait_name = trait_name
        self.trait_orderby = trait_orderby
        self.category = category
        self.affected_name = affected_name
        self.affected_multiplier = affected_multiplier
        self.affected_die = affected_die
        self.affected_adj = affected_adj
        self.affect = affect
        self.recharge_on = recharge_on
        self.variable_recharge_multiplier = variable_recharge_multiplier
        self.variable_recharge_die = variable_recharge_die
        self.variable_recharge_adj = variable_recharge_adj
        self.description = description

    def __str__(self):
        outstr = (f'\ntrait_name:                   '
                  f'{self.trait_name}')
        if self.trait_orderby:
            outstr = (f'{outstr}\ntrait_orderby:                '
                      f'{self.trait_orderby}')
        if self.category:
            outstr = (f'{outstr}\ncategory:                     '
                      f'{self.category}')
        if self.affected_name:
            outstr = (f'{outstr}\naffected_name:                '
                      f'{self.affected_name}')
        if self.affected_multiplier:
            outstr = (f'{outstr}\naffected_multiplier:          '
                      f'{self.affected_multiplier}')
        if self.affected_die:
            outstr = (f'{outstr}\naffected_die:                 '
                      f'{self.affected_die}')
        if self.affected_adj:
            outstr = (f'{outstr}\naffected_adj:                 '
                      f'{self.affected_adj}')
        if self.affect:
            outstr = (f'{outstr}\naffect:                       '
                      f'{self.affect}')
        if self.recharge_on:
            outstr = (f'{outstr}\nrecharge_on:                  '
                      f'{self.recharge_on}')
        if self.variable_recharge_multiplier:
            outstr = (f'{outstr}\nvariable_recharge_multiplier: '
                      f'{self.variable_recharge_multiplier}')
        if self.variable_recharge_die:
            outstr = (f'{outstr}\nvariable_recharge_die:        '
                      f'{self.variable_recharge_die}')
        if self.variable_recharge_adj:
            outstr = (f'{outstr}\nvariable_recharge_adj:        '
                      f'{self.variable_recharge_adj}')
        if self.description:
            outstr = (f'{outstr}\ndescription:                  '
                      f'{self.description}')

        return outstr


class RacialTraits(object):
    def __init__(self, db, race, inc_parent_race=None):
        self.traits = []
        self.proficient = []
        self.proficient_source = []
        self.rawtraits = None
        self.populate_traits(db, race, inc_parent_race)

    def populate_traits(self, db, race, inc_parent_race):
        sql = (f"SELECT race, trait_name, trait_orderby, category, "
               f"affected_name, affected_multiplier, affected_die, "
               f"affected_adj, affect, recharge_on, "
               f"variable_recharge_multiplier, variable_recharge_die, "
               f"variable_recharge_adj, description "
               f"FROM dnd_5e.v_racial_trait where "
               f"lower(race) = lower('{race}') ")
        if inc_parent_race:
            sql = (f"{sql} or lower(race) = lower('{inc_parent_race}') "
                   f"order by trait_name, trait_orderby,category;")

        self.rawtraits = db.query(sql)

        for t in self.rawtraits:
            self.traits.append(Trait(t[0], t[1], t[2], t[3], t[4], t[5], t[6],
                               t[7], t[8], t[9], t[10], t[11], t[12], t[13]))
            if t[3] and t[3] == "Proficiency Skill":
                self.proficient.append(t[4])
                self.proficient_source.append(t[1])


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = RacialTraits(db, "Mountain dwarf", "Dwarf")
    for b in a1.traits:
        print(b)
