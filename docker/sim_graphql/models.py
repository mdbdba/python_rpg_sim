# flask_sqlalchemy/models.py
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://app:1wm4iMSfX9hzehT@pgs/rpg' )
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
# We will need this for querying
Base.query = db_session.query_property()

def addit(al_class):
    db_session.add(al_class)
    db_session.commit()


class Race(Base):
    __tablename__ = 'lu_race'
    race = Column(String, primary_key=True)
    subrace_of = Column(String)
    avg_max_age = Column(Integer)
    base_walking_speed = Column(Integer)
    height_min_inches = Column(Integer)
    height_modifier_adj = Column(Integer)
    height_modifier_die = Column(Integer)
    height_modifier_multiplier = Column(Integer)
    maturity_age = Column(Integer)
    size = Column(String)
    weight_min_pounds = Column(Integer)
    weight_modifier_adj = Column(Integer)
    weight_modifier_die = Column(Integer)
    weight_modifier_multiplier = Column(Integer)
    source_material = Column(String)
    source_credit_url = Column(String)
    source_credit_comment = Column(String)

class racialFirstName(Base):
    __tablename__ = 'lu_racial_first_name'
    id = Column(Integer, primary_key=True)
    race = Column(String)
    gender = Column(String)
    value  = Column(String)

class racialLastName(Base):
    __tablename__ = 'lu_racial_last_name'
    id = Column(Integer, primary_key=True)
    race = Column(String)
    gender = Column(String)
    value  = Column(String)

class pcClass(Base):
    __tablename__ = 'lu_class'
    pc_class = Column('class', String, primary_key=True)
    hit_die = Column(Integer)
    ability_pref_str = Column(String)
    source_material = Column(String)
    source_credit_url = Column(String)
    source_credit_comment = Column(String)


class studyInstance(Base):
    __tablename__ = 'study_instance'
    id = Column(Integer, primary_key=True)
    study_name = Column(String)
    stats = Column(String)
    run_status = Column(String)

class characterRequest(Base):
    __tablename__ = 'character_request'
    id = Column(Integer, primary_key=True)
    character_name = Column(String)
    gender = Column(String)
    race_candidate = Column(String, )
    class_candidate = Column(String)
    level = Column(Integer)
    tta = Column(String)
    ability_array_str = Column(String)
    height = Column(Integer)
    weight = Column(Integer)
    alignment_abbrev = Column(String)
    skin_tone = Column(String)
    hair_color = Column(String)
    hair_type = Column(String)
    eye_color = Column(String)
    ranged_weapon = Column(String)
    melee_weapon = Column(String)
    ranged_ammunition_type = Column(String)
    ranged_ammunition_amt = Column(Integer)
    armor = Column(String)
    shield = Column(String)
    request_datetime = Column(Date)
    request_status = Column(String)
    complete_datetime = Column(Date)
    created_by_webuser = Column(String)
    character_id = Column(Integer)

class playerCharacter(Base):
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    race = Column(String)
    character_class = Column('class', String)
    level = Column(Integer)
    tta = Column(String)
    raw_ability_string = Column(String)
    ability_base_string = Column(String)
    ability_string = Column(String)
    ability_racial_mod_string = Column(String)
    ability_modifier_string = Column(String)
    hit_points = Column(Integer)
    temp_hit_points = Column(Integer)
    cur_hit_points = Column(Integer)
    height = Column(Integer)
    weight = Column(Integer)
    alignment = Column(String)
    alignment_abbrev = Column(String)
    skin_tone = Column(String)
    hair_color = Column(String)
    hair_type = Column(String)
    eye_color = Column(String)
    ranged_weapon = Column(String)
    melee_weapon = Column(String)
    ranged_ammunition_type = Column(String)
    ranged_ammunition_amt = Column(Integer)
    armor = Column(String)
    shield = Column(String)
    created_by_webuser = Column(String)

class partySummary(Base):
    __tablename__ = 'v_party_summary'
    party_name = Column('name', String, primary_key=True)
    character_desc_1 = Column(String)
    character_desc_2 = Column(String)
    character_desc_3 = Column(String)
    character_desc_4 = Column(String)
    character_desc_5 = Column(String)
    character_desc_6 = Column(String)
    character_desc_7 = Column(String)
