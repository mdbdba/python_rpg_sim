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

        # db_config = "dbname=rpg host=localhost"
        # db_config = " ".join([db_config, "password=1wm4iMSfX9hzehT port=5433"])
        # db_config = " ".join([db_config, "user=app"])

        try:
            # print('connecting to PostgreSQL database...')
            self.connection = pg.connect(db_config)
            self.cursor = self.connection.cursor()
            self.cursor.execute('SELECT VERSION()')
            self.db_version = self.cursor.fetchone()

        except Exception as error:
            print('Error: connection not established {}'.format(error))

    def insertAndReturnId(self, stmt):
        try:
            stmt = (f"{stmt} returning id")
            self.cursor.execute(stmt)
            newId = self.cursor.fetchone()[0]
            self.connection.commit()

        except Exception as error:
            print('error execting "{}", error: {}'.format(stmt, error))
            return -1
        else:
            return newId

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


if __name__ == '__main__':
    a1 = InvokePSQL()
    print(a1.db_version)
