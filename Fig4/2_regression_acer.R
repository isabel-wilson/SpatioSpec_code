library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)

setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
cluster <- "small"
df <- read.table("avdist_demo_acer_8-30.txt")
df <- df[df$additional_visuospatial != 0, ]
lh_col <- paste0("avdist_unnormed_in_cluster_", cluster, "_lh")
rh_col <- paste0("avdist_unnormed_in_cluster_", cluster, "_rh")
df <- df[!is.na(df[[lh_col]]) & !is.na(df[[rh_col]]), ]
df[["avdist_unnormed_in_cluster_both_hemi"]] <- (df[[lh_col]] + df[[rh_col]]) / 2

df$avdist_unnormed_in_cluster_both_hemi_flipped <- 100 - df$avdist_unnormed_in_cluster_both_hemi

model <- lm(additional_acer ~ age, data = df)
res_acer <- resid(model)

model <- lm(avdist_unnormed_in_cluster_both_hemi_flipped ~ age, data = df)
res_avdist <- resid(model)

output <- lm(avdist_unnormed_in_cluster_both_hemi_flipped ~ age, data = df)
summary(output)

ggplot(data = df, aes(x = res_acer, y = res_avdist)) + 
  geom_point(color = "#fc7d7d", size = 2) + 
  geom_smooth(method = "lm", linewidth = 2, color = "black") +
  theme_classic() + 
  labs(
    y = "",
    x = ""
  ) + 
  theme(
    axis.title = element_text(size = 22),
    axis.text = element_text(size = 22),
    aspect.ratio = 1
  ) 

ggsave("C:/meg/SpatioSpec_results/plot2.png", width = 5, height = 5, dpi = 300)

