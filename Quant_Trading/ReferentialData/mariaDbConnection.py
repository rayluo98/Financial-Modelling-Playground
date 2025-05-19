# Module Imports
import mariadb
import sys
from sqlConnection import sqlConnection
import logging 

class mariaDB(sqlConnection):
    def __init__(self, DBNAME: str="Histo", 
                 argEng: str="mariadb+mariadbconnector",
                 connector = mariadb):
        # Creating connection object
        ### argEng = mariadb+mariadbconnector
        super().__init__(DBNAME, argEng, connector)
        # self.cursor = None
        # try:
        #     self.mydb = mariadb.connect(
        #         user=self.database_username,
        #         password=self.database_password,
        #         host=self.database_ip,
        #         database=self.DBNAME
        #     )
        #     self.cursor = self.mydb.cursor() 
        # except mariadb.Error as e:
        #     print(f"Error connecting to MariaDB Platform: {e}")
        #     sys.exit(1)        

        #DEPRECATED
    def create_db_from_cursor(self, cursor, DB_NAME:str):
        super().create_db_from_cursor(cursor, DB_NAME)

    ### DEPRECATED
    def create_database(self, DB_NAME:str):
        super().create_database(DB_NAME)

    ### DEPRECATED
    def _HistoToTable(self, data:dict, attr:str):
        super()._HistoToTable(data, attr)
        
def main():
    test = mariaDB("LE_HISTO")
    from ReferentialData.polygonData import PolygonAPI
    import pickle
    import os
    ## End Date
    end_dt = "2025-02-20"
    ## Start date
    start_dt = "2020-01-20"
    # Loading "pairs trade" buckets
    DIR = r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'
    COR_DIR = r'\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Clustering'
    with open(os.path.join(COR_DIR, "correlation_buckets_no_shorts.pkl"), "rb") as file:
        BUCKETS = pickle.load(file)
    # Concatenating dictionary value lists
    UNIVERSE=[]
    for i in list(BUCKETS.values()):
        UNIVERSE.extend(i)

    colnames = ["Close", "Volume"]
    DataLoader = PolygonAPI()
    MID_LOADED = False
    HIGH_LOADED = False
    if not MID_LOADED:
        mid_df = {}
    if not HIGH_LOADED:
        high_df = {}
    ### loading in low frequency data
    if len(mid_df) == 0:
        mid_df, _ = DataLoader.getPrices(UNIVERSE, timespan= "day", from_ = start_dt, 
                                        to_=end_dt,
                                    logDir=DIR, _parallel=True)
        MID_LOADED = True

    ### loading in high frequency data
    if len(high_df) == 0:
        high_df, _ = DataLoader.getPrices(UNIVERSE,from_ = start_dt, 
                    
                    
                                        to_=end_dt, timespan="minute", logDir=DIR, _parallel=True)
        HIGH_LOADED = True
    test._DfHistoToTable(mid_df, attr = "day")
    test._DfHistoToTable(high_df, attr = "minute")

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()