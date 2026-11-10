Code for the "SpatioSpec" paper. Reproducible! Commented! Well-organized! Explained for reviewers!

-------------------------------------------------------------------------------------------------------------------
HOW TO REPRODUCE THIS PAPER

Upon request, we will send you input files pre-organized in the "INPUT" format described below. 

To reproduce this paper, you should click "run" on the following two scripts, in the following order: 
1. main_analyses.py
2. demographics_cognitive_regression.py

Outputs will appear in the "OUTPUT" format (described below). If you would not like to generate outputs yourself, these output files are, too, available upon request. 

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

-------------------------------------------------------------------------------------------------------------------
ORGANIZATION OF OUTPUT FILES

SpatioSpec_code
|-- Data
|   |-- CAMCAN_avdist_demo_acer.txt         # table organizing individual demographics, cognitive scores, and gradient expression
|   |-- CAMCAN_centroids_large_lh.pkl       # centroids of cluster. 8 files of this format (large, small; lh, rh; xyz coords, vertex)
|   |-- CAMCAN_individual_distances_from_centroid_cluster_large_lh.rds     # distance of in-cluster peaks from centroid of cluster. 4 files of this format (large, small; lh, rh)
|   |-- CAMCAN_individual_peaks_lh.pkl      # individual peaks. 8 files of this format (lh, rh; unnormalized, normalized; xyz coords, vertex)
|   |-- CAMCAN_subject_list.txt
|   |-- Demographics                        # folder; contents same as input
|   |-- Imaging_data                        # folder; contents same as input
|   |-- OMEGA_first15_subject_list.txt
|   |-- OMEGA_full_subject_list.txt
|   |-- OMEGA_individual_peaks_first15_lh.pkl   # individual peaks. 4 files of this format (first15, full; lh, rh)
|   |-- fs_subjects                         # folder; contents same as input
|   |-- labels_lh_8-30Hz_bestparams_9_0.0319_0.5.pkl     # cluster labels for st-dbscan (lh)
|   |-- labels_rh_8-30Hz_bestparams_9_0.0319_0.5.pkl     # cluster labels for st-dbscan (rh)
|   |-- omega-camcan_distance_cluster1
|   |   |-- actual_first15_lh.txt                 # distance of peaks from centroid. 4 files of this format (first15, full; lh, rh)
|   |   |-- null_5000perms_11_first15_lh.txt      # 5000 permutations of distance. 20 files of this format (bin lengths 1, 2, 4, 11; first15, full; lh, rh)
|   |-- plots                               # statistics and simple plots that can be used for checking the paper  
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
`-- Scripts                                 # folder; contents same as input

-------------------------------------------------------------------------------------------------------------------
FAQ (frequently-asked questions)

What do I need to change in the script? base_dir = .../SpatioSpec_code/Data/

-------------------------------------------------------------------------------------------------------------------
UAQ (unfrequently-asked questions)

How long did this take to set up? 18 nearly-consecutive hours
