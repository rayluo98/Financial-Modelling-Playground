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


# Import Statsmodels
from statsmodels.tsa.api import VAR
from statsmodels.tools.eval_measures import rmse, aic

from hurst import compute_Hc

#rom pandas.io.data import DataReader
import pykalman

class KalmanFilter(object):
    def __init__(self, data):
        self.data = data
        self.signal = data
        self.kf = None

    def UnivariateKF(name, df, init_mu = 0, init_cov = 1):
        """
        """
        # delta = 1e-5
        # trans_cov = delta / (1 - delta) * np.eye(2)
        # obs_mat = np.vstack(
        #     [df[names[0]], np.ones(df[names[0]].shape)]
        # ).T[:, np.newaxis]
        
        kf = pykalman.KalmanFilter(transition_matrices = [1],
                    observation_matrices = [1],
                    initial_state_mean = init_mu,
                    initial_state_covariance = init_cov,
                    observation_covariance=init_cov,
                    transition_covariance=1)

        mean, cov = kf.filter(df[name])
        # mean, std = mean.squeeze(), np.std(cov.squeeze())

        # plt.figure(figsize=(15,7))
        # plt.plot(df[name] - mean, 'm', lw=1)
        # plt.plot(np.sqrt(cov.squeeze()), 'y', lw=1)
        # plt.plot(-np.sqrt(cov.squeeze()), 'c', lw=1)
        # plt.title('Kalman filter estimate')
        # plt.legend(['Error: real_value - mean', 'std', '-std'])
        # plt.xlabel('Day')
        # plt.ylabel('Value')
        
        return mean, cov

    def calc_slope_intercept_kalman(names, df):
        """
        Utilise the Kalman Filter from the pyKalman package
        to calculate the slope and intercept of the regressed
        ETF df.
        """
        delta = 1e-5
        trans_cov = delta / (1 - delta) * np.eye(2)
        obs_mat = np.vstack(
            [df[names[0]], np.ones(df[names[0]].shape)]
        ).T[:, np.newaxis]
        
        kf = pykalman.KalmanFilter(
            n_dim_obs=1, 
            n_dim_state=2,
            initial_state_mean=np.zeros(2),
            initial_state_covariance=np.ones((2, 2)),
            transition_matrices=np.eye(2),
            observation_matrices=obs_mat,
            observation_covariance=1.0,
            transition_covariance=trans_cov
        )
        
        state_means, state_covs = kf.filter(df[names[1]].values)
        return state_means, state_covs
    