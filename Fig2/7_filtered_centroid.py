""" 
1. Computes cluster-specific group centroid per frequency
2. Computes each individual's distance from that cluster centroid
3. Normalizes distances by the approx width of the cluster along its main axis
4. Convert to R-readable format

"""
#%%
# Import packages
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
import math

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
fs_dir = "C:/meg/params/fs_subjects"
hemi = "lh"
cluster = [0]
name = "small"
iteration = "small"

# Frequencies
freqs = np.arange(8, 30, 0.25)

#---------------------------------------------------------
#---------- Useful functions
#---------------------------------------------------------

def stc_one_timepoint(stc, t): 
   """
   Given an stc with multiple timepoints, create a new stc that contains 
   only the given timepoint. The stc will be symmetrical, with the right side a 
   copy of the left.
   """

   # Create a new stc that contains only this timepoint
   if hemi == "lh": 
      t_stc_side_data = stc.lh_data[:, stc.time_as_index(t)]
   else: 
      t_stc_side_data = stc.rh_data[:, stc.time_as_index(t)]

   # Find top 20% of the positive; set everything below to 0
   t_stc_side_data[t_stc_side_data < 0] = 0
   lim = np.percentile(t_stc_side_data, 80)
   t_stc_side_data[t_stc_side_data < lim] = 0

   # Bind lh and rh together
   t_stc_lh_rh_data = np.vstack((t_stc_side_data, t_stc_side_data))

   # Make stc (both hemi)
   t_stc = mne.SourceEstimate(
      data = t_stc_lh_rh_data, 
      vertices=stc.vertices,
      tmin=t, 
      tstep=stc.tstep
   )
   
   return t_stc

# not needed for now
def plot_stc(savedir, brain_to_plot, t, center_of_mass): 
   """
   Plots the given brain at the given time with a dot at the center of mass
   """
   brain = brain_to_plot.plot(
      subject="fsaverage",
      subjects_dir="C:/meg/params/fs_subjects",
      hemi=hemi,
      initial_time=t,
      time_viewer=False,
      time_label="Frequency " + f"{t:.{2}f}",
      colormap="viridis", 
      surface = 'inflated'
      )
   brain.add_foci(center_of_mass, coords_as_verts=True, hemi=hemi, color='red', scale_factor=1.0)
   brain.show_view("dorsal")
   brain.save_image(savedir + "/" + str(t) + ".png")

# not needed for now
def make_3d_plot_spatiospec(savedir, COM_list, name):

   palette_col1 = np.linspace(0, 1, len(COM_list))[:, None]
   palette_col2 = np.zeros(len(COM_list))[:, None]
   palette_col3 = np.zeros(len(COM_list))[:, None]
   palette = np.hstack((palette_col1, palette_col2, palette_col3))

   fig = plt.figure()
   ax = fig.add_subplot(111, projection='3d')

   for i in range(0, len(COM_list)): 
      trip = COM_list[i]
      print("Coordinate: " + str(trip))
      x = trip[0]
      y = trip[1]
      z = trip[2]
      ax.scatter(xs = x, ys = y, zs = z, color=palette[i], s = 4)

   ax.set_zlabel("z (up)")
   ax.set_xlabel(f"x (right), on {hemi}")
   ax.set_ylabel("y (front)")
   ax.set_zlim(-80, 80)
   ax.set_xlim(-40, 40)
   ax.set_ylim(-100, 100)
   ax.set_title(name)

   fig.savefig(savedir + "/" + name + ".png", dpi=300, bbox_inches=None)



#-------------------------------------------------------
#---------- Filter list of COMS by label
#---------------------------------------------------------

# Load labels
best_eps1 = 0.0319
best_eps2 = 0.5
best_minpts = 9
filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)
with open(f"{base_dir}/labels_{filename}.pkl", "rb") as f:
   labels = pickle.load(f)

# Load list of COMs
with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}_vertex.pkl"), "rb") as f:
   COM_coord_subject_df = pickle.load(f)

# Filter
mask = np.isin(labels, cluster)
df_filtered = COM_coord_subject_df[mask]


#---------------------------------------------------------
#---------- Compute COM of COMs
#---------------------------------------------------------
"""
Loop through freqs. For each freq: (1) Extract relevant rows
(2) Join them to produce a new array 
(3) Compute the centroid 

"""
# Need this
inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{fs_dir}/fsaverage/surf/{hemi}.inflated")

# to save images in
time = datetime.now().strftime("%m-%d_%H-%M")
new_folder_name = f"{base_dir}/{time}_centroid_cluster_{name}_{hemi}"

# Output list
COM_list = []

# Loop through freqs
for f in freqs: 
   print(f)

   df_filtered_f = df_filtered.loc[df_filtered['freq'] == f]

   # stc_data for this freq
   stc_data = np.zeros(shape = (inflated_surface_rr.shape[0], 1))

   # For each point: 
   for col_i, (index, row) in enumerate(df_filtered_f.iterrows()):

      # Pull out coordinate and convert to vertex
      vertex = row[2:].to_numpy()[0]
      #vertex = np.where((inflated_surface_rr == coord).all(axis=1))[0][0]
      
      # Create an array with 0s everywhere, except for a 1 at given vertex, or more than 1 if two subjects are there
      stc_data[vertex, 0] = stc_data[vertex, 0] + 1

   if np.any(stc_data!=0): 

      # Convert to stc
      stc_data_bothhemi = np.vstack((stc_data, stc_data))
      stc = mne.SourceEstimate(
         data = stc_data_bothhemi,
         vertices=[np.arange(0, inflated_surface_rr.shape[0]), np.arange(0, inflated_surface_rr.shape[0])],
         tmin=0,
         tstep=1
      )

      # Compute centroid
      if hemi == "lh": 
         hemi_param = 0
      else: 
         hemi_param = 1
      COM_vertex, _, _ = stc.center_of_mass(hemi=hemi_param, subject = "fsaverage", subjects_dir = "C:/meg/params/fs_subjects")

      # Plot for checking
      # os.makedirs(new_folder_name, exist_ok=True)
      # plot_stc(savedir = new_folder_name, brain_to_plot = stc, t = f, center_of_mass = COM_vertex)
         
      # Add to list of centroids
      COM_coord = inflated_surface_rr[COM_vertex]
      row = np.insert(COM_coord, 0, f)
      COM_list.append(row)

   else: 
      COM_list.append(np.array([f, 0, 0, 0]))

#make_3d_plot_spatiospec(savedir = new_folder_name, COM_list = COM_list, name = f"{hemi} cluster {name} centroids")

file = os.path.join(base_dir, f"mean_stc_COM_cluster_{name}_{hemi}.pkl") 
with open(file, "wb") as f:
    pickle.dump(COM_list, f)


#---------------------------------------------------------
#---------- Subject deviation from group centroid
#---------------------------------------------------------


# User input
# freqs_og = np.arange(8, 30, 0.25) # because some of the files you will load have this format
# freqs = np.arange(10, 30, 0.25)


##### Read files

# CENTROIDS
# created earlier in this script
# list
with open(os.path.join(base_dir, f"mean_stc_COM_cluster_{iteration}_{hemi}.pkl"), "rb") as f:
   mean = pickle.load(f)
#mean = np.column_stack([freqs_og, mean])
mean = pd.DataFrame(mean, columns=["freq", "x", "y", "z"])
freqs_used = np.unique(mean["freq"])
#mean = mean[mean["freq"].isin(freqs)]

# INDIVIDUALS
# created by individual_spread.py
# dataframe with cols subject, freq, x, y, z
with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}.pkl"), "rb") as f:
   individuals = pickle.load(f)
individuals = individuals[individuals["freq"].isin(freqs_used)]


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

with open(os.path.join(base_dir, f"individual_distances_from_centroid_cluster_{iteration}_{hemi}.pkl"), "wb") as f: 
   pickle.dump(distances, f)



##### Normalize the distances to an approximation of the length of the cluster on its longest axis
# - the difference between the earliest and latest mean

with open(os.path.join(base_dir, f"mean_stc_COM_cluster_{iteration}_{hemi}.pkl"), "rb") as f:
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
with open(os.path.join(base_dir, f"individual_distances_from_centroid_cluster_{iteration}_{hemi}.pkl"), "rb") as f: 
   distances = pickle.load(f)
distances["distance_normed"]= distances["distance"]/distance_long_axis

with open(os.path.join(base_dir, f"individual_distances_from_centroid_cluster_{iteration}_{hemi}_normalized.pkl"), "wb") as f: 
   pickle.dump(distances, f)


##### Plot

# Plot a histogram of distances (for each frequency)
# Loop through frequencies. For each frequency, plot histogram for subjects, then save. 

# for f in freqs:
#    print("Now working on " + str(f))

#    # Subset the rows for this particular frequency
#    df = distances.loc[distances['freq'] == f]
#    # Get just the column distance, and nothing else (not even indices)
#    distance_col = df["distance_normed"].values

#    # Initialize figure
#    fig = plt.figure()

#    # Plot
#    plt.hist(distance_col, bins = 100)

#    # Add labels
#    plt.title('Histogram of distances from centroid for frequency ' + str(f))
#    plt.xlabel('Distance (normalized to distance between first and last centroid)')
#    plt.ylabel('Count')
#    plt.xlim(0, 1.6)
#    plt.ylim(0, 40)


#---------------------------------------------------------
#---------- Convert pkl to rds, for next step in R
#---------------------------------------------------------
path = os.path.join(base_dir, f"individual_distances_from_centroid_cluster_{iteration}_{hemi}")

with open(path + ".pkl", "rb") as f:
   data = pickle.load(f)

data.to_feather(path + ".rds")


# %%
