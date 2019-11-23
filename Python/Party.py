from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter
from CommonFunctions import stringToArray

class Party(object):
    def __init__(self,
             db,
             name,
             character_id_str=None,
             party_composition_id=11,
             ability_array_str="10,10,10,10,10,10",
             level=1,
             gender_candidate="Random",
             overwrite_party=False,
             debug_ind=0):

        self.character_id_str = character_id_str
        self.party_composition_id = party_composition_id
        self.name = name
        self.ability_array_str = ability_array_str
        self.level = level
        self.gender_candidate = gender_candidate
        self.debug_ind = debug_ind
        self.character_ids = []
        self.character_list = []

        if self.party_name_exists(db) and not overwrite_party:
            print(f'Using the {self.name} party that already exists.')
            self.set_existing_characters(db)
        else:
            if not self.party_composition_exists(db) and character_id_str is None:
                raise Exception(f'The party composition id, {party_composition_id}, does not exist.')

            if character_id_str is None:
                print(f'Creating {name}: a level {level} party consisting of '
                      f'{party_composition_id} with abilities: {ability_array_str}')
                party_classes = self.get_party_composition(db)
                for party_class in party_classes:
                    primary_race = self.get_primary_race(db, party_class[0])
                    print(f'create {primary_race} {party_class[0]}')
                    tmppc = PlayerCharacter(db, class_candidate=party_class[0], race_candidate=primary_race,
                                    gender_candidate=self.gender_candidate,
                                    ability_array_str=self.ability_array_str,
                                    debug_ind=self.debug_ind)
                    self.character_ids.append(tmppc.character_id)

                print(self.character_ids )

            else:
                print( f'Creating {name}: a party consisting of '
                       f'character ids: {character_id_str}')
                self.character_ids = stringToArray(self.character_id_str)

            self.verify_character_id_list(db)
            self.create_party_in_db(db)
            self.character_list = self.build_character_list(db)

    def get_party_name(self):
        return self.name

    def get_party(self):
        return self.character_list

    def set_existing_characters(self, db):
        sql=f"select character_id from dnd_5e.party where name = '{self.name}'"
        res = db.query(sql)
        for character_id in res:
            tmppc = PlayerCharacter(db, character_id=character_id[0], debug_ind=self.debug_ind)
            self.character_ids.append(tmppc.character_id)
            self.character_list.append(tmppc)

        return res

    def build_character_list(self,db):
        tmp_list = []
        for id in self.character_ids:
            tmp_list.append(PlayerCharacter(db, character_id=id), debug_ind=self.debug_ind)
        return tmp_list

    def get_primary_race(self,db, pclass):
        sql=f"select primary_race_candidate from dnd_5e.lu_class where class = '{pclass}'"
        res = db.query(sql)
        return res[0][0]

    def get_party_composition(self,db):
        sql = f"select class from party_composition_class where party_composition_id = {self.party_composition_id};"
        res = db.query(sql)
        return res

    def create_party_in_db(self,db):
        for character_id in self.character_ids:
            sql = f"insert into dnd_5e.party(name,character_id) values ('{self.name}',{character_id})"
            db.insert(sql)

    def verify_character_id(self,db, character_id):
        sql = f"select count(id) from dnd_5e.character where id={character_id};"
        res = db.query(sql)
        if res[0][0] == 1:
            return_value = True
        else:
            return_value = False

        return return_value

    def verify_character_id_list(self,db):
        fail_str = ""
        for character_id in self.character_ids:
            if not self.verify_character_id(db, character_id):
                fail_str = f'{fail_str}{character_id}, '
        if len(fail_str) > 0:
                fail_str = fail_str[:-2]
                raise Exception(f"Character ids: {fail_str} do not exist")

    def party_name_exists(self, db):
        sql = f"select count(name) from party where name='{self.name}';"
        res = db.query(sql)
        if res[0][0] > 0:
            return_value = True
        else:
            return_value = False

        return return_value

    def party_composition_exists(self, db):
        sql = f"select count(id) from party_composition where id='{self.party_composition_id}';"
        res = db.query(sql)
        if res[0][0] == 1:
            return_value = True
        else:
            return_value = False

        return return_value

if __name__ == '__main__':
    db = InvokePSQL()
    a = Party(db, name='AllStars_3')
    print(a.get_party())
