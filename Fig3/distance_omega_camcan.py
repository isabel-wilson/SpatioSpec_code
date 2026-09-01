""""
Computes distances of OMEGA data from CAMCAN centroids. Computes null distribution. Plots

"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import math
import argparse

base_dir = "/scratch/isw3/distance_omega_camcan"

parser = argparse.ArgumentParser()
parser.add_argument("--hemi", type=str)
parser.add_argument("--segment", type=str)
parser.add_argument("--binlength", type=int)
args = parser.parse_args()

hemi = args.hemi
segment = args.segment
binlength = args.binlength

##### READ FILES 

# CENTROIDS
camcan_dir = f"{base_dir}/03_lh_rh_rerun"
camcan_COM_path = f"{camcan_dir}/mean_stc_COM_cluster_large_{hemi}.pkl" # non-within cluster: mean_stc_COM_8-30_{hemi}.pkl"
with open(camcan_COM_path, "rb") as f: 
   mean = pickle.load(f)
mean = np.column_stack([np.arange(8, 30, 0.25), mean])
mean = pd.DataFrame(mean, columns=["freq", "x", "y", "z"])

# INDIVIDUALS
omega_dir = f"{base_dir}/05_omega"
omega_individual_COM_path = f"{omega_dir}/COM_coord_subject_df_8_to_30_{segment}_{hemi}.pkl"
with open(omega_individual_COM_path, "rb") as f: 
   individuals = pickle.load(f)

print("done reading files")

##### ACTUAL DISTANCE
# Distance = sqrt((x-x)^2 + (y-y)^2 + (z-z)^2)
actual_distances = pd.DataFrame(columns = ["subject", "freq", "distance"])
for index, row in individuals.iterrows():
   subject = row["filename"]
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
   actual_distances.loc[len(actual_distances)] = [subject, freq, distance]

with open(f"{omega_dir}/omega-camcan_distance_cluster1/actual_{segment}_{hemi}.pkl", "wb") as f: 
   pickle.dump(actual_distances, f)
with open(f"{omega_dir}/omega-camcan_distance_cluster1/MEAN_actual_{segment}_{hemi}.txt", "w") as file:
    file.write(str(actual_distances["distance"].mean()))

print("done computing actual mean distance")

##### PERMUTATIONS 

null_distribution = []
for i in range(5000): 
   print(i)

   permuted_mean = mean.copy()
   freq_col = mean["freq"].to_list()
   starts = np.arange(0, 88, binlength)
   chunks = []
   for start in starts:
      chunk = freq_col[start:start + binlength]
      chunks.append(chunk)
   permuted_chunks = np.random.permutation(chunks)
   permuted_mean_clean = []
   for chunk in permuted_chunks:
      permuted_mean_clean.extend(chunk)
   permuted_mean["freq"] = permuted_mean_clean
      
   distances = pd.DataFrame(columns = ["subject", "freq", "distance"])
   for index, row in individuals.iterrows():
      subject = row["filename"]
      freq = row["freq"]
      x_individual = row["x"]
      y_individual = row["y"]
      z_individual = row["z"]
      x_mean = permuted_mean.loc[permuted_mean['freq'] == freq, 'x'].iloc[0]
      y_mean = permuted_mean.loc[permuted_mean['freq'] == freq, 'y'].iloc[0]
      z_mean = permuted_mean.loc[permuted_mean['freq'] == freq, 'z'].iloc[0]
      x_term = (x_individual - x_mean)**2
      y_term = (y_individual - y_mean)**2
      z_term = (z_individual - z_mean)**2
      distance = math.sqrt(x_term + y_term + z_term)
      distances.loc[len(distances)] = [subject, freq, distance]
   average_distance = distances["distance"].mean()
   null_distribution.append(average_distance)

with open(f'{omega_dir}/omega-camcan_distance_cluster1/null_5000perms_{binlength}_{segment}_{hemi}.txt', 'w') as f:
   for item in null_distribution:
      f.write(f"{item}\n")


# %%
import matplotlib.pyplot as plt

names = ["null_5000perms_1_full_lh"]

for name in names: 

   with open(f"C:/meg/params/05_omega/omega-camcan_distance_cluster1/{name}.txt", "r", encoding="utf-8") as file:
      floats = [float(line.strip()) for line in file]

   fig, ax = plt.subplots()
   ax.hist(np.subtract(100, floats), bins = 100, color = "#A3A3A3")
   ax.spines['top'].set_visible(False)
   ax.spines['right'].set_visible(False)
   ax.set_xlim(20, 40)
   #ax.set_xticklabels([])
   ax.set_ylim(0, 160)
   ax.set_yticks([])
   ax.set_yticklabels([])

   print(name)
   print(f"min: {str(min(np.subtract(100, floats)))}, max: {str(max(np.subtract(100, floats)))}")

# %%
name = "null_5000perms_11_full_rh"
actual = 62.59021744986827

with open(f"C:/meg/params/05_omega/omega-camcan_distance_cluster1/{name}.txt", "r", encoding="utf-8") as file:
      data = [float(line.strip()) for line in file]

len([x for x in data if x < actual])/len(data)
# %%
