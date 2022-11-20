import psycopg
from psycopg import Error
from configparser import ConfigParser


class Connessione:

    def __init__(self, config='./CONFIG.ini'):
        cfg = ConfigParser()
        cfg.read(config)
        user = cfg.get("POSTGRESQL", "USER")
        password = cfg.get("POSTGRESQL", "PASSWORD")
        host = cfg.get("POSTGRESQL", "HOST")
        port = cfg.get("POSTGRESQL", "PORT")
        dbname = cfg.get("POSTGRESQL", "DBNAME")
        try:
            self.conn = psycopg.connect(user=user, password="", host=host, port=port, dbname=dbname)
            self.cur = self.conn.cursor()
            print("Connecting to PostgreSQL is Ok")
        except (Exception, Error) as error:
            raise Exception("Error while connecting to PostgreSQL")

    def query(self, sql):
        self.cur.execute(sql)

    def query1(self, sql, data):
        self.cur.execute(sql, data)

    def close(self):
        self.cur.close()
        self.conn.close()



