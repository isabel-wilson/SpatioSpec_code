
# %%
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
import matplotlib.colors as mcolors
import os
from matplotlib.colors import LinearSegmentedColormap

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
fs_dir = "C:/meg/params/fs_subjects"
hemi = "lh"

stc = mne.read_source_estimate(f"{base_dir}/mean_stc")

with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}_vertex.pkl"), "rb") as f:
   df = pickle.load(f)

#with open(os.path.join(base_dir, f"mean_stc_COM_cluster_large_lh.pkl"), "rb") as f:
#   df2 = pickle.load(f)

hex_color = "#ebe51a"  # your color here
rgb = mcolors.to_rgb(hex_color)  # (r, g, b) in 0-1 range

# build RGBA array: same color throughout, alpha ramps 0 -> 1
n = 256
colors_rgba = np.zeros((n, 4))
colors_rgba[:, 0] = rgb[0]  # R
colors_rgba[:, 1] = rgb[1]  # G
colors_rgba[:, 2] = rgb[2]  # B
colors_rgba[:, 3] = np.linspace(0, 1, n)  # alpha: transparent -> opaque

custom_cmap = LinearSegmentedColormap.from_list("hex_to_transparent", colors_rgba)

brain = stc.plot(
    subject="fsaverage",
    subjects_dir=fs_dir,
    hemi="rh",
    surface="inflated",
    background='white',
    cortex="white", 
    alpha = 1, 
    colormap = custom_cmap
   # clim=dict(kind='value', lims=[0,0,0])
)

#%%
src = mne.setup_source_space(
    "fsaverage", spacing="ico5", subjects_dir=fs_dir, add_dist=False
)

lh_rr_full, _ = mne.read_surface(f"{fs_dir}/fsaverage/surf/lh.inflated")
rh_rr_full, _ = mne.read_surface(f"{fs_dir}/fsaverage/surf/rh.inflated")

lh_vertno = src[0]["vertno"]       # ~4098 indices into the full-res lh mesh
rh_vertno = src[1]["vertno"]       # ~4098 indices into the full-res rh mesh

lh_use_tris = src[0]["use_tris"]   # triangulation among the kept lh vertices (0..n-1)
rh_use_tris = src[1]["use_tris"]

lh_rr_dec = lh_rr_full[lh_vertno]  # oct6 inflated coordinates, lh
rh_rr_dec = rh_rr_full[rh_vertno]  # oct6 inflated coordinates, rh

for i in lh_vertno[:300]:
    pointA = lh_use_tris[i, 0]
    pointB = lh_use_tris[i, 1]

    pointA_coords = lh_rr_full[pointA]
    pointB_coords = lh_rr_full[pointB]

    line_points = np.array([pointA_coords.tolist(), pointB_coords.tolist()])

    brain.plotter.add_lines(
        line_points, 
        color='grey', 
        width=5
        )
brain.plotter.render()


#%%

import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
import matplotlib.colors as mcolors
import os
from matplotlib.colors import LinearSegmentedColormap

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
fs_dir = "C:/meg/params/fs_subjects"
hemi = "lh"

stc = mne.read_source_estimate(f"{base_dir}/mean_stc")

with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}_vertex.pkl"), "rb") as f:
   df = pickle.load(f)

df_filtered = df.drop_duplicates(subset='vertex')

cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(np.unique(df["freq"])) - 1)
n = 0
for index, row in df_filtered.iterrows(): 
    n = n + 1
    print(n)
    rgba = cmap(norm((row["freq"]-8)/0.25))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        row["vertex"],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=0.5,
        alpha=1
    )

brain.save_image(os.path.join(base_dir, f"brain_all_lateral_{hemi}_vertex.png"))























#%%
#with open(os.path.join(base_dir, f"mean_stc_COM_clusterlarge_{hemi}_8-30_vertex.pkl"), "rb") as f:
#    mean = pickle.load(f)

#a = [127893, 135372, 130121, 20873, 111256, 95621, 98309, 131162, 115237, 17941, 140486, 124244]

ideals = e
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(ideals) - 1)
for i in range(len(ideals)): 
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        ideals[i],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1
    )

#%%
e = [15865] #18805,61509,156421,61232,38384,108386,123381,105697,32164,130966,131007,44331]

ideals = e
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(ideals) - 1)
for i in range(len(ideals)): 
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        ideals[i],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1
    )


inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"C:/meg/params/fs_subjects/fsaverage/surf/{hemi}.inflated")
for i in range(len(ideals)):
    mean_point = e[i]
    individual_point = a[i]

    mean_point_coord = inflated_surface_rr[mean_point]
    individual_point_coord = inflated_surface_rr[individual_point]

    line_points = np.array([mean_point_coord.tolist(), individual_point_coord.tolist()])

    brain.plotter.add_lines(
        line_points, 
        color='red', 
        width=15
        )
brain.plotter.render()








#%%
b = [13974,
  61451,
  9468,
  146926,
  11127,
  12279,
  26675,
  144917,
  65401,
  6163,
  29154]

ideals = b
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(ideals) - 1)
for i in range(len(ideals)): 
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        ideals[i],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1
    )

c = [38535,
  15170,
  141942,
  96750,
  58680,
  73758,
  95651,
  123398,
  76322,
  130949,
  34506,
  64096]

ideals = c
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(ideals) - 1)
for i in range(len(ideals)): 
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        ideals[i],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1
    )

d = [148659,
  126059,
  86014,
  141812,
  135046,
  139738,
  144656,
  103342,
  81475,
  227,
  129521,
  145257]

ideals = c
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(ideals) - 1)
for i in range(len(ideals)): 
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        ideals[i],
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1
    )




#%%
#%%
#%%
ideals = [127893, 135372, 130121, 20873, 111256, 95621, 98309, 131162, 115237, 17941, 140486, 124244]

for red in reds: 
   brain.add_foci(
        red,
        coords_as_verts=True,
        hemi=hemi,
        color="red",
        scale_factor=1.5,
        alpha=1.0,
    )


# %%
import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
import matplotlib.colors as mcolors
import matplotlib

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"
fs_dir = "C:/meg/params/fs_subjects"
name = "large"
hemi = "lh"

# Frequencies
freqs = np.arange(8, 30, 0.25)

with open(os.path.join(base_dir, f"mean_stc_COM_cluster{name}_{hemi}_8-30_vertex.pkl"), "rb") as f:
    mean = pickle.load(f)

stc = mne.read_source_estimate("C:/meg/params/mean_stc")

brain = stc.plot(
    subject="fsaverage",
    subjects_dir=fs_dir,
    hemi=hemi,
    surface="inflated",
    background='white',
    cortex="white", 
    alpha = 0.5
)

vertices = [127893, 135372, 130121, 20873, 111256, 95621, 98309, 131162, 115237, 17941, 140486, 124244]

cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(vertices) - 1)
for i, vertex in enumerate(vertices):
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        vertex,
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=1,
        alpha=1,
    )

#%%
reds = [86259, 156460, 78150, 156128, 32444, 106828, 99968, 150784, 80060, 48612, 4000, 94685, 144499, 92579, 65452, 105978, 50594, 152580]

for red in reds: 
    brain.add_foci(
        red,
        coords_as_verts=True,
        hemi=hemi,
        color="red",
        scale_factor=0.8,
        alpha=1.0,
 )


# %%

#%%
 

stc = mne.read_source_estimate("C:/meg/params/mean_stc")

brain = stc.plot(
    subject="fsaverage",
    subjects_dir=fs_dir,
    hemi=hemi,
    surface="inflated",
    background='white',
    cortex="white"
)

with open('C:/meg/params/03_lh_rh_rerun/figure1_lh_alpha.txt', 'r', encoding='utf-8') as file:
    lines = file.read().splitlines()

for line in lines:
    brain.add_foci(
        int(line),
        coords_as_verts=True,
        hemi=hemi,
        color="#481A6C",
        scale_factor=0.5,
        alpha=1.0
    )

with open('C:/meg/params/03_lh_rh_rerun/figure1_lh_beta.txt', 'r', encoding='utf-8') as file:
    lines = file.read().splitlines()

for line in lines:
    brain.add_foci(
        int(line),
        coords_as_verts=True,
        hemi=hemi,
        color="#C8E020",
        scale_factor=0.5,
        alpha=1.0
    )

# %%
point_a = [-38, -60.6, 26.4]
point_b = [-36.7, -82.2, 27.2]
line_points = np.array([point_a, point_b])

brain.plotter.add_lines(
    line_points, 
    color='red', 
    width=5, 
    name='my_custom_line'
)

brain.plotter.render()





# %%
# %%
# %%
# %%
# %%

import mne
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
import pickle
import os
from datetime import datetime
import matplotlib.colors as mcolors

# User input
base_dir = "C:/meg/params/0_SpatioSpec_results"
fs_dir = "C:/meg/params/fs_subjects"
name = "large"
hemi = "rh"

stc = mne.read_source_estimate("C:/meg/params/mean_stc")

brain = stc.plot(
    subject="fsaverage",
    subjects_dir="C:/meg/params/fs_subjects",
    hemi=hemi,
    surface="inflated",
    background='white',
    clim=dict(kind='value', lims=[0,0,0]),
    alpha = 1,
    time_label=None,
    colorbar=False,
    time_viewer = False,
    cortex='white'
)

with open(os.path.join(base_dir, f"mean_stc_COM_cluster_{name}_{hemi}_8-30_vertex.pkl"), "rb") as f:
    mean = pickle.load(f)

vertices = mean
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=len(vertices) - 1)
for i, vertex in enumerate(vertices):
    rgba = cmap(norm(i))
    color = mcolors.to_hex(rgba)
    brain.add_foci(
        vertex,
        coords_as_verts=True,
        hemi=hemi,
        color=color,
        scale_factor=0.7,
        alpha=1,
    )

#%%
with open(os.path.join(base_dir, f"COM_coord_subject_df_8_to_30_{hemi}_vertex.pkl"), "rb") as f:
   individuals = pickle.load(f)

individual = individuals[individuals["subject"] == "310051"]
individual_points = individual["vertex"].to_numpy()

#reds = [86259, 156460, 78150, 156128, 32444, 106828, 99968, 150784, 80060, 48612, 4000, 94685, 144499, 92579, 65452, 105978, 50594, 152580]

for individual_point in individual_points: 
    brain.add_foci(
        individual_points,
        coords_as_verts=True,
        hemi=hemi,
        color="red",
        scale_factor=0.5,
        alpha=1.0,
 )

inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"C:/meg/params/fs_subjects/fsaverage/surf/{hemi}.inflated")
for i in range(len(individual_points)):
    mean_point = vertices[i]
    individual_point = individual_points[i]

    mean_point_coord = inflated_surface_rr[mean_point]
    individual_point_coord = inflated_surface_rr[individual_point]

    line_points = np.array([mean_point_coord.tolist(), individual_point_coord.tolist()])

    brain.plotter.add_lines(
        line_points, 
        color='red', 
        width=5
        )
brain.plotter.render()

#%%

with open(f"C:/meg/params/05_omega/actual_lh.pkl", "rb") as f:
    mean = pickle.load(f)

plt.hist(mean["distance"], bins = 100)
# %%
