import logging
import mysql.connector
import sqlalchemy
import pandas as pd

class sqlConnection(object):
    def __init__(self, DBNAME: str="Histo", argEng: str = "", connector= mysql.connector):
        # Creating connection object
        # optional port: 3306
        self.port = 3306
        self.database_username = 'root'
        self.database_password = 'alohomora'
        self.database_ip       = 'localhost'
        # self.database_ip       = '192.168.0.190'
        self.DBNAME     = DBNAME
        self.connector = connector
        self.domain_socket = r'/var/run/mariadb10.sock'
        try:
            self.mydb = connector.connect(
                host = self.database_ip,
                user = self.database_username,
                password = self.database_password)
            self.engine = None
            self.cursor = self.mydb.cursor()
            if argEng != "":
                ## mysql+mysqlconnector
                self.engine = sqlalchemy.create_engine('{0}://{1}:{2}@{3}/{4}'.
                        format(argEng, self.database_username, self.database_password, 
                                f"{self.database_ip}:{self.port}", self.DBNAME))
        except connector.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")

    #DEPRECATED
    def create_db_from_cursor(self, cursor, DB_NAME:str):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except self.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    ## DEPRECATED
    def create_database(self, DB_NAME:str):
        try:
            self.cursor.execute("USE {}".format(DB_NAME))
        except self.connector.Error as err:
            print("Database {} does not exists.".format(DB_NAME))
            ## ERROR 1049: ER_BAD_DB_ERROR
            if err.errno == 1049:
                self.create_db_from_cursor(self.cursor, DB_NAME)
                print("Database {} created successfully.".format(DB_NAME))
                self.mydb.database = DB_NAME
            else:
                print(err)
                exit(1)

    ### need to add error handling  - DEPRECATED
    def _HistoToTable(self, data:dict):
        self.create_database("LE_HISTO")
        for ticker in data:
            check_table_exist = ("DROP TABLE IF EXISTS %s")
            self.cursor.execute(check_table_exist, ticker)

            create_table = ("CREATE TABLE %s ( "
                            "Open FLOAT, "
                            "High FLOAT, "
                            "Low FLOAT, "
                            "Volume FLOAT, "
                            "VWAP FLOAT, "
                            "Timestamp TIMESTAMP, "
                            "Transactions INT, "
                            "OTC BOOL")
            self.cursor.execute(create_table, ticker)

            add_histo = ("INSERT INTO %s "
                        "(Open, High, Low, Volume, VWAP, Timestamp, Transactions, OTC) "
                        "VALUES (%s, %s, %s, %s, %s)")

            # Iteratively add data entries - very bad
            for _, row in data[ticker].iterrows():
                self.cursor.execute(add_histo, tuple(row))
            logging.info("Contributed to HISTO:{0}".format(ticker))
        return None
    
    def _DfHistoToTable(self, data:dict, attr:str):
        self.create_database(f"LE_HISTO_{attr}")
        with self.engine.connect() as conn:
            for ticker in data:
                data[ticker].to_sql(con=conn, name=ticker, if_exists='replace')
                logging.info("Contributed to HISTO:{0}".format(ticker))
        return None
        
def main():
    test = sqlConnection()

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()