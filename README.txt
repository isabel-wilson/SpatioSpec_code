Code and data for the "SpatioSpec" project. 

-------------------------------------------------------------------------------------------------------------------
CONCEPTUAL OVERVIEW: 

SECTION 1: CAMCAN ANALYSES
(main_analyses.py)
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 runs ST-DBSCAN
- STEP 3 computes the centroids of large and small clusters
- STEP 4 computes the "distance" of individual participants' clusters from these centroids
- STEP 5 tests colocalization with the FC gradient

SECTION 2: OMEGA ANALYSES
(main_analyses.py)
- STEP 1 computes participant-level frequency-wise oscillatory peaks
- STEP 2 computes actual and permuted distance of step 1 outputs from the centroids of the CAM-CAN data
- STEP 3 computes summary statistics for step 2

SECTION 3: RELATIONSHIPS WITH AGE/COGNITION
(demographic_cognitive_regression.R)

-------------------------------------------------------------------------------------------------------------------
HOW TO RUN THE CODE: 

After organizing your file system as required (see DIRECTORY ORGANIZATION), run scripts in order:
1. main_analyses.py
2. demographics_cognitive_regression.py

There are also "supplementary" code files you may like to look at. These are: 
- choose_st-dbscan_parameters.py - was used to choose parameters for clustering
- demographic_stats.py - was used to compute demographic information for methods section of manuscript

-------------------------------------------------------------------------------------------------------------------
DIRECTORY ORGANIZATION:

base_dir = .../SpatioSpec_code/Data/ # Set your base_dir variable to this

INPUTS: Before running scripts, please organize your files like this:

SpatioSpec_code
|-- Data
|   |-- CAMCAN_subject_list.txt
|   |-- Demographics
|   |   |-- OmegaQuestionnaireResponses.tsv # downloaded directly from OMEGA public repo
|   |   |-- QC_notes.tsv # from OMEGA MEG preprocessing
|   |   |-- approved_data.csv # downloaded directly from CAMCAN public repo
|   |   |-- clean_scores.csv # downloaded directly from CAMCAN public repo
|   |   |-- entireSampleDemographics.csv # downloaded directly from CAMCAN public repo
|   |   `-- sessions.tsv # from OMEGA MEG preprocessing
|   |-- Imaging_data
|   |   |-- CAMCAN_whitened_stc # Folder of beamformed stcs; more detail below
|   |   |-- OMEGA_whitened_stc_first15
|   |   `-- OMEGA_whitened_stc_full
|   |-- OMEGA_first15_subject_list.txt
|   |-- OMEGA_full_subject_list.txt
|   |-- fs_subjects
|   |   `-- fsaverage
|   `-- st_dbscan.py # This script is credited to Eren Cakmak <eren.cakmak@uni-konstanz.de> and Manuel Plank <manuel.plank@uni-konstanz.de>
`-- Scripts # This is the folder that is available on github
    |-- choose_st-dbscan_parameters.py
    |-- demographic_stats.R
    |-- demographics_cognitive_regression.R
    `-- main_analyses.py

More information about beamformed stcs: Source-imaged, whitened PSD for each subject in fsaverage space. The data attribute is an array of vertices x frequency (157 frequencies, from 1-40 Hz in 0.25 Hz steps). Each value is the difference between the power and aperiodic fit; it can be negative when the aperiodic fit is higher than the power. stc.tmin = 1 (representing the lowest frequency) and stc.tstep=0.25 (representing the frequency resolution). Saved as {subject}_psd_beamformer_fsaverage_whitened-lh.stc and {subject}_psd_beamformer_fsaverage_whitened-rh.stc.


OUTPUTS: After running scripts, this is what your file system will look like:

SpatioSpec_code
|-- Data
|   |-- CAMCAN_avdist_demo_acer.txt
|   |-- CAMCAN_centroids_large_lh.pkl
|   |-- CAMCAN_centroids_large_lh_vertex.pkl
|   |-- CAMCAN_centroids_large_rh.pkl
|   |-- CAMCAN_centroids_large_rh_vertex.pkl
|   |-- CAMCAN_centroids_small_lh.pkl
|   |-- CAMCAN_centroids_small_lh_vertex.pkl
|   |-- CAMCAN_centroids_small_rh.pkl
|   |-- CAMCAN_centroids_small_rh_vertex.pkl
|   |-- CAMCAN_individual_distances_from_centroid_cluster_large_lh.rds
|   |-- CAMCAN_individual_distances_from_centroid_cluster_large_rh.rds
|   |-- CAMCAN_individual_distances_from_centroid_cluster_small_lh.rds
|   |-- CAMCAN_individual_distances_from_centroid_cluster_small_rh.rds
|   |-- CAMCAN_individual_peaks_lh.pkl
|   |-- CAMCAN_individual_peaks_lh_normalized.pkl
|   |-- CAMCAN_individual_peaks_lh_vertex.pkl
|   |-- CAMCAN_individual_peaks_rh.pkl
|   |-- CAMCAN_individual_peaks_rh_normalized.pkl
|   |-- CAMCAN_individual_peaks_rh_vertex.pkl
|   |-- CAMCAN_subject_list.txt
|   |-- Demographics
|   |   |-- OmegaQuestionnaireResponses.tsv
|   |   |-- QC_notes.tsv
|   |   |-- approved_data.csv
|   |   |-- clean_scores.csv
|   |   |-- entireSampleDemographics.csv
|   |   `-- sessions.tsv
|   |-- Imaging_data
|   |   |-- CAMCAN_whitened_stc
|   |   |-- OMEGA_whitened_stc_first15
|   |   `-- OMEGA_whitened_stc_full
|   |-- OMEGA_first15_subject_list.txt
|   |-- OMEGA_full_subject_list.txt
|   |-- OMEGA_individual_peaks_first15_lh.pkl
|   |-- OMEGA_individual_peaks_first15_rh.pkl
|   |-- OMEGA_individual_peaks_full_lh.pkl
|   |-- OMEGA_individual_peaks_full_rh.pkl
|   |-- fs_subjects
|   |   `-- fsaverage
|   |-- labels_lh_8-30Hz_bestparams_9_0.0319_0.5.pkl
|   |-- labels_rh_8-30Hz_bestparams_9_0.0319_0.5.pkl
|   |-- omega-camcan_distance_cluster1
|   |   |-- actual_first15_lh.txt
|   |   |-- actual_first15_rh.txt
|   |   |-- actual_full_lh.txt
|   |   |-- actual_full_rh.txt
|   |   |-- null_5000perms_11_first15_lh.txt
|   |   |-- null_5000perms_11_first15_rh.txt
|   |   |-- null_5000perms_11_full_lh.txt
|   |   |-- null_5000perms_11_full_rh.txt
|   |   |-- null_5000perms_1_first15_lh.txt
|   |   |-- null_5000perms_1_first15_rh.txt
|   |   |-- null_5000perms_1_full_lh.txt
|   |   |-- null_5000perms_1_full_rh.txt
|   |   |-- null_5000perms_2_first15_lh.txt
|   |   |-- null_5000perms_2_first15_rh.txt
|   |   |-- null_5000perms_2_full_lh.txt
|   |   |-- null_5000perms_2_full_rh.txt
|   |   |-- null_5000perms_4_first15_lh.txt
|   |   |-- null_5000perms_4_first15_rh.txt
|   |   |-- null_5000perms_4_full_lh.txt
|   |   |-- null_5000perms_4_full_rh.txt
|   |   |-- null_5000perms_8_first15_lh.txt
|   |   |-- null_5000perms_8_first15_rh.txt
|   |   |-- null_5000perms_8_full_lh.txt
|   |   `-- null_5000perms_8_full_rh.txt
|   |-- plots
|   |   |-- FCgradient_colocalization_summary.txt
|   |   |-- Fig2B_lh_8-30Hz_bestparams_9_0.0319_0.5_clusters.png
|   |   |-- Fig2B_lh_8-30Hz_bestparams_9_0.0319_0.5_large.png
|   |   |-- Fig2B_rh_8-30Hz_bestparams_9_0.0319_0.5_clusters.png
|   |   |-- Fig2B_rh_8-30Hz_bestparams_9_0.0319_0.5_large.png
|   |   |-- Fig2d_lh.png
|   |   |-- Fig2d_rh.png
|   |   |-- Fig3B_histogram_null_5000perms_1_full_lh.png
|   |   |-- Fig3B_histogram_null_5000perms_1_full_rh.png
|   |   |-- Fig4A.png
|   |   |-- Fig4A_regression_stats.txt
|   |   |-- Fig4B.png
|   |   |-- Fig4B_regression_stats.txt
|   |   |-- TableS1.txt
|   |   |-- cluster_summary.txt
|   |   `-- small_cluster_regression_stats.txt
|   `-- st_dbscan.py
`-- Scripts
    |-- choose_st-dbscan_parameters.py
    |-- demographic_stats.R
    |-- demographics_cognitive_regression.R
    `-- main_analyses.py

