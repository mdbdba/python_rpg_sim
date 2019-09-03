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
             overwrite_party=False):

        self.character_id_str = character_id_str
        self.party_composition_id = party_composition_id
        self.name = name
        self.ability_array_str = ability_array_str
        self.level = level
        self.gender_candidate = gender_candidate
        self.character_ids = []

        if self.party_name_exists(db) and not overwrite_party:
            raise Exception(f'The {self.name} party already exists.')

        if not self.party_composition_exists(db) and character_id_string is None:
            raise Exception(f'The party composition id, {party_composition_id}, does not exist.')

        if character_id_str is None:
            print(f'Creating {name}: a level {level} party consisting of '
                  f'{party_composition_id} with abilities: {ability_array_str}')
        else:
            print( f'Creating {name}: a party consisting of '
                   f'character ids: {character_id_str}')
            self.character_ids = stringToArray(self.character_id_str)
            self.verify_character_id_list(db)
            self.create_party_in_db(db)

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

