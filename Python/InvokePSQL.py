import configparser
import psycopg2 as pg
from CommonFunctions import find_file


class InvokePSQL(object):

    """docstring for InvokePSQLClient"""

    def __init__(self):
        config = configparser.ConfigParser()
        dbini = find_file('db.ini')
        config.read(dbini)
        db_config = (f"host='{config['DEFAULT']['host']}' " 
                     f"dbname='{config['DEFAULT']['dbname']}' " 
                     f"user='{config['DEFAULT']['user']}' " 
                     f"password='{config['DEFAULT']['password']}' " 
                     f"port='{config['DEFAULT']['port']}'")
        self.db_id_str = (f"{config['DEFAULT']['user']}@{config['DEFAULT']['host']}:" 
                          f"{config['DEFAULT']['port']}/{config['DEFAULT']['dbname']}")
        try:
            # print('connecting to PostgreSQL database...')
            self.connection = pg.connect(db_config)
            self.cursor = self.connection.cursor()
            self.cursor.execute('SELECT VERSION()')
            self.db_version = self.cursor.fetchone()

        except Exception as error:
            print(f"Error: connection to {self.db_id_str} not established {error}")

    def insert_and_return_id(self, stmt):
        try:
            stmt = f"{stmt} returning id"
            self.cursor.execute(stmt)
            new_id = self.cursor.fetchone()[0]
            self.connection.commit()

        except Exception as error:
            print('error execting "{}", error: {}'.format(stmt, error))
            return -1
        else:
            return new_id

    def insert(self, stmt):
        try:
            self.cursor.execute(stmt)
            self.connection.commit()

        except Exception as error:
            print('error execting "{}", error: {}'.format(stmt, error))
            return False
        else:
            return True

    def query(self, query):
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()

        except Exception as error:
            print('error execting query "{}", error: {}'.format(query, error))
            return None
        else:
            return results

    def __del__(self):
        if self.connection is not None:
            self.connection.close()
        if self.cursor is not None:
            self.cursor.close()

    def __repr__(self):
        return self.db_id_str

if __name__ == '__main__':
    a1 = InvokePSQL()
    print(a1.db_version)
