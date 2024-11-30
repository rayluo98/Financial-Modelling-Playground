from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler 
from sklearn.preprocessing import normalize 
from sklearn.decomposition import PCA 
from sklearn import datasets
from collections import namedtuple
import numpy as np
import pandas as pd

Score = namedtuple("Score", ["Silhouette", "Rand"])

"""
DBSCAN Algorithm

DBSCAN(dataset, eps, MinPts){
# cluster index
C = 1
for each unvisited point p in dataset {
         mark p as visited
         # find neighbors
         Neighbors N = find the neighboring points of p

         if |N|>=MinPts:
             N = N U N'
             if p' is not a member of any cluster:
                 add p' to cluster C 
}
"""

class DBSCANwrapper(object):
   
    def __init__(self, X, labels=None):
        self.X = X
        self.labels = labels
        # Number of clusters in labels, ignoring noise if present.
        self._n_clusters_ = 0
        self._model = None
        self._score = None

    def fit(self, X, eps=0.05, min_samples=10, test=False):
        scaler = StandardScaler() 
        X_scaled = scaler.fit_transform(X) 
        
        # Normalizing the data so that  
        # the data approximately follows a Gaussian distribution 
        X_normalized = normalize(X_scaled) 
  
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X_normalized)
        # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        # core_samples_mask[db.core_sample_indices_] = True
        self._model = db
        if not test:
            self._n_clusters_ = len(set(self.getLabels())) - (1 if -1 in self.getLabels() else 0)
        return None 
    
    def _optimize(self, metric: str,  y_true=None, threshold=1e-2):
        max_score = None
        score_idx = None 
        if metric == "SC":
            max_score = -1
            score_idx = 0
        else:
            max_score = 0
            score_idx = 1

        optimal_eps = 0
        optimal_minSample = 3
        res = {}

        eps_list = np.arange(threshold, 1, threshold)
        minSample_list = np.arange(3, int(len(self.X) / 3))

        for eps, min_sample in zip(eps_list, minSample_list):
            self.fit(self.X, eps, min_sample, True)
            test_score = self.getScore()
            if test_score[score_idx] > max_score:
                max_score = test_score[score_idx]
            res[(eps, min_sample)] = test_score[score_idx]
            optimal_eps = eps
            optimal_minSample = min_sample
        print("Optimal EPS: {0}, Optimal Minsample: {1}".format(optimal_eps, optimal_minSample ))

        self.fit(self.X, optimal_eps, optimal_minSample)
        return None

    
    def getLabels(self):
        if self._model == None:
            print("WARNING: model not fit yet!")
            return None
        else:
            labels = self._model.labels_
            return labels

    def getScore(self, y_true=None):
        # evaluation metrics
        sc = metrics.silhouette_score(self.X, self.getLabels())
        print("Silhouette Coefficient:%0.2f" % sc)
        ari = None
        if y_true != None:
            ari = metrics.adjusted_rand_score(y_true, self.getLabels())
            print("Adjusted Rand Index: %0.2f" % ari)
        return Score(sc, ari)
    
def main():
    beta = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\^FTW5000_beta.csv').set_index('Ticker')
    beta = beta.loc[:, ~beta.columns.str.contains('^Unnamed')]
    dbModel = DBSCANwrapper(beta)
    dbModel._optimize("SC")
    print(dbModel.getLabels())

if __name__ == "__main__":
    main()