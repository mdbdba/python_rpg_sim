# websim Service

# Import framework
from flask import Flask, jsonify
# , request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
# from json import dumps


access = 'app:1wm4iMSfX9hzehT'
engine = create_engine('postgresql+psycopg2://app:1wm4iMSfX9hzehT@pgs/rpg')
app = Flask(__name__)
api = Api(app)


class simRest(Resource):
    def get(self):
        return {
            'gameSystems': ['dnd_5e']
        }


class Races(Resource):
    def get(self):
        conn = engine.connect()
        sql = (f"select race, subrace_of, source_material, "
               f"source_credit_url, source_credit_comment, avg_max_age, "
               f"base_walking_speed, height_min_inches, height_modifier_adj, "
               f"height_modifier_die, height_modifier_multiplier, "
               f"maturity_age, size, weight_min_pounds, weight_modifier_adj, "
               f"weight_modifier_die, weight_modifier_multiplier "
               f"from lu_race")
        query = conn.execute(sql)
        # return {'races': [i[0] for i in query.cursor.fetchall()]}
        result = {'races':
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


class Race(Resource):
    def get(self, race_name):
        conn = engine.connect()
        sql = (f"select race, subrace_of, source_material, "
               f"source_credit_url, source_credit_comment, avg_max_age, "
               f"base_walking_speed, height_min_inches, height_modifier_adj, "
               f"height_modifier_die, height_modifier_multiplier, "
               f"maturity_age, size, weight_min_pounds, weight_modifier_adj, "
               f"weight_modifier_die, weight_modifier_multiplier "
               f"from lu_race where race = '{race_name}'")
        query = conn.execute(sql)
        result = {'race':
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


class racialFirstNames(Resource):
    def get(self, race_name):
        conn = engine.connect()
        sql = (f"select race, gender, value "
               f"from lu_racial_first_name "
               f"where race = '{race_name}'")
        query = conn.execute(sql)
        result = {race_name:
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


class racialLastNames(Resource):
    def get(self, race_name):
        conn = engine.connect()
        sql = (f"select race, gender, value "
               f"from lu_racial_last_name "
               f"where race = '{race_name}'")
        query = conn.execute(sql)
        result = {race_name:
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


class pcClasses(Resource):
    def get(self):
        conn = engine.connect()
        sql = (f"SELECT class, hit_die, ability_pref_str, source_material, "
               f"source_credit_url, source_credit_comment "
               f"FROM lu_class")
        query = conn.execute(sql)
        result = {'Classes':
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


class pcClass(Resource):
    def get(self, class_name):
        conn = engine.connect()
        sql = (f"SELECT class, hit_die, ability_pref_str, source_material, "
               f"source_credit_url, source_credit_comment "
               f"FROM lu_class "
               f"WHERE class = '{class_name}'")
        query = conn.execute(sql)
        result = {'Class':
                  [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)


# Create routes
api.add_resource(simRest, '/')
api.add_resource(Races, '/races')
api.add_resource(Race, '/races/<race_name>')
api.add_resource(racialFirstNames, '/first_names/<race_name>')
api.add_resource(racialLastNames, '/last_names/<race_name>')
api.add_resource(pcClasses, '/classes')
api.add_resource(pcClass, '/classes/<class_name>')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
