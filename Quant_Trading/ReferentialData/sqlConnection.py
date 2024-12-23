from errno import errorcode
#import mysql.connector
import logging
import mysql.connector.errorcode
import sqlalchemy
import pandas as pd

class sqlConnection(object):
    def __init__(self, DBNAME: str="Histo"):
        # Creating connection object
        # optional port: 3306
        # self.mydb = mysql.connector.connect(
        #     host = "localhost",
        #     user = "root",
        #     password = "@SunshineJan2024")
        # self.cursor = self.mydb.cursor()
        database_username = 'root'
        database_password = '@SunshineJan2024'
        database_ip       = 'localhost'
        self.DBNAME     = DBNAME
        self.mydb = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                                    format(database_username, database_password, 
                                                            database_ip, self.DBNAME))

        
    # def __exit__(self):
    #     self.close()
        
    #DEPRECATED
    def create_database(cursor, DB_NAME:str):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    ## DEPRECATED
    def create_database(self, DB_NAME:str):
        try:
            self.cursor.execute("USE {}".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                sqlConnection.create_database(self.cursor, DB_NAME:str)
                print("Database {} created successfully.".format(DB_NAME))
                self.mydb.database = DB_NAME
            else:
                print(err)
                exit(1)


    def _HistoToTable(self, data:dict):
        sqlConnection.create_database("LE_HISTO")
        for ticker in data:
            
            data[ticker].to_sql(con=self.mydb, name=ticker, if_exists='replace')
            # check_table_exist = ("DROP TABLE IF EXISTS %s")
            # self.cursor.execute(check_table_exist, ticker)

            # create_table = ("CREATE TABLE %s ( "
            #                 "Open FLOAT, "
            #                 "High FLOAT, "
            #                 "Low FLOAT, "
            #                 "Volume FLOAT, "
            #                 "VWAP FLOAT, "
            #                 "Timestamp TIMESTAMP, "
            #                 "Transactions INT, "
            #                 "OTC BOOL")
            # self.cursor.execute(create_table, ticker)

            # add_histo = ("INSERT INTO %s "
            #             "(Open, High, Low, Volume, VWAP, Timestamp, Transactions, OTC) "
            #             "VALUES (%s, %s, %s, %s, %s)")

            # data_employee = ('Geert', 'Vanderkelen', tomorrow, 'M', date(1977, 6, 14))

            # # Insert new employee
            # cursor.execute(add_employee, data_employee)
            # emp_no = cursor.lastrowid

            # # Insert salary information
            # data_salary = {
            # 'emp_no': emp_no,
            # 'salary': 50000,
            # 'from_date': tomorrow,
            # 'to_date': date(9999, 1, 1),
            # }
            # cursor.execute(add_salary, data_salary)
            logging.Logger.info("Contributed to HISTO:{0}".format(ticker))
        return None
        
def main():
    test = sqlConnection()

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()