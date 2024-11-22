from abc import abstractmethod
import pandas as pd 

class BetaFactory(object):

    @abstractmethod
    def calculateBeta(self, portfolio:pd.DataFrame):
        pass

    @abstractmethod
    def getBeta(self):
        pass