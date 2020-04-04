import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Race as RaceModel, racialFirstName as racialFirstNameModel
from models import racialLastName as racialLastNameModel, pcClass as pcClassModel
from models import studyInstance as studyInstanceModel
from models import characterRequest as characterRequestModel
from models import playerCharacter as playerCharacterModel
from models import partySummary as partySummaryModel
from models import addit


class Race(SQLAlchemyObjectType):
    class Meta:
        model = RaceModel
        interfaces = (relay.Node, )


class RaceConnection(relay.Connection):
    class Meta:
        node = Race


class racialFirstName(SQLAlchemyObjectType):
    class Meta:
        model = racialFirstNameModel
        interfaces = (relay.Node, )


class racialFirstNameConnection(relay.Connection):
    class Meta:
        node = racialFirstName

class racialLastName(SQLAlchemyObjectType):
    class Meta:
        model = racialLastNameModel
        interfaces = (relay.Node, )


class racialLastNameConnection(relay.Connection):
    class Meta:
        node = racialLastName

class pcClass(SQLAlchemyObjectType):
    class Meta:
        model = pcClassModel
        interfaces = (relay.Node, )

class pcClassConnection(relay.Connection):
    class Meta:
        node = pcClass

class studyInstance(SQLAlchemyObjectType):
    class Meta:
        model = studyInstanceModel
        interfaces = (relay.Node,)

class studyInstanceConnection(relay.Connection):
    class Meta:
        node = studyInstance

class characterRequest(SQLAlchemyObjectType):
    class Meta:
        model = characterRequestModel
        interfaces = (relay.Node,)

class characterRequestConnection(relay.Connection):
    class Meta:
        node = characterRequest

class playerCharacter(SQLAlchemyObjectType):
    class Meta:
        model = playerCharacterModel
        interfaces = (relay.Node, )

class playerCharacterConnection(relay.Connection):
    class Meta:
        node = playerCharacter

class partySummary(SQLAlchemyObjectType):
    class Meta:
        model = partySummaryModel
        interfaces = (relay.Node, )

class partySummaryConnection(relay.Connection):
    class Meta:
        node = partySummary


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_races = SQLAlchemyConnectionField(RaceConnection)
    all_racialFirstNames = SQLAlchemyConnectionField(racialFirstNameConnection)
    all_racialLastNames = SQLAlchemyConnectionField(racialLastNameConnection)
    all_pcClasses = SQLAlchemyConnectionField(pcClassConnection)
    all_studyInstances = SQLAlchemyConnectionField(studyInstanceConnection)
    all_characterRequests = SQLAlchemyConnectionField(characterRequestConnection)
    all_playerCharacters = SQLAlchemyConnectionField(playerCharacterConnection)
    all_parties = SQLAlchemyConnectionField(partySummaryConnection)

schema = graphene.Schema(query=Query)

class CreateCharacterRequest(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        character_name = graphene.String()
        gender = graphene.String()
        race_candidate = graphene.String()
        class_candidate = graphene.String()
        level = graphene.Int()
        tta = graphene.String()
        ability_array_str = graphene.String()
        height = graphene.Int()
        weight = graphene.Int()
        alignment_abbrev = graphene.String()
        skin_tone = graphene.String()
        hair_color = graphene.String()
        hair_type = graphene.String()
        eye_color = graphene.String()
        ranged_weapon = graphene.String()
        melee_weapon = graphene.String()
        ranged_ammunition_type = graphene.String()
        ranged_ammunition_amt = graphene.Int()
        armor = graphene.String()
        shield = graphene.String()
        created_by_webuser = graphene.String()

    char_req = graphene.Field(lambda: characterRequest)
    def mutate(self, id=None, character_name = 'Random', gender = 'rd', race_candidate = 'Random', class_candidate = 'Random',
               level = -1, tta = 'Random', ability_array_str = 'Common', height = -1, weight = -1,
               alignment_abbrev = 'Random', skin_tone = 'Random', hair_color = 'Random', hair_type = 'Random',
               eye_color='Random', ranged_weapon='Default',
               melee_weapon='Default', ranged_ammunition_type='Default', ranged_ammunition_amt=-1,
               armor='Default', shield='Default', created_by_webuser = 'Default'):
        char_req = characterRequestModel(gender = gender,
                                         character_name = character_name,
                                         race_candidate = race_candidate,
                                         class_candidate = class_candidate,
                                         level = level,
                                         tta = tta,
                                         ability_array_str = ability_array_str,
                                         height = height,
                                         weight = weight,
                                         alignment_abbrev = alignment_abbrev,
                                         skin_tone = skin_tone,
                                         hair_color = hair_color,
                                         hair_type = hair_type,
                                         eye_color = eye_color,
                                         ranged_weapon = ranged_weapon,
                                         melee_weapon = melee_weapon,
                                         ranged_ammunition_type = ranged_ammunition_type,
                                         ranged_ammunition_amt = ranged_ammunition_amt,
                                         armor = armor, shield = shield,
                                         created_by_webuser =created_by_webuser)
        addit(char_req)

        return CreateCharacterRequest(char_req=char_req)

class Mutation(graphene.ObjectType):
    create_character_request = CreateCharacterRequest.Field()

schema_mutation = graphene.Schema(query=Query, mutation=Mutation)
