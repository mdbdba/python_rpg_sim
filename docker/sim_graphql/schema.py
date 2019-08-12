import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Race as RaceModel, racialFirstName as racialFirstNameModel
from models import racialLastName as racialLastNameModel, pcClass as pcClassModel


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

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_races = SQLAlchemyConnectionField(RaceConnection)
    all_racialFirstNames = SQLAlchemyConnectionField(racialFirstNameConnection)
    all_racialLastNames = SQLAlchemyConnectionField(racialLastNameConnection)
    all_pcClasses = SQLAlchemyConnectionField(pcClassConnection)

schema = graphene.Schema(query=Query)