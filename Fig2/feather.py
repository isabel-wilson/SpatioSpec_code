import pickle
path ="C:/meg/params/03_lh_rh_rerun/mean_stc_COM_8-30_lh"

with open(path + ".pkl", "rb") as f:
   data = pickle.load(f)

data.to_feather(path + ".rds")