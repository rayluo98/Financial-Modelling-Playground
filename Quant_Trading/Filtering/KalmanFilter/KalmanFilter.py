from __future__ import print_function
import pandas as pd
import os
# Standard imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sklearn
import math
from logging import Logger
%matplotlib inline
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics import tsaplots 

# Import Statsmodels
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse, aic

from hurst import compute_Hc

#rom pandas.io.data import DataReader
from pykalman import KalmanFilter

class KalmanFilter(object):
    def __init__(self, data):
        self.data = data
        self.signal = data


    