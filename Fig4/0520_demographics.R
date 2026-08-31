# Load packages
library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)
library(report)
library(caret)

# Load data
acer <- read.csv("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/clean_scores.csv")
demo <- read.csv("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/entireSampleDemographics.csv")
colnames(acer)[colnames(acer)=="ID"] <- "subject"
brain <- read_feather("C:/meg/params/03_lh_rh_rerun/individual_distances_from_centroid_normalized_lh.rds")
brain$subject <- paste0("sub-CC", brain$subject)
View(acer)
View(demo)
View(brain)

brain_summary <- brain %>% group_by(subject) %>% count()
nrow(brain_summary) # 604

brains_with_demo <- merge(brain_summary, demo, by.x = "subject")
nrow(brains_with_demo) # 604

brains_with_acer <- merge(brain_summary, acer, by.x = "subject")
nrow(brains_with_acer) # 604

# Full cam-can brain sample
max(brains_with_demo$age)
max(brains_with_demo$age)
min(brains_with_demo$age)
round(mean(brains_with_demo$age))
round(sd(brains_with_demo$age))
nrow(brains_with_demo %>% filter(sex == "MALE"))

# Cam-can cognitive sample
max(brains_with_acer$age)
max(brains_with_acer$age)
min(brains_with_acer$age)
round(mean(brains_with_acer$age))
round(sd(brains_with_acer$age))
nrow(brains_with_acer %>% filter(sex == "MALE"))