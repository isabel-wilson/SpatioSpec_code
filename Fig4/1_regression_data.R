# Load packages
library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)
library(report)
library(tidyverse)
library(glue)
library(reticulate)

# User input
base_dir = "C:/meg/params/03_lh_rh_rerun"


setwd(paste0(base_dir, "/camcan_behav_demo/prepped_data"))

##### AVERAGE DISTANCE

compute_avg_distances <- function(file_paths, col_names, freq_threshold) {
  
  process_file <- function(file_path, col_name) {
    distances <- read_feather(file_path)
    distances$subject <- paste0("sub-CC", distances$subject)
    distances <- distances %>% filter(freq >= freq_threshold)
    
    distances %>%
      group_by(subject) %>%
      summarise(
        !!paste0("avdist_normed_", col_name) := mean(distance_normed),
        !!paste0("avdist_unnormed_", col_name) := mean(distance),
        .groups = "drop")
  }
  
  Map(process_file, file_paths, col_names) %>%
    reduce(full_join, by = "subject")
}

df_merged <- compute_avg_distances(
  file_paths = c(paste0(base_dir, "/individual_distances_from_centroid_normalized_lh.rds"), 
                  paste0(base_dir, "/individual_distances_from_centroid_normalized_rh.rds")),
  col_names = c(glue("lh"), glue("rh")),
  freq_threshold = as.integer(8)
)


##### Points in cluster only
# Produce files: average_distance_counts_cluster_
# and add to dataframe
for (hemi in c("lh", "rh")) {
  for (cluster in c("large", "small")) {
    print(hemi)
    print(cluster)
    system(glue("python3 {base_dir}/python_scripts/make_average_distance_counts_cluster.py {hemi} {cluster}"))
    df_temp <- read_feather(glue("{base_dir}/average_distance_counts_cluster_{cluster}_{hemi}_8-30.rds"))
    df_temp$subject <- paste0("sub-CC", df_temp$subject)
    df_merged <- merge(df_merged, df_temp, by="subject")
  }
}


##### DEMOGRAPHICS AND DETAILED ACER

scores <- read.csv(glue("{base_dir}/camcan_behav_demo/clean_scores.csv"))
colnames(scores)[colnames(scores)=="ID"] <- "subject"
scores$sex_binary <- ifelse(scores$sex == "MALE", 1, 0)

avdist_scores <- merge(df_merged, scores, by="subject")

app <- read.csv(glue("{base_dir}/camcan_behav_demo/approved_data.csv"), sep="\t")
colnames(app)[colnames(app)=="CCID"] <- "subject"
app$subject <- paste0("sub-", app$subject)

avdist_app_scores <- merge(avdist_scores, app, by="subject")
write.table(avdist_app_scores, glue("avdist_demo_acer_8-30.txt"))
View(avdist_app_scores)
