#%%
"""
Pipeline for producing data related to the "SpatioSpec" project 

This code runs continuously - i.e., set your directories up like described, and outputs will appear in /Data and /plots. 
Outputs in /plots are basic statistics and plots you can use to verify results in the manuscript. 

-------------------------------------------------------------------------------------------------------------------
OVERVIEW: 

SECTION 1: CAMCAN ANALYSES
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 runs ST-DBSCAN
- STEP 3 computes the centroids of large and small clusters
- STEP 4 computes the "distance" of individual participants' clusters from these centroids
- STEP 5 tests colocalization with the FC gradient

SECTION 2: OMEGA ANALYSES
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 computes actual and permuted distance of step 1 outputs from the centroids of the CAM-CAN data
- STEP 3 computes summary statistics for step 2

---------------------------------------------------------------------------------------------------------------------
"""

# -------------------------------------------------------------------------------------------------------------------
# Import packages
# -------------------------------------------------------------------------------------------------------------------

import os
import sys
import math
import pickle
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne


# -------------------------------------------------------------------------------------------------------------------
# Set directories
# -------------------------------------------------------------------------------------------------------------------

base_dir = "scratch/isw3/SpatioSpec/Data/" # USER INPUT

fs_dir = f"{base_dir}/fs_subjects"

# Make directories
os.makedirs(f"{base_dir}/plots", exist_ok=True)
os.makedirs(f"{base_dir}/omega-camcan_distance_cluster1", exist_ok=True)


# -------------------------------------------------------------------------------------------------------------------
""" -----------------------------------------------------------------------------------------------------------------
CAMCAN ANALYSES
Pipeline for analyses related to the CAM-CAN data

OVERVIEW
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 runs ST-DBSCAN
---- You may be interested in how the ST-DBSCAN parameters used here were initially chosen - see the choose_st-dbscan_parameters.py script
- STEP 3 computes the centroids of large and small clusters
- STEP 4 computes the "distance" of individual participants' clusters from these centroids
---- After step 4 in this python script, use the demographics_cognitive_regression.R script to test associations between distance and demographics/cognitive measures
- STEP 5 tests colocalization with the FC gradient

"""
# -------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------------------------
"""
STEP 1: COMPUTE INDIVIDUAL-LEVEL FREQUENCY-WISE OSCILLATORY PEAKS
For each subject, compute the spatial location of the peak power for each frequency - i.e., "subject trajectory"

Input:
- CAMCAN_subject_list.txt
- Imaging_data/CAMCAN_whitened_stc folder of {subject}_psd_beamformer_fsaverage_whitened-{hemi}.stc

Output:
- CAMCAN_individual_peaks_{hemi}.pkl - for each subject and frequency, the coordinates of the peak power in that frequency
- CAMCAN_individual_peaks_{hemi}_vertex.pkl - same as first, but in vertex numbers instead of coordinates
- CAMCAN_individual_peaks_{hemi}_normalized.pkl - same as first, but with coordinates normalized by their max/min

"""
# -------------------------------------------------------------------------------------------------------------------

# Set up
freqs = np.arange(8, 30, 0.25)

# Useful function
def stc_one_timepoint(stc, t, hemi):
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

# Load subjects
with open(f"{base_dir}/CAMCAN_subject_list.txt") as f:
    subjects = f.read().split()

for hemi in ["lh", "rh"]:
    inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{fs_dir}/fsaverage/surf/{hemi}.inflated")

    # Empty dataframe
    individual_peaks_coord_df = pd.DataFrame(columns=["subject", "freq", "x", "y", "z"])
    individual_peaks_vertices_df = pd.DataFrame(columns=["subject", "freq", "vertex"])

    for subject in subjects:

        file = f"{base_dir}/Imaging_data/CAMCAN_whitened_stc/{subject}_psd_beamformer_fsaverage_whitened"
        stc = mne.read_source_estimate(file)

        for f in freqs:
            t_stc = stc_one_timepoint(stc, f, hemi)

            if hemi=="lh":
                relevant_data = t_stc.lh_data
            else:
                relevant_data = t_stc.rh_data

            # If all vertices are 0, set peak to an array of nans
            if np.all(relevant_data==0):
                individual_peaks_coord_df.loc[len(individual_peaks_coord_df)] = [subject, f, None, None, None]
                individual_peaks_vertices_df.loc[len(individual_peaks_vertices_df)] = [subject, f, None]
            else:
                COM_vertex, _ = t_stc.get_peak(hemi=hemi)
                COM_coord = inflated_surface_rr[COM_vertex] # this gives you an array
                individual_peaks_coord_df.loc[len(individual_peaks_coord_df)] = [subject, f, COM_coord[0], COM_coord[1], COM_coord[2]]
                # For plotting and the FCgradient analysis later, you need to gather locations as vertices also
                individual_peaks_vertices_df.loc[len(individual_peaks_vertices_df)] = [subject, f, COM_vertex]

    # Write to file
    with open(f"{base_dir}/CAMCAN_individual_peaks_{hemi}.pkl", "wb") as f:
        pickle.dump(individual_peaks_coord_df, f)
    with open(f"{base_dir}/CAMCAN_individual_peaks_{hemi}_vertex.pkl", "wb") as f:
        pickle.dump(individual_peaks_vertices_df, f)

    # Normalize and write normalized version to file
    individual_peaks_coord_df['x'] = individual_peaks_coord_df['x'] + 100
    individual_peaks_coord_df['x'] = (individual_peaks_coord_df['x'] - individual_peaks_coord_df['x'].min()) / (individual_peaks_coord_df['x'].max() - individual_peaks_coord_df['x'].min())
    individual_peaks_coord_df['y'] = individual_peaks_coord_df['y'] + 100
    individual_peaks_coord_df['y'] = (individual_peaks_coord_df['y'] - individual_peaks_coord_df['y'].min()) / (individual_peaks_coord_df['y'].max() - individual_peaks_coord_df['y'].min())
    individual_peaks_coord_df['z'] = individual_peaks_coord_df['z'] + 100
    individual_peaks_coord_df['z'] = (individual_peaks_coord_df['z'] - individual_peaks_coord_df['z'].min()) / (individual_peaks_coord_df['z'].max() - individual_peaks_coord_df['z'].min())

    with open(f"{base_dir}/CAMCAN_individual_peaks_{hemi}_normalized.pkl", "wb") as f:
        pickle.dump(individual_peaks_coord_df, f)


# -------------------------------------------------------------------------------------------------------------------
"""
STEP 2: ST-DBSCAN
Use ST-DBSCAN to label points. Parameters were previously selected using the steps described in choose_st-dbscan_parameters.py
Requires: https://github.com/eren-ck/st_dbscan/blob/7591838bca5f4d138926219d3ae939cb282c39b4/src/st_dbscan/st_dbscan.py

Input:
For each hemi:
- CAMCAN_individual_peaks_{hemi}_normalized.pkl

Output:
For each hemi:
- labels... pkl, where file name includes parameters

Also outputs things for you to look at: counts of labels and a plot/sketch of the large cluster (main result)

"""
# -------------------------------------------------------------------------------------------------------------------

# Import previously downloaded st-dbscan code: https://github.com/eren-ck/st_dbscan/blob/7591838bca5f4d138926219d3ae939cb282c39b4/src/st_dbscan/st_dbscan.py
sys.path.append(base_dir)
import st_dbscan as st

#----- Useful functions for plotting

def plot_color_by_freq(data, savedir):
    """
    Plots with points colored according to frequency
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(xs = data[:, 1], ys = data[:, 2], zs = data[:, 3], c = data[:, 0], cmap = 'viridis', s = 1)

    ax.set_zlabel("z (up)")
    ax.set_xlabel(f"x (right), on {hemi}")
    ax.set_ylabel("y (front)")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_zlim(-100, 100)
    ax.view_init(azim=20, elev=0)
    fig.savefig(savedir, dpi=300, bbox_inches="tight", pad_inches=1)
    plt.ion()

def plot(data, labels, savedir):
    """
    Plots with points colored by cluster (label)
    This code is partly based on https://github.com/eren-ck/st_dbscan
    """
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 2, projection='3d')

    colors = ["#F80606",'#33a02c', '#1f78b4','#ff7f00','#6a3d9a','#b2df8a','#fb9a99','#a6cee3','#fdbf6f','#cab2d6',]
    #colors = ['#00000000','#00000000','#00000000']
    #colors= ['#00000000','#00000000','#33a02c']

    # For every label:
    # Choose a colour for the label
    # Pick out all the rows in the data that have this label
    # Plot everything for this label
    # Move on to next label
    for i in range(-1, len(set(labels))):
        if i == -1:
            col = [0, 0, 0, 1] #continue # does not print noise; alternatively, you could colour noise black:
        else:
            col = colors[i % len(colors)]

        clust = data[np.where(labels==i)]

        ax.scatter(xs = clust[:,0], ys = clust[:,1], zs = clust[:,2], c=[col], s = 0.1, marker = '.')

    ax.set_zlabel("z (up)")
    ax.set_xlabel(f"x (right), on {hemi}")
    ax.set_ylabel("y (front)")
    ax.set_xlim(-40, 40)
    ax.set_ylim(-100, 100)
    ax.set_zlim(-75, 75)
    #  https://matplotlib.org/stable/api/toolkits/mplot3d/view_angles.html
    if hemi == "rh":
        ax.view_init(azim=250)

    fig.tight_layout()
    fig.savefig(savedir, dpi=300, bbox_inches="tight", pad_inches=1)



#---- PARAMETERS (previously selected)
best_eps1 = 0.0319
best_eps2 = 0.5
best_minpts = 9

results = {}
cluster_ids = {"lh": (2, 0), "rh": (1, 0)}  # (large, small) (labelled differently by st_dbscan per hemisphere)

for hemi in ["lh", "rh"]:

    #----- Load data
    with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}_normalized.pkl"), "rb") as f:
        CAMCAN_individual_peaks_normalized = pickle.load(f)
    data_normed = CAMCAN_individual_peaks_normalized.loc[:, ['freq','x','y','z']].values

    filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)

    #----- Run dbscan
    st_dbscan = st.ST_DBSCAN(eps1 = best_eps1, eps2 = best_eps2, min_samples = best_minpts)
    st_dbscan.fit(data_normed)
    labs = st_dbscan.labels

    with open(f"{base_dir}/labels_" + filename + ".pkl", "wb") as f:
        pickle.dump(labs, f)

    #---- Start preparing to compute statistics
    labs = np.array(labs)
    large, small = cluster_ids[hemi]
    results[hemi] = [np.mean(labs == large) * 100, np.mean(labs == small) * 100,
                     len(set(labs)) - 3, np.mean(labs == -1) * 100]

    #----- Plot
    with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}.pkl"), "rb") as f:
        CAMCAN_individual_peaks_df = pickle.load(f)
    data = CAMCAN_individual_peaks_df.loc[:, ['freq','x','y','z']].values
    mask = labs == cluster_ids[hemi][0]  # large cluster
    plot_color_by_freq(data[mask], f"{base_dir}/plots/Fig2B_" + filename + "_large.png")
    plot(data[:, 1:], labs, f"{base_dir}/plots/Fig2B_" + filename + "_clusters.png")

#----- Save statistics
lh, rh = results["lh"], results["rh"]
with open(f"{base_dir}/plots/cluster_summary.txt", "w") as f:
    f.write(f"percentage of points in largest cluster --- lh: {lh[0]:.2f}, rh: {rh[0]:.2f}\n")
    f.write(f"percentage of points in smaller cluster --- lh: {lh[1]:.2f}, rh: {rh[1]:.2f}\n")
    f.write(f"number of other clusters --- lh: {lh[2]}, rh: {rh[2]}\n")
    f.write(f"percentage of points in outliers --- lh: {lh[3]:.2f}, rh: {rh[3]:.2f}\n")


# -------------------------------------------------------------------------------------------------------------------
"""
STEP 3: CENTROIDS OF CLUSTERS
Computes the group mean of points within the large cluster, and the group mean of points within the small cluster

Input:
- labels... pkl
- CAMCAN_individual_peaks_{hemi}.pkl

Output:
- CAMCAN_centroids_{clustername}_{hemi}.pkl
- CAMCAN_centroids_{clustername}_{hemi}_vertex.pkl - for fcgradient colocalization

"""
# -------------------------------------------------------------------------------------------------------------------


for hemi in ["lh", "rh"]:

    #----- Load files
    inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{fs_dir}/fsaverage/surf/{hemi}.inflated")

    filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)
    with open(f"{base_dir}/labels_{filename}.pkl", "rb") as f:
        labels = pickle.load(f)

    with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}.pkl"), "rb") as f:
        CAMCAN_individual_peaks_df = pickle.load(f)

    for cluster in cluster_ids[hemi]:
        print(cluster)

        #---- FILTER to include only points in cluster
        mask = np.isin(labels, cluster)
        df_filtered = CAMCAN_individual_peaks_df[mask]

        #----- Compute center of mass of center of masses:
        # Loop through freqs. For each freq: (1) Extract relevant rows
        # (2) Join them to produce a new array
        # (3) Compute the centroid

        COM_list = [] # List for output
        COM_list_vertex = [] # Same, but in vertex format instead of xyz format
        # Loop through freqs
        for f in freqs:
            print(f)
            # Just points for this freq:
            df_filtered_f = df_filtered.loc[df_filtered['freq'] == f]
            # stc_data for this freq:
            stc_data = np.zeros(shape = (inflated_surface_rr.shape[0], 1))
            # For each point: (row is subject, freq, x, y, z)
            for col_i, (index, row) in enumerate(df_filtered_f.iterrows()):
            # Pull out coordinate and convert to vertex
                coord = row[2:].to_numpy()
                vertex = np.where((inflated_surface_rr == coord).all(axis=1))[0][0]
                # Create an array with 0s everywhere, except for a 1 at given vertex, or more than 1 if two subjects are there
                stc_data[vertex, 0] = stc_data[vertex, 0] + 1
            if np.any(stc_data!=0):
                # Convert to stc
                stc_data_bothhemi = np.vstack((stc_data, stc_data))
                stc = mne.SourceEstimate(
                    data = stc_data_bothhemi,
                    vertices=[np.arange(0, inflated_surface_rr.shape[0]), np.arange(0, inflated_surface_rr.shape[0])],
                    tmin=0,
                    tstep=1)
                # Compute centroid
                if hemi == "lh":
                    hemi_param = 0
                else:
                    hemi_param = 1
                COM_vertex, _, _ = stc.center_of_mass(hemi=hemi_param, subject = "fsaverage", subjects_dir = fs_dir)
                COM_coord = inflated_surface_rr[COM_vertex]
                COM_list.append(np.insert(COM_coord, 0, f))
                COM_list_vertex.append(np.array([f, COM_vertex]))
                print(f, COM_vertex)
            else:
                COM_list.append(np.array([f, np.nan, np.nan, np.nan]))
                COM_list_vertex.append(np.array([f, np.nan]))

        if cluster == 0:
            clustername = "small"
        else:
            clustername = "large"

        with open(os.path.join(base_dir, f"CAMCAN_centroids_{clustername}_{hemi}.pkl") , "wb") as file:
            pickle.dump(COM_list, file)
        with open(os.path.join(base_dir, f"CAMCAN_centroids_{clustername}_{hemi}_vertex.pkl") , "wb") as file:
            pickle.dump(COM_list_vertex, file)

# -------------------------------------------------------------------------------------------------------------------
"""
STEP 4: DISTANCES
Computes the average distance of each individual (ie of all their peaks) from the corresponding group mean,
once for large cluster and once for small cluster, for each hemi

Input:
- CAMCAN_centroids_{clustername}_{hemi}.pkl
- CAMCAN_individual_peaks_{hemi}.pkl

Output:
- CAMCAN_individual_distances_from_centroid_cluster_{clustername}_{hemi}

This output will be used to compute regressions using demographics_cognitive_regression.R

"""
# -------------------------------------------------------------------------------------------------------------------

cluster_ids = {"lh": (2, 0), "rh": (1, 0)}

for hemi in ["lh", "rh"]:
    for cluster_index in cluster_ids[hemi]:
        if cluster_index == 0:
            clustername = "small"
        else:
            clustername = "large"

        # LOAD DATA
        with open(os.path.join(base_dir, f"CAMCAN_centroids_{clustername}_{hemi}.pkl"), "rb") as f:
            mean = pickle.load(f)
        mean = pd.DataFrame(mean, columns=["freq", "x", "y", "z"])
        freqs_used = np.unique(mean["freq"])

        with open(os.path.join(base_dir, f"CAMCAN_individual_peaks_{hemi}.pkl"), "rb") as f:
            individuals = pickle.load(f)
        individuals = individuals[individuals["freq"].isin(freqs_used)]

        # FOR EACH INDIVIDUAL, INCLUDE ONLY PEAKS ASSIGNED TO CLUSTER
        filename = f"{hemi}_8-30Hz_bestparams_" + str(best_minpts) + "_" + str(best_eps1) + "_" + str(best_eps2)
        with open(f"{base_dir}/labels_{filename}.pkl", "rb") as f:
            labs = pickle.load(f)
        individuals = individuals[labs == cluster_index]

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

        distances.to_feather(f"{base_dir}/CAMCAN_individual_distances_from_centroid_cluster_{clustername}_{hemi}.rds")

# -------------------------------------------------------------------------------------------------------------------
"""
STEP 5: COLOCALIZATION WITH SECOND PC OF FC GRADIENT

Input:
- CAMCAN_centroids_{clustername}_{hemi}_vertex.pkl

Output:
- stats and plots, saved to /plots

"""
# -------------------------------------------------------------------------------------------------------------------
from neuromaps.datasets import fetch_annotation
from neuromaps.transforms import fslr_to_fsaverage
import nibabel as nib
import diptest

#---- Prepare fcgradient data
params = dict(source='margulies2016', desc='fcgradient02', space='fsLR', den='32k')

lh_path, rh_path = fetch_annotation(**params)

if params['space'] == 'fsLR':
    lh_img, rh_img = fslr_to_fsaverage((lh_path, rh_path), target_density='164k', hemi=['L', 'R'])
    lh_data = lh_img.agg_data()
    rh_data = rh_img.agg_data()
else:
    lh_data = nib.load(lh_path).agg_data()
    rh_data = nib.load(rh_path).agg_data()

lh_vertno = np.arange(lh_data.shape[0])
rh_vertno = np.arange(rh_data.shape[0])
data = np.concatenate([lh_data, rh_data])[:, None]

stc = mne.SourceEstimate(
    data,
    vertices=[lh_vertno, rh_vertno],
    tmin=0,
    tstep=1,
    subject='fsaverage',)

#----- Useful function
# Given a list of vertices, finds values under them on the stc
# can take vertex numbers directly if left hemi, but if right need to start at len_vertices
def get_values_at_vertices(stc, vertex_list, hemi):
    n_lh = len(stc.vertices[0])
    offset = 0 if hemi == 'lh' else n_lh
    row_idx = np.array(vertex_list) + offset
    return stc.data[[int(r) for r in row_idx]]

stats = {}
for hemi in ["lh", "rh"]:

    #----- Load centroids
    with open(os.path.join(base_dir, f"CAMCAN_centroids_large_{hemi}_vertex.pkl") , "rb") as file:
        centroids = pickle.load(file)
    centroids_df = pd.DataFrame(centroids, columns=["freqs", "vertex"])

    #----- Statistics and plotting
    values = get_values_at_vertices(stc, centroids_df["vertex"].to_numpy(), hemi=hemi)
    dip, pval = diptest.diptest(values[:, 0], boot_pval=True, seed=0)
    stats[hemi] = {"dip": dip, "pval": pval}

    fig, ax = plt.subplots(dpi=900)
    ax.plot(centroids_df["freqs"], values[:, 0])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Loading")
    fig.savefig(f"{base_dir}/plots/Fig2d_{hemi}.png")

with open(f"{base_dir}/plots/FCgradient_colocalization_summary.txt", "w") as f:
    for hemi, diptest_stats in stats.items():
        f.write(f"{hemi}: {diptest_stats}\n")


# -------------------------------------------------------------------------------------------------------------------
""" ----------------------------------------------------------------------------------------------------------------
OMEGA ANALYSES
Pipeline for analyses related to the OMEGA data


Overview:
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 computes actual and permuted distance of step 1 outputs from the centroids of the CAM-CAN data
- STEP 3 computes summary statistics for step 2

"""
# -------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------
"""
STEP 1: COMPUTE INDIVIDUAL-LEVEL FREQUENCY-WISE OSCILLATORY PEAKS

For each subject, compute the spatial location of the peak power for each frequency - i.e., "subject trajectory"
Note that this section is the same as the "compute individual peaks" section in main_analyses.py
Does this separately for each segment (full scan or first 15 seconds)

Input:
- OMEGA_{segment}_subject_list.txt
- Imaging_data/OMEGA_whitened_stc_{segment} folder of {subject}_*_psd_beamformer_fsaverage_whitened-{hemi}.stc

Output:
- OMEGA_individual_peaks_{segment}_{hemi}.pkl - for each subject and frequency, the coordinates of the peak power in that frequency

"""
# -------------------------------------------------------------------------------------------------------------------

for segment in ["full", "first15"]:

    # Load subjects
    with open(f"{base_dir}/OMEGA_{segment}_subject_list.txt") as f:
        subjects = f.read().split()

    for hemi in ["lh", "rh"]:
        inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{fs_dir}/fsaverage/surf/{hemi}.inflated")

        # Empty dataframe
        individual_peaks_coord_df = pd.DataFrame(columns=["subject", "freq", "x", "y", "z"])

        for subject in subjects:

            file = glob.glob(f"{base_dir}/Imaging_data/OMEGA_whitened_stc_{segment}/{subject}_*_psd_beamformer_fsaverage_whitened*")[0]
            stc = mne.read_source_estimate(file)

            for f in freqs:
                t_stc = stc_one_timepoint(stc, f, hemi)

                if hemi=="lh":
                    relevant_data = t_stc.lh_data
                else:
                    relevant_data = t_stc.rh_data

                # If all vertices are 0, set peak to an array of nans
                if np.all(relevant_data==0):
                    individual_peaks_coord_df.loc[len(individual_peaks_coord_df)] = [subject, f, None, None, None]
                else:
                    COM_vertex, _ = t_stc.get_peak(hemi=hemi)
                    COM_coord = inflated_surface_rr[COM_vertex] # this gives you an array
                    individual_peaks_coord_df.loc[len(individual_peaks_coord_df)] = [subject, f, COM_coord[0], COM_coord[1], COM_coord[2]]
                    # Occasionally (e.g. for plotting) you may want to gather spatial locations as vertices instead of xyz coordinates This is the code for that:
                    # individual_peaks_coord_df.loc[len(individual_peaks_coord_df)] = [subject, f, COM_vertex]

        # Write to file
        with open(f"{base_dir}/OMEGA_individual_peaks_{segment}_{hemi}.pkl", "wb") as f:
            pickle.dump(individual_peaks_coord_df, f)


# -------------------------------------------------------------------------------------------------------------------
"""
STEP 2: COMPUTE DISTANCE AND NULL-DISTRIBUTION OF DISTANCE

Compute the spatial distance of the OMEGA individual-level frequency-wise oscillatory peaks from the centroids of the CAM-CAN data (i.e., from the frequency-wise group averages of peaks in cluster 1).
Additionally, compute the spatial distance of the OMEGA individual-level frequency-wise oscillatory peaks from the *permuted* centroids of the CAM-CAN data.

Input:
- CAMCAN_centroids_large_{hemi}.pkl
- OMEGA_individual_peaks_{segment}_{hemi}.pkl

Output:
- actual_{segment}_{hemi}.txt - the average, over all participants, of the distance, over all frequencies, from spatial oscillatory peaks (OMEGA) to the centroids (CAM-CAN)
- null_5000perms_{binlength}_{segment}_{hemi}.txt - distances similar to the above, but this time the distance is computed after randomly permuting the CAM-CAN centroids

Outputs are saved to the folder omega-camcan_distance_cluster1

"""
# -------------------------------------------------------------------------------------------------------------------

np.random.seed(0)

# Loop over stuff
for binlength in [1, 2, 4, 8, 11]:
    for segment in ["full", "first15"]:
        for hemi in ["rh", "lh"]:

            ##### READ FILES

            # LOAD DATA: CAM-CAN CENTROIDS
            camcan_COM_path = f"{base_dir}/CAMCAN_centroids_large_{hemi}.pkl"
            with open(camcan_COM_path, "rb") as f:
                mean = pickle.load(f)
            mean = pd.DataFrame(mean, columns=["freq", "x", "y", "z"])

            # LOAD DATA: OMEGA INDIVIDUAL PEAKS
            omega_individual_COM_path = f"{base_dir}/OMEGA_individual_peaks_{segment}_{hemi}.pkl"
            with open(omega_individual_COM_path, "rb") as f:
                individuals = pickle.load(f)

            print("done reading files")

            ##### COMPUTE ACTUAL DISTANCE
            # Compute the *actual* distance from the OMEGA to the CAM-CAN data - i.e., the non-permuted distance
            # Distance = sqrt((x-x)^2 + (y-y)^2 + (z-z)^2)
            # FAQ: Why is this code here, where it runs again with every loop? Answer: For clarity/simplicity, and because it runs quickly anyways.
            actual_distances = pd.DataFrame(columns = ["subject", "freq", "distance"])
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
                actual_distances.loc[len(actual_distances)] = [subject, freq, distance]

            with open(f"{base_dir}/omega-camcan_distance_cluster1/actual_{segment}_{hemi}.txt", "w") as file:
                file.write(str(actual_distances["distance"].mean()))

            print("done computing actual mean distance")

            ##### PERMUTATIONS
            # Permute the centroids for the CAM-CAN data by frequency, then recompute the distance

            null_distribution = []
            for i in range(5000):

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
                    subject = row["subject"]
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

            with open(f'{base_dir}/omega-camcan_distance_cluster1/null_5000perms_{binlength}_{segment}_{hemi}.txt', 'w') as f:
                for item in null_distribution:
                    f.write(f"{item}\n")

            print(f"Done permutations and distance computation for {binlength}_{segment}_{hemi}")

# -------------------------------------------------------------------------------------------------------------------
"""
STEP 3: COMPUTE SUMMARY STATISTICS

Input:
- The outputs of step 2 above (actual...txt and null...txt)

Output:
- Plots and tables, saved to /plots

Note that, throughout this code, all distance values (i.e., all values read in from file in this section) are subtracted from 100 (the length of an fsaverage axis) - i.e., flipped. This is in order to turn them from a measure of "distance from gradient" into a measure "gradient expression."

"""

# -------------------------------------------------------------------------------------------------------------------

distance_data_dir = f"{base_dir}/omega-camcan_distance_cluster1/"

##### PLOT HISTOGRAM (FIGURE 3B)

# In the manuscript, just plot the null distributions for bin size 1 (0.25 Hz) (left and right hemi)
for hemi in ["lh", "rh"]:
    name = f"null_5000perms_1_full_{hemi}"

    # Read data file
    with open(f"{distance_data_dir}/{name}.txt", "r", encoding="utf-8") as file:
        floats = [float(line.strip()) for line in file]
    floats = np.subtract(100, floats)

    # Plot
    fig, ax = plt.subplots()
    ax.hist(floats, bins = 100, color = "#A3A3A3")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(20, 40)
    ax.set_yticks([])
    ax.set_yticklabels([])

    # Get statistics, and put it on the plot for convenience
    with open(f"{distance_data_dir}/actual_full_{hemi}.txt", "r", encoding="utf-8") as file:
        actual = 100 - [float(line.strip()) for line in file][0] # Subtract value from 100 to flip
    range_str = f"min: {str(round(min(floats), 2))}, max: {str(round(max(floats), 2))}"
    pval = len([x for x in floats if x >= actual])/len(floats)
    ax.set_title(f"{name} \n range: {range_str} \n actual: {str(round(actual, 2))} \n p-val: {str(pval)}")

    # Save plot
    fig.savefig(f"{base_dir}/plots/Fig3B_histogram_{name}.png", bbox_inches="tight")


##### COMPUTE STATISTICS (TABLE S1)

segment_hemi = ['full_lh', 'full_rh', 'first15_lh', 'first15_rh']

# Write all output to file
with open(f'{base_dir}/plots/TableS1.txt', 'w') as file:
    print(*segment_hemi, file=file)
    actuals = []
    for sh in segment_hemi:
        actual = 100 - np.loadtxt(f'{distance_data_dir}/actual_{sh}.txt')
        actuals.append(round(actual, 2))
    print("Empirical:", file=file)
    print(*actuals, sep='\t', file=file)
    print("Permuted:", file=file)
    for b in [1, 2, 4, 8, 11]:
        row = [f'{b * 0.25} Hz']
        for sh in segment_hemi:
            null = 100 - np.loadtxt(f'{distance_data_dir}/null_5000perms_{b}_{sh}.txt')
            actual = 100 - np.loadtxt(f'{distance_data_dir}/actual_{sh}.txt')
            p = np.sum((null >= actual)) / (len(null))
            row.append(f'[{null.min():.2f}, {null.max():.2f}] p={p:.4f}')
        print(*row, sep='\t', file=file)

# %%

