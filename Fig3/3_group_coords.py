####  CENTROID USING ALL DATA
#%%
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

# User input
hemi = "rh"
base_dir = "C:/meg/params/05_omega"

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



# Frequencies to loop through
freqs = np.arange(8, 30, 0.25)

# List of list of center of masses
COM_coord_subject_list = []

# Load stc
file = os.path.join(base_dir, "mean_stc_full")
stc = mne.read_source_estimate(file)

# need this
inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"C:/meg/params/fs_subjects/fsaverage/surf/{hemi}.inflated")

# List of center of masses for this subject
COM_list = []

for f in freqs:
   t_stc = stc_one_timepoint(stc, f)

   if hemi=="lh": 
      relevant_data = t_stc.lh_data
   else: 
      relevant_data = t_stc.rh_data

   # If all vertices are 0, set center-of-mass to an array of nans
   if np.all(relevant_data==0): 
      COM_coord = np.array([np.nan, np.nan, np.nan])
   else:
      COM_vertex, _ = t_stc.get_peak(hemi=hemi)
      plot_stc(savedir = os.path.join(base_dir, "group_coords", hemi), brain_to_plot = t_stc, t = f, center_of_mass = COM_vertex)
      COM_coord = inflated_surface_rr[COM_vertex]
      COM_list.append(COM_coord)

make_3d_plot_spatiospec(savedir = os.path.join(base_dir, "group_coords"), COM_list = COM_list, name = hemi + " group centroids")

file = os.path.join(base_dir, f"mean_stc_full_COM_8-30_{hemi}.pkl") 
with open(file, "wb") as f:
    pickle.dump(COM_list, f)
# %%

file = os.path.join(base_dir, "mean_stc_full")
stc = mne.read_source_estimate(file)

stc.plot(
   subject="fsaverage",
   subjects_dir="C:/meg/params/fs_subjects",
   time_viewer = True
)


# %%
import re
for filename in ["sub-0155_psd_beamformer_fsaverage_whitened-rh.stc", "sub-0006_psd_beamformer_fsaverage_whitened-lh.stc", "sub-0063_psd_beamformer_fsaverage_whitened-rh.stc", "sub-0154_psd_beamformer_fsaverage_whitened-lh.stc"]:
   subject = re.search(r'sub-(\d+)', filename).group(1)
   if subject in subjects_exclude: 
      continue
   print(filename)
# %%

with open("C:/meg/params/05_omega/mean_stc_full_COM_8-30_lh.pkl", "rb") as f:
   df = pickle.load(f)
# %%
