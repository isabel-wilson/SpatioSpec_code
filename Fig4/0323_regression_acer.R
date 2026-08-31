# Load packages
library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)
library(report)
library(caret)
library(pls)
library(ropls)

# Load data
setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
df <- read.table("avdist_demo_acer_10-30.txt")

# Demographics: 
min(df$age)
max(df$age)
mean(df$age)
sd(df$age)
table(df$homeint_sex)

df <- df[df$additional_visuospatial != 0, ]
# Create _both_hemi cols
variables <- c("number_in_cluster", "avdist_in_cluster") #, "avdist_all", "avdist_unnormed", "avdist_normed", 
for (variable in variables) {
  df[[paste0(variable, "_both_hemi")]] <- (df[[paste0(variable, "_lh")]] + df[[paste0(variable, "_rh")]])/2
}

plot(df$number_in_cluster_both_hemi, df$avdist_in_cluster_both_hemi, xlim=c(0, 88), ylim=c(0, 1))
cor.test(df$number_in_cluster_both_hemi, df$avdist_in_cluster_both_hemi)

# Convert to matrix for opls
dataMatrix <- as.matrix(df)
rownames(dataMatrix) <- dataMatrix[, "subject"]
View(dataMatrix)

# Select columns to become Y (keep rownames)
Y <- dataMatrix[, c("number_in_cluster_lh", "number_in_cluster_rh", "avdist_in_cluster_lh", "avdist_in_cluster_rh")]
Y <- apply(Y, 2, as.numeric)
View(Y)

# Select columns to become X
X <- dataMatrix[, c("age", "additional_attention_orientation", "additional_memory", "additional_fluencies", "additional_language", "additional_visuospatial")]
colnames(X) <- c("age", "attention_orientation", "memory", "fluencies", "language", "visuospatial")
X <- apply(X, 2, as.numeric)
View(X)

df.pls <- opls(x = X, y = Y, orthoI = 0, permI = 20)





#---- PLS: package ropls -----
# https://bioconductor.org/packages/release/bioc/vignettes/ropls/inst/doc/ropls-vignette.html#43_Partial_least-squares:_PLS_and_PLS-DA
# https://rdrr.io/bioc/ropls/man/opls.html


#------
# One plot

library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)

setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
df <- read.table("avdist_demo_acer_10-30.txt")
df <- df[df$additional_visuospatial != 0, ]
variables <- "avdist_in_cluster" 

for (variable in variables) {
  df[[paste0(variable, "_both_hemi")]] <- (df[[paste0(variable, "_lh")]] + df[[paste0(variable, "_rh")]])/2
} #"_lh", "_rh",
for (variable in variables) {
  for (postfix in c("_both_hemi")) {  
    
    i <- paste0(variable, postfix)
    print(i)
    
    # With outliers
    formula <- as.formula(paste("rank(", i, ") ~ age"))
    model <- lm(formula, data = df)
    
    # Remove outliers
    df$cooksd <- cooks.distance(model)
    n <- nrow(df)
    threshold <- 4 / n
    df_cleaned <- df[df$cooksd < threshold,]
    
    # Model again
    model_nooutliers <- lm(formula, data = df_cleaned)
    print(summary(model_nooutliers))
    
    # Plot final thing
    res <- resid(model_nooutliers)
    p <- ggplot(data = df_cleaned, aes(x = additional_visuospatial, y = res)) +
      geom_point(
        color = "#2E4057",
        alpha = 0.65,
        size = 2.5,
        shape = 16
      ) +
      geom_smooth(
        method = "lm",
        se = TRUE,
        color = "#E84855",
        fill = "#E84855",
        alpha = 0.15,
        linewidth = 0.9
      ) +
      geom_hline(yintercept=0,         
                 color = "#E84855",
                 fill = "#E84855",
                 alpha = 0.15,
                 linewidth = 0.9) + 
      labs(
        x = "ACER",
        y = "Average distance of points \n in cluster from centroid",
        title = paste("Average distance from centroid vs ACER \n (age-regressed)")
      ) +
      theme(
        plot.title = element_text(face = "bold", size = 14, margin = margin(b = 10)),
        axis.title = element_text(color = "#444444", size = 12),
        axis.text = element_text(color = "#666666", size = 10),
        panel.grid.major = element_line(color = "#E8E8E8", linewidth = 0.5),
        panel.grid.minor = element_blank(),
        plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        plot.margin = margin(16, 16, 16, 16)
      )
    print(p)
  }
}









#----- SIMPLE MODEL -----
setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
df <- read.table("avdist_demo_acer_10-30.txt")
df <- df[df$additional_visuospatial != 0, ]
# Create _both_hemi cols
variables <- "avdist_in_cluster"  #c("number_in_cluster", "avdist_in_cluster") #, "avdist_all", "avdist_unnormed", "avdist_normed", 
for (variable in variables) {
  df[[paste0(variable, "_both_hemi")]] <- (df[[paste0(variable, "_lh")]] + df[[paste0(variable, "_rh")]])/2
}#"_lh", "_rh",
for (variable in variables) {
  for (postfix in c("_both_hemi")) {  

    i <- paste0(variable, postfix)
    print(i)

    ggsave("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data/avdist_vs_acer.png", p, width = 7, height = 5, dpi = 300, bg = "white")
    
    # With outliers
    formula <- as.formula(paste("rank(", i, ") ~ additional_visuospatial + age"))
    model <- lm(formula, data = df)

    # Remove outliers
    df$cooksd <- cooks.distance(model)
    n <- nrow(df)
    threshold <- 4 / n
    df_cleaned <- df[df$cooksd < threshold,]

    # Model again
    model_nooutliers <- lm(formula, data = df_cleaned)
    print(summary(model_nooutliers))

    # Plot final thing
    p <- ggplot(data = df_cleaned, aes(x = additional_visuospatial, y = .data[[i]])) +
          geom_point() +
          geom_smooth(method = "lm", se = TRUE) +
          theme_minimal() +
          xlab(i)
    print(p)

  }
}

#----- MODEL COMPARISON: VERSION 1 -----
# note: don't remove outliers, as the AIC diff only works if the same dataset

# for (variable in variables) {
#   for (postfix in c("_lh", "_rh", "_both_hemi")) {
# 
#     i <- paste0(variable, postfix)
#     print(i)
# 
#     ##### Model 1
# 
#     model1_formula <- as.formula(paste("rank(", i, ") ~ age"))
#     model1 <- lm(model1_formula, data = df)
# 
#     ##### Model 2
# 
#     model2_formula <- as.formula(paste("rank(", i, ") ~ additional_visuospatial + age"))
#     model2 <- lm(model2_formula, data = df)
# 
#     ##### Difference
#     delta_aic <- AIC(model1) - AIC(model2)
#     print(delta_aic)
# 
#   }
# }


#----- MODEL COMPARISON: VERSION 2 -----
# note: don't remove outliers, as the AIC diff only works if the same dataset
# 
# model1 <- lm(additional_acer ~ age, data = df)
# model2 <- lm(additional_acer ~ age + number_in_cluster_both_hemi + avdist_in_cluster_both_hemi, data = df)
# model3 <- lm(additional_acer ~ age + avdist_in_cluster_both_hemi, data = df)
# 
# deltaA <- AIC(model1) - AIC(model2)
# print(deltaA)
# deltaB <- AIC(model2) - AIC(model3) # is number_in_cluster meaningful
# print(deltaB)

  
#---- PLS: package pls -----
# https://cran.r-project.org/web/packages/pls/vignettes/pls-manual.html

# scale=TRUE -> scales variables to all have mean 0 and sd 1; ensures no one variable is overly influential 
# due to different units
# validation=CV -> evaluate performance using k-fold cross-validation, with k=10
# Y <- as.matrix(df[, as.vector(rbind(paste0(variables, "_lh"), paste0(variables, "_rh")))])
# model <- plsr(Y ~ age + additional_attention_orientation + additional_memory + additional_fluencies + additional_language + additional_visuospatial, data=df, scale=TRUE, validation="CV")
# summary(model)
# validationplot(model, val.type="MSEP") # black is training, red is CV
# plot(model, plottype = "loadings", comps=1:4, legendpos = "topright")
# plot(model, plottype = "coef", ncomp=1:4)


########################## RUN AGAIN #####################################

# Load packages
library(feather)
library(tidyverse)
library(ggplot2)
library(ggfortify)
library(report)
library(caret)
library(pls)
library(ropls)

setwd("C:/meg/params/03_lh_rh_rerun/camcan_behav_demo/prepped_data")
df <- read.table("avdist_demo_acer_10-30.txt")
df <- df[df$additional_visuospatial != 0, ]
variables <- c("number_in_cluster", "avdist_in_cluster")


Y <- as.matrix(df[, as.vector(rbind(paste0(variables, "_lh"), paste0(variables, "_rh")))])
model <- plsr(Y ~ age + additional_attention_orientation + additional_memory + additional_fluencies + additional_language + additional_visuospatial, data=df, scale=TRUE, validation="CV")
summary(model)
validationplot(model, val.type="MSEP") # black is training, red is CV
plot(model, plottype = "loadings", comps=1:4, legendpos = "topright")
plot(model, plottype = "coef", ncomp=1:4)



