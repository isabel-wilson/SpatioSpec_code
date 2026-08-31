#%%
# Import packages
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import math
import os

# User input
hemi = "lh"
base_dir = "C:/meg/params/03_lh_rh_rerun"


##### Read files

# CENTROIDS
# created by group_coords.py
# (1) Computed the subject-level average of the spectrum (2) Computed the peaks of this average
with open(os.path.join(base_dir, f"mean_stc_COM_8-30_{hemi}.pkl"), "rb") as f:
   mean = pickle.load(f)
mean = np.column_stack([np.arange(8, 30, 0.25), mean])
mean = pd.DataFrame(mean, columns=["freq", "x", "y", "z"])


# INDIVIDUALS
# created by individual_spread.py
# dataframe with cols subject, freq, x, y, z
with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}.pkl"), "rb") as f:
   individuals = pickle.load(f)

##### Distance = sqrt((x-x)^2 + (y-y)^2 + (z-z)^2)

# dataframe for output: 
# x y z mean is included to be helpful for later plotting
distances = pd.DataFrame(columns = ["subject", "freq", "distance"])

for index, row in individuals.iterrows():
   subject = row["subject"]
   freq = row["freq"]
   x_individual = row["x"]
   y_individual = row["y"]
   z_individual = row["z"]
   x_mean = mean.loc[mean['freq'] == freq, 'x'].iloc[0]
   y_mean = mean.loc[mean['freq'] == freq, 'y'].iloc[0]
   z_mean = mean.loc[mean['freq'] == freq, 'z'].iloc[0]
   x_term = (x_individual - x_mean)**2
   y_term = (y_individual - y_mean)**2
   z_term = (z_individual - z_mean)**2
   distance = math.sqrt(x_term + y_term + z_term)
   distances.loc[len(distances)] = [subject, freq, distance]

with open(os.path.join(base_dir, f"individual_distances_from_centroid_{hemi}.pkl"), "wb") as f: 
   pickle.dump(distances, f)

##### Normalize the distances to an approximation of the length of the cluster on its longest axis
# - the difference between the earliest and latest mean

with open(os.path.join(base_dir, f"mean_stc_COM_8-30_{hemi}.pkl"), "rb") as f:
   mean = pickle.load(f)

# First mean
first_x = mean[0][0]
first_y = mean[0][1]
first_z = mean[0][2]
last_x = mean[len(mean)-1][0]
last_y = mean[len(mean)-1][1]
last_z = mean[len(mean)-1][2]

# distance between first and last
x_term = (first_x - last_x)**2
y_term = (first_y - last_y)**2
z_term = (first_z - last_z)**2
distance_long_axis = math.sqrt(x_term + y_term + z_term)

# do the normalization
with open(os.path.join(base_dir, f"individual_distances_from_centroid_{hemi}.pkl"), "rb") as f: 
   distances = pickle.load(f)
distances["distance_normed"]= distances["distance"]/distance_long_axis

with open(os.path.join(base_dir, f"individual_distances_from_centroid_normalized_{hemi}.pkl"), "wb") as f: 
   pickle.dump(distances, f)

   
##### Plot

# Plot a histogram of distances (for each frequency)
# Loop through frequencies. For each frequency, plot histogram for subjects, then save. 
freqs = np.arange(8, 30, 0.25)

for f in freqs:
   print("Now working on " + str(f))

   # Subset the rows for this particular frequency
   df = distances.loc[distances['freq'] == f]
   # Get just the column distance, and nothing else (not even indices)
   distance_col = df["distance_normed"].values

   # Initialize figure
   fig = plt.figure()

   # Plot
   plt.hist(distance_col, bins = 100)

   # Add labels
   plt.title('Histogram of distances from centroid for frequency ' + str(f))
   plt.xlabel('Distance (normalized to distance between first and last centroid)')
   plt.ylabel('Count')
   plt.xlim(0, 1.6)
   plt.ylim(0, 40)

   # Save
   plt.savefig(os.path.join(base_dir, f"0315_subject_deviation_from_group_centroid_normed", hemi, str(f) + ".png"), dpi=300, bbox_inches=None)

# %%
