#%%
# STEP 1: Setup

# Import packages
import mne
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt

# Set directories
matthew_dir="/home/isw3/scratch/camcan/parameterization/outputs" #"/home/matteng/projects/def-awiesman/matteng/parameterization"
cam_dir="/home/isw3/scratch/camcan/meg_outputs" #"/home/matteng/projects/def-awiesman/data-sets/Cam-CAN/meg_outputs"
plot_output="/home/isw3/scratch/camcan/plots"

# STEP 2: Create whitened PSD for each subject and save as stc

# Frequency dimension: Goal is to match the dimension of the stc frequency array, which is:
freq_dim = np.arange(1, 40.25, 0.25).reshape(1, -1)

# List files containing parameterization tables (one for each subject)
os.chdir(matthew_dir)
filenames = os.listdir()

# List of subjects that were skipped for missing stc file
good_subject_list = []

# Loop through files
for file in filenames: 

   # Extract subject from filename
   subject = re.search(r'sub-CC\d{6}', file).group(0)

   ##### PSD Model (exponential)
    
   # This is the list where you will put the model for each vertex
   rows = []

   # Read csv file
   csv = pd.read_csv(file)

   # Get average offset and exponent for this subject (to be used for fixing bad values)
   average_exponent = np.nanmean(csv.iloc[:, 2])
   average_offset = np.nanmean(csv.iloc[:, 1])

   # Loop through rows of csv file
   for i in range(len(csv)): 
        
      # Collect values
      vertex = int(csv.iloc[i, 0])
      exponent = csv.iloc[i, 2]
      offset = csv.iloc[i, 1]

      # Make sure values look okay; if there are errors, replace with subject mean
      if type(exponent) != np.float64 or not np.isfinite(exponent): 
         print("error in exponent for subject " + subject + " vertex " + str(vertex) + ", setting to subject average")
         exponent = average_exponent
      if type(offset) != np.float64 or not np.isfinite(offset): 
         print("error in offset for subject " + subject + " vertex " + str(vertex) + ", setting to subject average")
         offset = average_offset

      # Compute exponential for this vertex
      # In linear space - not in log space
      exponential = 10**(offset - (np.log10(freq_dim))*exponent)
    #   print(exponential)
    #   print(freq_dim[0, 0])
    #   print(offset)
    #   print(exponent)

      # Add the exponential for this vertex to the "rows" list
      rows.append(exponential)

   # The final array of all exponentials for all vertices (cleaned up)
   model = np.array(rows).squeeze()

   ##### Read PSD

   # Get the stc file path
   # Note: there is both an -lh and a -rh in the folder, but they are the same 
   stc_folder_path = cam_dir + "/" + subject + "/"
   stc_path = stc_folder_path + "psd_beamformer_fsaverage"

   # Check if both hemispheres exist; if missing, skip
   if not os.path.isfile(stc_folder_path + "psd_beamformer_fsaverage-lh.stc"):
      print(subject + " missing stc left hemisphere, skipping (won't appear in good_subject_list)")
   elif not os.path.isfile(stc_folder_path + "psd_beamformer_fsaverage-rh.stc"):
      print(subject + " missing stc right hemisphere, skipping (won't appear in good_subject_list)")
   else: 

      # Read the stc file
      stc = mne.read_source_estimate(stc_path)

      # Make sure you're only dealing with frequencies 1 to 40
      new_data = stc.data[:, int(1/0.25):int(40/0.25)+1]
      new_times = stc.times[int(1/0.25):]
      new_stc = mne.SourceEstimate(
         data=new_data,
         vertices=stc.vertices,
         tmin=new_times[0],
         tstep=stc.tstep,
      )

      ##### Subtraction

      # Whiten PSD: Subtract model PSD from real PSD
      # modeL: comes in not logged (linear)
      # stc data: comes in not logged (linear)
      # frequency is linear for both
      # subtraction happens in linear-linear space
      whitened_psd = new_stc.data - model

      # Create a plot for whitened PSD, and save it for review
      plt.figure()
      plt.plot(freq_dim[0], np.average(model.T, axis=1), label="Aperiodic fit", color="blue")
      plt.plot(new_stc.times, np.average(new_stc.data.T, axis=1), label="Original PSD", color="black")
      plt.plot(freq_dim.T, np.average(whitened_psd.T, axis=1), label="Whitened PSD", color="red")
      plt.ylabel("Power")
      plt.xlabel("Frequency")
      plt.legend()
      plt.title(subject + " detrending")
      plt.savefig(plot_output + "/" + subject + ".png", dpi=300, bbox_inches="tight") 
      plt.close()

      # Convert the whitened psd to stc, then save it
      whitened_psd_stc = mne.SourceEstimate(
         data=whitened_psd,
         vertices=stc.vertices,
         tmin=freq_dim[0, 0],
         tstep=stc.tstep,
         )
      whitened_psd_stc.save(stc_folder_path + "/psd_whitened_beamformer", overwrite=True)

      # Add to list of subjects run
      good_subject_list.append(subject)


