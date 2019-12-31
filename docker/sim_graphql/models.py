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
