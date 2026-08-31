""" 
This will plot group centroids (from cluster 1) on an STC

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

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
fs_dir = "C:/meg/params/fs_subjects"
hemi = "lh"

# Frequencies
freqs = np.arange(8, 30, 0.25)

# with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}_vertex.pkl"), "rb") as f:
 #  mean = pickle.load(f)
# inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{fs_dir}/fsaverage/surf/{hemi}.inflated")

stc = mne.read_source_estimate("C:/meg/params/mean_stc")

brain = stc.plot(
    subject="fsaverage",
    subjects_dir="C:/meg/params/fs_subjects",
    hemi=hemi,
    surface="inflated",
)

for vertex in mean["vertex"]:
   brain.add_foci(
      vertex,
      coords_as_verts=True,   
      hemi=hemi,
      color="white",
      scale_factor=0.5,  
      alpha=1.0,
   )
# %%
