from collections import defaultdict


class Weapon(object):
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.melee_weapon_ind = False
        self.martial_weapon_ind = False
        self.two_handed_ind = False
        self.versatile_ind = False
        self.reach_ind = False
        self.thrown_ind = False
        self.ranged_weapon_ind = False
        self.loading_ind = False
        self.light_ind = False
        self.heavy_ind = False
        self.finesse_ind = False
        self.proficient_ind = None
        self.default_damage_type = None
        #  if this is a versatile weapon, the two
        #  values below should be used if the weapon
        # is being wielded two-handed.
        self.versatile_2hnd_mod = None
        self.versatile_2hnd_die = None
        self.setWeaponProperties(self.db)
        self.damage_dict = defaultdict(list)
        self.setDamageType(self.db)
        self.setWeaponInfo(self.db)

    def setWeaponProficient(self, value=True):
        self.proficient_ind = value

    def setWeaponProperties(self, db):
        sql = (f"select property "
               f"from dnd_5e.lu_weapon_weapon_property "
               f"where weapon = '{self.name}';")
        sRes = db.query(sql)
        for row in sRes:
            # print(row[0])
            if row[0] == 'Two-handed':
                self.two_handed_ind = True
            if 'Versatile' in row[0]:
                self.versatile_ind = True
                if ('(' in row[0] and 'd' in row[0]):
                    thda = row[0].split("(")[1].replace(')', '').split('d')
                    self.versatile_2hnd_mod = int(thda[0])
                    self.versatile_2hnd_die = int(thda[1])
            if row[0] == 'Reach':
                self.reach_ind = True
            if row[0] == 'Finesse':
                self.finesse_ind = True
            if row[0] == 'Thrown':
                self.thrown_ind = True
            if row[0] == 'Loading':
                self.loading_ind = True
            if row[0] == 'Light':
                self.light_ind = True
            if row[0] == 'Heavy':
                self.heavy_ind = True

    def setDamageType(self, db):
        sql = (f"select damage_type "
               f"from dnd_5e.lu_weapon_damage_type "
               f"where weapon = '{self.name}';")
        sRes = db.query(sql)
        if (sRes):
            for row in sRes:
                # set value for default damage
                self.damage_dict[row[0]].append(1)
                self.default_damage_type = row[0]

    def setWeaponInfo(self, db):
        sql = (f"select category, damage_modifier, damage_die, "
               f"case when range_1 is null then -1 "
               f"else range_1 end as range_1, "
               f"case when range_2 is null then -1 "
               f"else range_2 end as range_2 "
               f"from lu_weapon "
               f"where name = '{self.name}';")
        sRes = db.query(sql)
        for row in sRes:
            if 'Martial' in row[0]:
                self.martial_ind = True
            if 'Melee' in row[0]:
                self.melee_weapon_ind = True
            if 'Ranged' in row[0]:
                self.ranged_weapon_ind = True
            self.damage_dict[self.default_damage_type].append(
                row[1])
            self.damage_dict[self.default_damage_type].append(
                row[2])
            self.damage_dict[self.default_damage_type].append(
                row[3])
            self.damage_dict[self.default_damage_type].append(
                row[4])
