library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)

setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
df <- read.table("avdist_demo_acer_10-30.txt")
df <- df[df$additional_visuospatial != 0, ]

variables <- c("number_in_cluster", "avdist_in_cluster") 
for (variable in variables) {
  df[[paste0(variable, "_both_hemi")]] <- (df[[paste0(variable, "_lh")]] + df[[paste0(variable, "_rh")]])/2
}
View(df)

model <- lm(avdist_normed_lh ~ age, data = df)
avdist_normed_lh_res <- resid(model)

model <- lm(avdist_normed_rh ~ age, data = df)
avdist_normed_rh_res <- resid(model)

model <- lm(number_in_cluster_lh ~ age, data = df)
number_in_cluster_lh_res <- resid(model)

model <- lm(number_in_cluster_rh ~ age, data = df)
number_in_cluster_rh_res <- resid(model)

model <- lm(additional_attention_orientation ~ age, data = df)
attention_orientation_res <- resid(model)

model <- lm(additional_memory ~ age, data = df)
memory_res <- resid(model)

model <- lm(additional_fluencies ~ age, data = df)
fluencies_res <- resid(model)

model <- lm(additional_language ~ age, data = df)
language_res <- resid(model)

model <- lm(additional_visuospatial ~ age, data = df)
visuospatial_res <- resid(model)

model <- lm(additional_acer ~ age, data = df)
acer_res <- resid(model)

X <- cbind(as.data.frame(avdist_normed_lh_res), 
           as.data.frame(avdist_normed_rh_res),
           as.data.frame(number_in_cluster_lh_res),
           as.data.frame(number_in_cluster_rh_res),
           as.data.frame(attention_orientation_res),
           as.data.frame(memory_res),
           as.data.frame(fluencies_res),
           as.data.frame(language_res),
           as.data.frame(visuospatial_res),
           as.data.frame(acer_res))

write.csv(X, "pls_matlab_input_res.csv", col.names = FALSE)

