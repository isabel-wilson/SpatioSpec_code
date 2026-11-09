#%%
"""
CHOOSE ST-DBSCAN PARAMETERS
The purpose of this file is to exemplify how parameters (eps1, eps2, and minpts) were selected for ST-DBSCAN for the SpatioSpec project. 
This file should be run interactively

"""
# -------------------------------------------------------------------------------------------------------------------
# SET UP
# -------------------------------------------------------------------------------------------------------------------

# User input
hemi = "lh"
base_dir = "C:/meg/params/0_SpatioSpec_results/SpatioSpec_code/Data/"

# Import packages
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.neighbors import NearestNeighbors
import sys
import math
import nibabel.freesurfer.io as fs
from collections import Counter
from sklearn.metrics import silhouette_score, davies_bouldin_score
from pathlib import Path
import os
sys.path.append(base_dir)
import st_dbscan as st

# -------------------------------------------------------------------------------------------------------------------
# LOAD DATAFRAMES
# -------------------------------------------------------------------------------------------------------------------
# Load dataframe that contains coordinates (x, y, and z) representing the center of mass for all subjects and frequencies 
# Need both normalized data (for clustering) and unnormalized data (for plotting)

# NORMALIZED DATA
with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}_normalized.pkl"), "rb") as f:
   COM_coord_subject_df_normalized = pickle.load(f)
data_normed = COM_coord_subject_df_normalized.loc[:, ['freq','x','y','z']].values

# UNNORMALIZED DATA
with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}.pkl"), "rb") as f:
   COM_coord_subject_df = pickle.load(f)
data = COM_coord_subject_df.loc[:, ['freq','x','y','z']].values

# -------------------------------------------------------------------------------------------------------------------
# CHOOSE STARTING PARAMETERS FOR ST-DBSCAN
# -------------------------------------------------------------------------------------------------------------------
"""
SOURCES: 
Function I am using: https://github.com/eren-ck/st_dbscan
Original paper: https://doi.org/10.1016/j.datak.2006.01.013

ST-DBSCAN requires the following parameters: 
eps1 = distance, spatial
eps2 = distance, time
minpts = min number of points within eps1 and eps2 distance of a point. "dense" = greater than minpts
The original dbscan paper also lists a parameter called delta_eps, but the python function does not

CHOOSING PARAMETERS: 
Use the heuristic method described in the original paper.
This method involves first defining minpts, then using minpts to find eps

1. minpts = ln(n) where n is size of database
"""
n = len(data_normed) 
print(n)
minpts = int(math.log(n))
print(minpts)
"""
2. Determine the distances to the k-nearest neighbors for each object, where k is equal to minpts
https://scikit-learn.org/stable/modules/neighbors.html#finding-the-nearest-neighbors
*distance array: note that the nearest neighbor of each point is the point itself, hence the 0s
3. Sort k-distance values in descending order
4. Determine elbow
5. Select eps to less than the distance defined at the elbow
"""
input = data_normed[:, 1:] # exclude the first two columns (subject and frequency)
nbrs = NearestNeighbors(n_neighbors = minpts, algorithm = "ball_tree").fit(input)
# metric = metric used for pairwise distances - using default minkowski (euclidean distance)
# algorithm = ball_tree (constructs a tree where each node is ball enclosing subset of points)
distances, indices = nbrs.kneighbors(input)
# distances is an array with int(minpts) number of columns
# unfold the array, then sort everything (removing zeros makes it easier to read the plot)
sorted_distances = np.trim_zeros(np.sort(distances.flatten()))[::-1]
# Plot
plt.plot(sorted_distances)
plt.grid()

# -------------------------------------------------------------------------------------------------------------------
# GRID SEARCH
# -------------------------------------------------------------------------------------------------------------------

def most_frequent_fraction(arr):
    counts = Counter(arr)
    total = len(arr)
    sorted_counts = sorted(counts.values(), reverse=True)
    return [count / total for count in sorted_counts[:3]]


eps1 = list()  # list params to loop through
eps2 = [] # list params to loop through
minpts = [] # list params to loop through

# Initialize dataframe to organize scores
df_scores = pd.DataFrame(columns=["eps1", "eps2", "minpts", "score"])

# Loop through every combination of parameters. Find the one that minimizes the davies_bouldin score
for a in eps1:
    for b in eps2:
        for c in minpts:
            print("Now working on: eps1 " + str(a) + " eps2 " + str(b) + " minpts " + str(c))

            st_dbscan = st.ST_DBSCAN(eps1 = a, eps2 = b, min_samples = c)
            st_dbscan.fit(data_normed)
            labels = st_dbscan.labels
            # remove outliers (-1)
            # create mask
            mask = labels > -1
            labels_nooutliers = labels[mask]
            data_normed_nooutliers = data_normed[mask]
            score = davies_bouldin_score(data_normed_nooutliers, labels_nooutliers)
            df_scores.loc[len(df_scores)] = [a, b, c, score]

            print("Score: " + str(score))

print(df_scores)

# -------------------------------------------------------------------------------------------------------------------
# RUN CLUSTERING WITH BEST PARAMETERS
# -------------------------------------------------------------------------------------------------------------------
# Previously chosen as best: 
best_eps1 = 0.0319
best_eps2 = 0.5
best_minpts = 9

filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)
print(filename)

#----- DBSCAN -----

st_dbscan = st.ST_DBSCAN(eps1 = best_eps1, eps2 = best_eps2, min_samples = best_minpts) 
st_dbscan.fit(data_normed)
mylabels = st_dbscan.labels

# Save
with open(f"{base_dir}/labels_" + filename + ".pkl", "wb") as f:
    pickle.dump(mylabels, f)
