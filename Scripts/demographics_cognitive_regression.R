# ------------------------------------------------------------------------------
# Script for associations with demographic/cognitive variables. 
# Run this after main_analyses.py, because you need the individual_distances
# output. 
# ------------------------------------------------------------------------------
rm(list = ls())
library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)
library(glue)

base_dir = "C:/meg/params/0_SpatioSpec_results/SpatioSpec_code/Data/"  # USER INPUT
demo_dir = paste0(base_dir, "Demographics/")


#----- SET UP FOR DATAFRAME ----------------------------------------------------

# Demographics and ACER
scores <- read.csv(glue("{demo_dir}/clean_scores.csv"))
colnames(scores)[colnames(scores)=="ID"] <- "subject"

app <- read.csv(glue("{demo_dir}/approved_data.csv"), sep="\t")
colnames(app)[colnames(app)=="CCID"] <- "subject"
app$subject <- paste0("sub-", app$subject)

demo_acer <- merge(app, scores, by="subject")

# Distances
# For one cluster and hemi, get each subject's average distance across frequencies
compute_avg_distances <- function(clustername, hemi) {
  distances <- read_feather(glue("{base_dir}/CAMCAN_individual_distances_from_centroid_cluster_{clustername}_{hemi}.rds"))
  distances$subject <- paste0("sub-CC", distances$subject)
  avg <- distances %>%
    filter(freq >= 8) %>%
    group_by(subject) %>%
    summarise(avdist = mean(distance))
  colnames(avg)[colnames(avg)=="avdist"] <- paste0("avdist_", hemi)
  return(avg)
}

#-------------------------------------------------------------------------------
#------ CLUSTER: LARGE ---------------------------------------------------------

clustername = "large"

# These input files are the distance of the individual peaks *in the large cluster* from the centroid of the large cluster
lh <- compute_avg_distances(clustername, "lh")
rh <- compute_avg_distances(clustername, "rh")
df_distances <- merge(lh, rh, by = "subject")

# Average over both hemis
# Reverse to obtain a measure of expression
df_distances <- df_distances %>%
  mutate(avdist_avg = (avdist_lh + avdist_rh) / 2) %>%
  mutate(expression = 100 - avdist_avg)

# Merge and save
df <- merge(df_distances, demo_acer, by="subject")
write.table(df, glue("{base_dir}/CAMCAN_avdist_demo_acer.txt"))


#----- STATS: EXPRESSION ~ AGE -------------------------------------------------
output <- lm(expression ~ age, data = df)
summary(output)

# Plot
ggplot(data = df, aes(x = age, y = expression)) + 
  geom_point(color = "#fc7d7d", size = 2) + 
  geom_smooth(method = "lm", linewidth = 2, color = "black") +
  theme_classic() + 
  labs(
    y = "gradient expression",
    x = "age"
  ) + 
  theme(
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    aspect.ratio = 1)

# Save
capture.output(summary(output), file = glue("{base_dir}/plots/Fig4A_regression_stats.txt"))
ggsave(glue("{base_dir}/plots/Fig4A.png"), width = 5, height = 5, dpi = 300)


#----- STATS: EXPRESSION RES ~ ACER RES --------------------------------------
df <- df[df$additional_acer != 0, ]

model <- lm(additional_acer ~ age, data = df)
res_acer <- resid(model)

model <- lm(expression ~ age, data = df)
res_expression <- resid(model)

output <- lm(res_expression ~ res_acer, data = df)
summary(output)

# Plot
ggplot(data = df, aes(x = res_acer, y = res_expression)) + 
  geom_point(color = "#fc7d7d", size = 2) + 
  geom_smooth(method = "lm", linewidth = 2, color = "black") +
  theme_classic() + 
  labs(
    y = "gradient expression (age-regressed)",
    x = "acer (age-regressed)"
  ) + 
  theme(
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    aspect.ratio = 1) 

# Save
capture.output(summary(output), file = glue("{base_dir}/plots/Fig4B_regression_stats.txt"))
ggsave(glue("{base_dir}/plots/Fig4B.png"), width = 5, height = 5, dpi = 300)



#-------------------------------------------------------------------------------
#------ CLUSTER: SMALL ---------------------------------------------------------

clustername = "small"

# These input files are the distance of the individual peaks *in the small cluster* from the centroid of the small cluster
lh <- compute_avg_distances(clustername, "lh")
rh <- compute_avg_distances(clustername, "rh")
df_distances <- merge(lh, rh, by = "subject")

# Average over both hemis
# Reverse to obtain a measure of expression
df_distances <- df_distances %>%
  mutate(avdist_avg = (avdist_lh + avdist_rh) / 2) %>%
  mutate(expression = 100 - avdist_avg)

# Merge. Don't save, because not as important as cluster_large stats
df <- merge(df_distances, demo_acer, by="subject")


#----- STATS: EXPRESSION ~ AGE -------------------------------------------------
output <- lm(expression ~ age, data = df)
summary(output)
capture.output(summary(output), file = glue("{base_dir}/plots/small_cluster_regression_stats.txt"))