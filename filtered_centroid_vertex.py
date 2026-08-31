""" 
This version computes the cluster-level centroids straight from the individual-level COMs
There is also a section that counts the number of points each participant has in the two main clusters

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
from collections import Counter

# User input
base_dir = "C:/meg/params/0_SpatioSpec_results"
fs_dir = "C:/meg/params/fs_subjects"
hemi = "rh"
cluster = [1]
name = "large"

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

def percentage_table(arr):
    total = len(arr)
    freq = Counter(arr)
    table = [(num, (count / total) * 100) for num, count in freq.items()]
    table.sort(key=lambda x: -x[1])
    return table

arr = labels
for num, perc in percentage_table(arr):
    print(f"{num}: {perc:.2f}%")


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
new_folder_name = f"{base_dir}/{time}_centroid_cluster{name}_{hemi}_vertex"

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
      vertex = row[2:].to_numpy()
      
      # Create an array with 0s everywhere, except for a 1 at given vertex, or more than 1 if two subjects are there
      stc_data[vertex[0], 0] = stc_data[vertex[0], 0] + 1

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
      os.makedirs(new_folder_name, exist_ok=True)
      plot_stc(savedir = new_folder_name, brain_to_plot = stc, t = f, center_of_mass = COM_vertex)
         
      # Add to list of centroids
      COM_list.append(COM_vertex)

   else: 
      continue

#make_3d_plot_spatiospec(savedir = new_folder_name, COM_list = COM_list, name = f"{hemi} cluster {name} centroids")

file = os.path.join(base_dir, f"mean_stc_COM_cluster_{name}_{hemi}_8-30_vertex.pkl") 
with open(file, "wb") as f:
    pickle.dump(COM_list, f)





#%%
import matplotlib.colors as mcolors
import numpy as np
import matplotlib.pyplot as plt
import mne

def lighten_color(hex_color, amount):
    """amount: 0 = white, 1 = original color"""
    rgb = mcolors.to_rgb(hex_color)
    white = np.array([1, 1, 1])
    return tuple(white + amount * (np.array(rgb) - white))

def darken_color(hex_color, amount):
    """amount: 0 = black, 1 = original color"""
    rgb = mcolors.to_rgb(hex_color)
    black = np.array([0, 0, 0])
    return tuple(black + amount * (np.array(rgb) - black))

base_color = "#20a486" #"#481c6e" # 

# Build a light -> dark gradient through the base color
white = lighten_color("white", 0.5)
light = lighten_color(base_color, 0.25)   # near-white tint
mid   = base_color
dark  = darken_color(base_color, 0.25)     # near-black shade

custom_cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_purple",
    [white, white, light, mid]
)


fig, ax = plt.subplots(figsize=(4, 1))
gradient = np.linspace(0, 1, 256).reshape(1, -1)
ax.imshow(gradient, aspect="auto", cmap=custom_cmap)

# hide ticks but keep the spines for a border
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color("black")
    spine.set_linewidth(1)

plt.show()

fs_dir = "C:/meg/params/fs_subjects"

stc = mne.read_source_estimate("C:/meg/params/03_lh_rh_rerun/mean_stc")
# times: 1 to 40 in 0.25 increments

# alpha 8-12, beta 15-30
stc_cropped = stc.copy().crop(tmin=15, tmax=30)
avg_data = stc_cropped.data.mean(axis=1)
print(np.min(avg_data))
print(np.max(avg_data))
print(np.min(avg_data)+((np.max(avg_data)-np.min(avg_data))/2))
avg_stc = mne.SourceEstimate(
    avg_data[:, np.newaxis],
    vertices=stc.vertices,
    tmin=0, tstep=1)
avg_stc.plot(
    subject="fsaverage",
    subjects_dir=fs_dir,
    hemi="rh",
    surface="inflated",
    background='white',
    cortex="white", 
    alpha = 1, 
    clim = dict(kind="percent", lims=[0, 40, 80]),
    colormap = custom_cmap
)
# mne defaults are clim = dict(kind="percent", lims=[96, 97.5, 99.95])

# %%
