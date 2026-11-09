Code for the "SpatioSpec" paper. 

-------------------------------------------------------------------------------------------------------------------
HOW TO REPRODUCE THIS PAPER

Upon request, we will send you all the input files you need, pre-organized in the "INPUT" format described below. 

To reproduce this paper, you should run the following two scripts, in the following order: 
1. main_analyses.py
2. demographics_cognitive_regression.py

You will need these packages: numpy pandas matplotlib mne neuromaps nibabel diptest pyarrow scipy scikit-learn. Outputs will appear in the "OUTPUT" format (described below). If you would not like to generate them yourself, these outputs are, too, available upon request. 

There are also "supplementary" code files that are not essential for reproducing the analyses, but that you may like to run to better understand the project. These are: 
- choose_st-dbscan_parameters.py - was used to choose parameters for clustering
- demographic_stats.py - was used to compute demographic information for methods section of manuscript

-------------------------------------------------------------------------------------------------------------------
ORGANIZATION OF INPUT FILES

SpatioSpec_code
|-- Data
|   |-- CAMCAN_subject_list.txt             # list of subjects used; available upon request
|   |-- Demographics
|   |   |-- OmegaQuestionnaireResponses.tsv # from OMEGA public repo
|   |   |-- QC_notes.tsv                    # from in-lab OMEGA MEG preprocessing; available upon request
|   |   |-- approved_data.csv               # from CAMCAN public repo
|   |   |-- clean_scores.csv                # from CAMCAN public repo
|   |   |-- entireSampleDemographics.csv    # from CAMCAN public repo
|   |   `-- sessions.tsv                    # from in-lab OMEGA MEG preprocessing; available upon request
|   |-- Imaging_data
|   |   |-- CAMCAN_whitened_stc             # input imaging data; available upon request
|   |   |-- OMEGA_whitened_stc_first15      # input imaging data; available upon request
|   |   `-- OMEGA_whitened_stc_full         # input imaging data; available upon request
|   |-- OMEGA_first15_subject_list.txt      # list of subjects used; available upon request
|   |-- OMEGA_full_subject_list.txt         # list of subjects used; available upon request
|   |-- fs_subjects
|   |   `-- fsaverage                       # from FreeSurfer
|   `-- st_dbscan.py                        # from https://github.com/eren-ck/st_dbscan (Eren Cakmak and Manuel Plank)
`-- Scripts                                 # available from https://github.com/isabel-wilson/SpatioSpec_code 
    |-- choose_st-dbscan_parameters.py
    |-- demographic_stats.R
    |-- demographics_cognitive_regression.R
    `-- main_analyses.py

base_dir = .../SpatioSpec_code/Data/

-------------------------------------------------------------------------------------------------------------------
ORGANIZATION OF OUTPUT FILES

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