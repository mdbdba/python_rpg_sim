import pathlib
import configparser
# import beeline
# from beeline.middleware.flask import HoneyMiddleware

from flask import Flask
from flask_graphql import GraphQLView

from models import db_session
from schema import schema, schema_mutation, Race, racialFirstName, racialLastName
from schema import pcClass, characterRequest, CreateCharacterRequest

# path = pathlib.Path('o11y.ini')
# if path.exists():
#     config = configparser.ConfigParser()
#     config.read('o11y.ini')
#     beeline.init(writekey=config['DEFAULT']['honeycomb_key'], dataset='RPG Simulation', service_name='graghql_backend')

app = Flask(__name__)

# if path.exists():
#     # db_events defaults to True, set to False if not using our db middleware with Flask-SQLAlchemy
#     HoneyMiddleware(app, db_events=True)

app.debug = True

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)
# /graphql-mutation
app.add_url_rule('/createCharacter', view_func=GraphQLView.as_view(
    'create-character',
    schema=schema_mutation, graphiql=True
))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=80, debug=True)