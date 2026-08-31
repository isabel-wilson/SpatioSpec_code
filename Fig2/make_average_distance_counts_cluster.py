#%%
#---------------------------------------------------------
#---------- Count points per participant in each cluster and compute average
#---------------------------------------------------------

# Import packages
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
from collections import Counter
import sys

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
hemi = sys.argv[1]
cluster = sys.argv[2] # "large" # outliers-no_large

# LOAD LABELS
best_eps1 = 0.0319
best_eps2 = 0.5
best_minpts = 9
filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)
with open(f"{base_dir}/labels_{filename}.pkl", "rb") as f:
   labels = pickle.load(f)

# Create binarized mask, where 1 is "points of current interest"
if hemi == "rh": 
   if cluster == "large": 
      mask = labels == 1 # for rh, large cluster is "1"
   elif cluster == "small": 
      mask = labels == 0 # for rh, small cluster is "0"
   elif cluster == "outliers-no_large":
      mask = ~np.isin(labels, [0, 1])
   else: 
      print("bad input")
elif hemi == "lh": 
   if cluster == "large": 
      mask = labels == 2 # for lh, large cluster is "2"
   elif cluster == "small": 
      mask = labels == 0 # for lh, small cluster is "0"
   elif cluster == "outliers-no_large":
      mask = ~np.isin(labels, [0, 2])
   else: 
      print("bad input")
else: 
   print("bad input")

# LOAD DISTANCES
# created earlier in this file
with open(os.path.join(base_dir, f"individual_distances_from_centroid_cluster_{cluster}_{hemi}_normalized.pkl"), "rb") as f:
   distances = pickle.load(f)

# FILTER: Apply mask to distances
filtered = distances[mask]
filtered = filtered[filtered["freq"] < 12]
#filtered.to_csv(f"filtered_{cluster}_{hemi}.csv")

all_subjects = distances["subject"].unique()

# Create new dataframe
filtered_stats = (
   filtered.groupby("subject")
   .agg(
      number_in_cluster=("subject", "count"),
      avdist_normed_in_cluster=("distance_normed", "mean"), 
      avdist_unnormed_in_cluster=("distance", "mean")
   )
   .reindex(all_subjects)
   .reset_index()
)

filtered_stats["number_in_cluster"] = filtered_stats["number_in_cluster"].fillna(0).astype(int)

# Add in a column for average_distance_all
distances_stats = (
   distances.groupby("subject")
   .agg(
      avdist_normed_all=("distance_normed", "mean"), 
      avdist_unnormed_all=("distance", "mean")
   )
   .reset_index()
)

stats = filtered_stats.merge(distances_stats, on="subject")

# Save
stats.columns = ["subject", f"number_in_cluster_{cluster}_{hemi}", f"avdist_normed_in_cluster_{cluster}_{hemi}", f"avdist_unnormed_in_cluster_{cluster}_{hemi}", f"avdist_normed_all_{cluster}_{hemi}", f"avdist_unnormed_all_{cluster}_{hemi}"]
stats.to_feather(os.path.join(base_dir, f"average_distance_counts_cluster_{cluster}_{hemi}_8-30.rds"))


# Plot to check
# filtered_stats["average_distance_in_cluster"].hist(bins=30)
# plt.xlabel("average_distance_in_cluster")
# plt.ylabel("number of subjects")
# plt.title(cluster_of_interest + " - " + hemi)
# plt.tight_layout()
# plt.show()

# filtered_stats["number_in_cluster"].hist(bins=30)
# plt.xlabel("count of points within cluster (max possible = 88)")
# plt.ylabel("number of subjects")
# plt.title(cluster_of_interest + " - " + hemi)
# plt.xlim(0, 88)
# plt.tight_layout()
# plt.show()

# plt.scatter(stats["number_in_cluster"], stats["average_distance_in_cluster"], label="in cluster")
# plt.scatter(stats["number_in_cluster"], stats["average_distance_all"], label="all")
# plt.xlabel("count of points within cluster (max possible = 88)")
# plt.ylabel("average distance")
# plt.title(cluster_of_interest + " - " + hemi)
# plt.legend()
# plt.xlim(0, 88)
# plt.tight_layout()
# plt.show()


#%%
