#-------------------------------------------------------------------------------
# Script for computing demographic information (e.g., counts of participants in 
# study) to include in methods section of paper. Uses files downloaded directly
# from OMEGA/CAMCAN public repositories. 
#-------------------------------------------------------------------------------

# Load packages
library(feather)
library(tidyverse)

base_dir = "C:/meg/params/0_SpatioSpec_results/SpatioSpec_code/Data/"  # USER INPUT
demo_dir = paste0(base_dir, "Demographics/") # Folder of demographics/cognitive downloaded directly from public repositories

##### CAMCAN

# Load data
acer <- read.csv(paste0(demo_dir, "clean_scores.csv"))
demo <- read.csv(paste0(demo_dir, "entireSampleDemographics.csv"))
colnames(acer)[colnames(acer)=="ID"] <- "subject"
brain <- read_feather(list.files(base_dir, pattern = "^CAMCAN_individual_distances", full.names = TRUE)[1]) # Get an example file of processed data

brain_summary <- brain %>% group_by(subject) %>% count()
nrow(brain_summary) # 604

brains_with_demo <- merge(brain_summary, demo, by.x = "subject")
nrow(brains_with_demo) # 604

brains_with_acer <- merge(brain_summary, acer, by.x = "subject")
nrow(brains_with_acer) # 604

# Full CAMCAN brain sample
max(brains_with_demo$age)
min(brains_with_demo$age)
round(mean(brains_with_demo$age), 2)
round(sd(brains_with_demo$age), 2)
nrow(brains_with_demo %>% filter(sex == "MALE"))

# CAMCAN cognitive sample
max(brains_with_acer$age)
min(brains_with_acer$age)
round(mean(brains_with_acer$age), 2)
round(sd(brains_with_acer$age), 2)
nrow(brains_with_acer %>% filter(sex == "MALE"))


##### OMEGA

# Full OMEGA sample
omega <- read.csv(paste0(demo_dir, "sessions.tsv"), sep="\t")

# Participants marked "Control," "sub-0," coregistration=Yes
omega_filt1 <- omega %>%
  filter(coregistration == "Yes") %>%
  group_by(participant_id) %>%
  filter(str_detect(participant_id, "^sub-0")) %>%
  filter(group == "Control")
omega_filt1_size <- length(unique(omega_filt1$participant_id))
omega_filt1_size

# Participants not excluded during MEG preprocessing/quality-control
QC_notes <- read.csv(paste0(demo_dir, "QC_notes.tsv"), sep="\t")
omega_filt2 <- QC_notes %>%
  filter(Inclusion == 0)
omega_filt2_size <- length(unique(omega_filt2$Subject))
omega_filt2_size
omega_filt2_run_lengths <- table(omega_filt2$Length)
omega_filt2_run_lengths

# Demographics of final sample
demo <- read.csv(paste0(demo_dir, "OmegaQuestionnaireResponses.tsv"), sep="\t")
omega_filt2_demo <- merge(omega_filt2, omega, by.x = "Subject", by.y = "participant_id")
omega_filt2_demo <- merge(omega_filt2_demo, demo, by.x = "Subject", by.y = "participant_id")
# This age information is taken from the sessions.tsv file, not from the questionnaire file, because the questionnaire is missing ages. 
# Age is age at time of MEG scan
omega_filt2_demo$age <- as.numeric(omega_filt2_demo$age)
omega_filt2_age_info <- round(c(mean(omega_filt2_demo$age), sd(omega_filt2_demo$age), min(omega_filt2_demo$age), max(omega_filt2_demo$age)), 2)
omega_filt2_age_info
omega_filt2_males_count <- count(omega_filt2_demo %>% filter(Sex == "M"))
omega_filt2_males_count[1, 1]
omega_filt2_demo <- omega_filt2_demo %>% mutate(total = rowSums(across(starts_with("EHI_"))))
omega_filt2_demo$handedness_laterality_quotient <- (omega_filt2_demo$total)/4 - 100
mean(omega_filt2_demo$handedness_laterality_quotient, na.rm = TRUE)