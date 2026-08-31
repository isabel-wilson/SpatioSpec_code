"""
This script creates a matrix of peaks for every subject and frequency
Adapted for either rh or lh

03/14 note: whitened data is on fir, so you can run the make-center-of-mass-matrix section on fir
"""
#%%
# Import packages
import mne
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pickle
from pathlib import Path

# USER INPUT: 
hemi = "rh"
base_dir = "/scratch/isw3/camcan_isabel"

# Load surface
inflated_surface_rr, inflated_surface_tri = mne.read_surface(f"{base_dir}/fs_subjects/fsaverage/surf/{hemi}.inflated")

# Frequencies to loop through
freqs = np.arange(8, 30, 0.25)


#%% 
#########################################################################
# Useful functions

def stc_one_timepoint(stc, t): 
   """
   Given an stc with multiple timepoints, create a new stc that contains 
   only the given timepoint. The stc will be symmetrical, with the right side a 
   copy of the left.
   """

   # Create a new stc that contains only this timepoint
   if hemi == "lh": 
      t_stc_side_data = stc.lh_data[:, stc.time_as_index(t)]
   else: 
      t_stc_side_data = stc.rh_data[:, stc.time_as_index(t)]

   # Find top 20% of the positive; set everything below to 0
   t_stc_side_data[t_stc_side_data < 0] = 0
   lim = np.percentile(t_stc_side_data, 80)
   t_stc_side_data[t_stc_side_data < lim] = 0

   # Bind lh and rh together
   t_stc_lh_rh_data = np.vstack((t_stc_side_data, t_stc_side_data))

   # Make stc (both hemi)
   t_stc = mne.SourceEstimate(
      data = t_stc_lh_rh_data, 
      vertices=stc.vertices,
      tmin=t, 
      tstep=stc.tstep
   )
   
   return t_stc

def plot_stc(savedir, brain_to_plot, t, center_of_mass): 
   """
   Plots the given brain at the given time with a dot at the center of mass
   """
   brain = brain_to_plot.plot(
      subject="fsaverage",
      subjects_dir=f"{base_dir}/fs_subjects",
      hemi=hemi,
      initial_time=t,
      time_viewer=False,
      time_label="Frequency " + f"{t:.{2}f}",
      colormap="viridis", 
      surface = 'inflated'
      )
   brain.add_foci(center_of_mass, coords_as_verts=True, hemi=hemi, color='red', scale_factor=1.0)
   brain.show_view("dorsal")
   brain.save_image(savedir + str(t) + ".png")

def make_3d_plot(savedir, current_freq_rows):
   fig = plt.figure()
   ax = fig.add_subplot(111, projection='3d')

   for _, row in current_freq_rows.iterrows():
      x = row["x"]
      y = row["y"]
      z = row["z"]
      ax.scatter(xs = x, ys = y, zs = z, color="blue", s = 2)

   ax.set_zlabel("z (up)")
   ax.set_xlabel(f"x (right), on {hemi}")
   ax.set_ylabel("y (front)")
   # ax.set_zlim(-80, 80)
   # ax.set_xlim(-60, 60)
   # ax.set_ylim(-100, 100)
   ax.set_title("Frequency: " + f"{f:.{2}f}")

   fig.savefig(savedir + str(f) + ".png", dpi=300, bbox_inches=None)
   

#%%
#########################################################################
# Create a center-of-mass matrix

# Load subjects. Some of the subjects in matthew_dir aren't in cam_dir, and vice versa. 
subjects_long = ['sub-CC110033', 
 'sub-CC110037',  
 'sub-CC110045',
 'sub-CC110056',
 'sub-CC110069',
 'sub-CC110087',
 'sub-CC110098',
 'sub-CC110101',
 'sub-CC110126',
 'sub-CC110174',
 'sub-CC110182',
 'sub-CC110187',
 'sub-CC110319',
 'sub-CC110411',
 'sub-CC110606',
 'sub-CC112141',
 'sub-CC120008',
 'sub-CC120049',
 'sub-CC120061',
 'sub-CC120065',
 'sub-CC120120',
 'sub-CC120166',
 'sub-CC120182',
 'sub-CC120218',
 'sub-CC120264',
 'sub-CC120276',
 'sub-CC120309',
 'sub-CC120313',
 'sub-CC120319',
 'sub-CC120347',
 'sub-CC120376',
 'sub-CC120409',
 'sub-CC120462',
 'sub-CC120469',
 'sub-CC120470',
 'sub-CC120550',
 'sub-CC120640',
 'sub-CC120727',
 'sub-CC120764',
 'sub-CC120795',
 'sub-CC121106',
 'sub-CC121111',
 'sub-CC121144',
 'sub-CC121158',
 'sub-CC121317',
 'sub-CC121397',
 'sub-CC121411',
 'sub-CC121428',
 'sub-CC121479',
 'sub-CC121685',
 'sub-CC121795',
 'sub-CC122172',
 'sub-CC122405',
 'sub-CC210023',
 'sub-CC210051',
 'sub-CC210088',
 'sub-CC210124',
 'sub-CC210148',
 'sub-CC210172',
 'sub-CC210182',
 'sub-CC210250',
 'sub-CC210519',
 'sub-CC210526',
 'sub-CC210617',
 'sub-CC210657',
 'sub-CC212153',
 'sub-CC220098',
 'sub-CC220107',
 'sub-CC220115',
 'sub-CC220132',
 'sub-CC220151',
 'sub-CC220198',
 'sub-CC220203',
 'sub-CC220223',
 'sub-CC220232',
 'sub-CC220234',
 'sub-CC220284',
 'sub-CC220323',
 'sub-CC220335',
 'sub-CC220352',
 'sub-CC220372',
 'sub-CC220419',
 'sub-CC220506',
 'sub-CC220518',
 'sub-CC220526',
 'sub-CC220535',
 'sub-CC220567',
 'sub-CC220610',
 'sub-CC220635',
 'sub-CC220697',
 'sub-CC220713',
 'sub-CC220828',
 'sub-CC220843',
 'sub-CC220901',
 'sub-CC220920',
 'sub-CC220974',
 'sub-CC220999',
 'sub-CC221002',
 'sub-CC221031',
 'sub-CC221033',
 'sub-CC221040',
 'sub-CC221054',
 'sub-CC221107',
 'sub-CC221209',
 'sub-CC221220',
 'sub-CC221244',
 'sub-CC221324',
 'sub-CC221336',
 'sub-CC221352',
 'sub-CC221373',
 'sub-CC221487',
 'sub-CC221511',
 'sub-CC221527',
 'sub-CC221565',
 'sub-CC221585',
 'sub-CC221595',
 'sub-CC221648',
 'sub-CC221740',
 'sub-CC221755',
 'sub-CC221775',
 'sub-CC221828',
 'sub-CC221886',
 'sub-CC221935',
 'sub-CC221954',
 'sub-CC221977',
 'sub-CC221980',
 'sub-CC222120',
 'sub-CC222125',
 'sub-CC222185',
 'sub-CC222258',
 'sub-CC222264',
 'sub-CC222304',
 'sub-CC222326',
 'sub-CC222367',
 'sub-CC222496',
 'sub-CC222555',
 'sub-CC222652',
 'sub-CC222797',
 'sub-CC222956',
 'sub-CC223085',
 'sub-CC223115',
 'sub-CC223286',
 'sub-CC310008',
 'sub-CC310051',
 'sub-CC310052',
 'sub-CC310086',
 'sub-CC310129',
 'sub-CC310135',
 'sub-CC310142',
 'sub-CC310160',
 'sub-CC310203',
 'sub-CC310214',
 'sub-CC310224',
 'sub-CC310252',
 'sub-CC310256',
 'sub-CC310331',
 'sub-CC310361',
 'sub-CC310385',
 'sub-CC310391',
 'sub-CC310397',
 'sub-CC310400',
 'sub-CC310410',
 'sub-CC310414',
 'sub-CC310450',
 'sub-CC310463',
 'sub-CC310473',
 'sub-CC312058',
 'sub-CC312222',
 'sub-CC320002',
 'sub-CC320022',
 'sub-CC320059',
 'sub-CC320088',
 'sub-CC320089',
 'sub-CC320107',
 'sub-CC320109',
 'sub-CC320160',
 'sub-CC320202',
 'sub-CC320206',
 'sub-CC320218',
 'sub-CC320267',
 'sub-CC320297',
 'sub-CC320321',
 'sub-CC320325',
 'sub-CC320336',
 'sub-CC320342',
 'sub-CC320379',
 'sub-CC320417',
 'sub-CC320429',
 'sub-CC320448',
 'sub-CC320461',
 'sub-CC320478',
 'sub-CC320500',
 'sub-CC320553',
 'sub-CC320568',
 'sub-CC320574',
 'sub-CC320575',
 'sub-CC320576',
 'sub-CC320608',
 'sub-CC320616',
 'sub-CC320621',
 'sub-CC320636',
 'sub-CC320651',
 'sub-CC320661',
 'sub-CC320680',
 'sub-CC320686',
 'sub-CC320687',
 'sub-CC320698',
 'sub-CC320759',
 'sub-CC320776',
 'sub-CC320814',
 'sub-CC320850',
 'sub-CC320870',
 'sub-CC320888',
 'sub-CC320893',
 'sub-CC320904',
 'sub-CC321000',
 'sub-CC321025',
 'sub-CC321053',
 'sub-CC321069',
 'sub-CC321073',
 'sub-CC321087',
 'sub-CC321107',
 'sub-CC321137',
 'sub-CC321154',
 'sub-CC321174',
 'sub-CC321203',
 'sub-CC321281',
 'sub-CC321291',
 'sub-CC321331',
 'sub-CC321368',
 'sub-CC321428',
 'sub-CC321431',
 'sub-CC321464',
 'sub-CC321504',
 'sub-CC321506',
 'sub-CC321529',
 'sub-CC321544',
 'sub-CC321557',
 'sub-CC321585',
 'sub-CC321594',
 'sub-CC321595',
 'sub-CC321880',
 'sub-CC321899',
 'sub-CC321976',
 'sub-CC322186',
 'sub-CC410015',
 'sub-CC410032',
 'sub-CC410040',
 'sub-CC410084',
 'sub-CC410086',
 'sub-CC410091',
 'sub-CC410094',
 'sub-CC410097',
 'sub-CC410101',
 'sub-CC410113',
 'sub-CC410119',
 'sub-CC410121',
 'sub-CC410129',
 'sub-CC410169',
 'sub-CC410173',
 'sub-CC410177',
 'sub-CC410179',
 'sub-CC410182',
 'sub-CC410220',
 'sub-CC410222',
 'sub-CC410226',
 'sub-CC410243',
 'sub-CC410248',
 'sub-CC410251',
 'sub-CC410284',
 'sub-CC410287',
 'sub-CC410289',
 'sub-CC410297',
 'sub-CC410323',
 'sub-CC410325',
 'sub-CC410354',
 'sub-CC410387',
 'sub-CC410390',
 'sub-CC410432',
 'sub-CC412004',
 'sub-CC412021',
 'sub-CC420060',
 'sub-CC420061',
 'sub-CC420071',
 'sub-CC420075',
 'sub-CC420089',
 'sub-CC420091',
 'sub-CC420094',
 'sub-CC420100',
 'sub-CC420137',
 'sub-CC420143',
 'sub-CC420148',
 'sub-CC420149',
 'sub-CC420157',
 'sub-CC420162',
 'sub-CC420167',
 'sub-CC420173',
 'sub-CC420180',
 'sub-CC420182',
 'sub-CC420197',
 'sub-CC420198',
 'sub-CC420202',
 'sub-CC420204',
 'sub-CC420217',
 'sub-CC420222',
 'sub-CC420226',
 'sub-CC420229',
 'sub-CC420231',
 'sub-CC420236',
 'sub-CC420241',
 'sub-CC420260',
 'sub-CC420261',
 'sub-CC420286',
 'sub-CC420322',
 'sub-CC420324',
 'sub-CC420348',
 'sub-CC420356',
 'sub-CC420383',
 'sub-CC420392',
 'sub-CC420396',
 'sub-CC420402',
 'sub-CC420412',
 'sub-CC420433',
 'sub-CC420435',
 'sub-CC420454',
 'sub-CC420462',
 'sub-CC420464',
 'sub-CC420493',
 'sub-CC420566',
 'sub-CC420582',
 'sub-CC420587',
 'sub-CC420589',
 'sub-CC420623',
 'sub-CC420720',
 'sub-CC420729',
 'sub-CC420776',
 'sub-CC510039',
 'sub-CC510043',
 'sub-CC510050',
 'sub-CC510076',
 'sub-CC510086',
 'sub-CC510115',
 'sub-CC510161',
 'sub-CC510163',
 'sub-CC510208',
 'sub-CC510220',
 'sub-CC510226',
 'sub-CC510237',
 'sub-CC510242',
 'sub-CC510243',
 'sub-CC510255',
 'sub-CC510256',
 'sub-CC510258',
 'sub-CC510259',
 'sub-CC510284',
 'sub-CC510304',
 'sub-CC510321',
 'sub-CC510323',
 'sub-CC510329',
 'sub-CC510342',
 'sub-CC510354',
 'sub-CC510355',
 'sub-CC510392',
 'sub-CC510393',
 'sub-CC510395',
 'sub-CC510415',
 'sub-CC510433',
 'sub-CC510434',
 'sub-CC510473',
 'sub-CC510474',
 'sub-CC510480',
 'sub-CC510483',
 'sub-CC510486',
 'sub-CC510534',
 'sub-CC510548',
 'sub-CC510551',
 'sub-CC510609',
 'sub-CC510629',
 'sub-CC510648',
 'sub-CC520002',
 'sub-CC520011',
 'sub-CC520013',
 'sub-CC520042',
 'sub-CC520053',
 'sub-CC520055',
 'sub-CC520065',
 'sub-CC520078',
 'sub-CC520083',
 'sub-CC520097',
 'sub-CC520122',
 'sub-CC520127',
 'sub-CC520134',
 'sub-CC520136',
 'sub-CC520147',
 'sub-CC520168',
 'sub-CC520175',
 'sub-CC520197',
 'sub-CC520209',
 'sub-CC520211',
 'sub-CC520215',
 'sub-CC520239',
 'sub-CC520247',
 'sub-CC520253',
 'sub-CC520254',
 'sub-CC520279',
 'sub-CC520287',
 'sub-CC520377',
 'sub-CC520390',
 'sub-CC520395',
 'sub-CC520398',
 'sub-CC520424',
 'sub-CC520477',
 'sub-CC520480',
 'sub-CC520503',
 'sub-CC520517',
 'sub-CC520552',
 'sub-CC520560',
 'sub-CC520562',
 'sub-CC520584',
 'sub-CC520585',
 'sub-CC520597',
 'sub-CC520607',
 'sub-CC520624',
 'sub-CC520673',
 'sub-CC520745',
 'sub-CC520868',
 'sub-CC520980',
 'sub-CC521040',
 'sub-CC610022',
 'sub-CC610028',
 'sub-CC610039',
 'sub-CC610040',
 'sub-CC610046',
 'sub-CC610050',
 'sub-CC610051',
 'sub-CC610052',
 'sub-CC610058',
 'sub-CC610061',
 'sub-CC610071',
 'sub-CC610076',
 'sub-CC610099',
 'sub-CC610101',
 'sub-CC610146',
 'sub-CC610178',
 'sub-CC610210',
 'sub-CC610212',
 'sub-CC610227',
 'sub-CC610285',
 'sub-CC610288',
 'sub-CC610292',
 'sub-CC610308',
 'sub-CC610344',
 'sub-CC610372',
 'sub-CC610392',
 'sub-CC610405',
 'sub-CC610469',
 'sub-CC610496',
 'sub-CC610508',
 'sub-CC610568',
 'sub-CC610575',
 'sub-CC610576',
 'sub-CC610594',
 'sub-CC610625',
 'sub-CC610631',
 'sub-CC610653',
 'sub-CC610658',
 'sub-CC610671',
 'sub-CC620005',
 'sub-CC620026',
 'sub-CC620073',
 'sub-CC620085',
 'sub-CC620090',
 'sub-CC620114',
 'sub-CC620118',
 'sub-CC620121',
 'sub-CC620129',
 'sub-CC620152',
 'sub-CC620164',
 'sub-CC620193',
 'sub-CC620259',
 'sub-CC620262',
 'sub-CC620264',
 'sub-CC620279',
 'sub-CC620284',
 'sub-CC620314',
 'sub-CC620354',
 'sub-CC620359',
 'sub-CC620405',
 'sub-CC620406',
 'sub-CC620413',
 'sub-CC620429',
 'sub-CC620436',
 'sub-CC620444',
 'sub-CC620451',
 'sub-CC620454',
 'sub-CC620466',
 'sub-CC620479',
 'sub-CC620490',
 'sub-CC620496',
 'sub-CC620499',
 'sub-CC620515',
 'sub-CC620518',
 'sub-CC620526',
 'sub-CC620549',
 'sub-CC620557',
 'sub-CC620567',
 'sub-CC620572',
 'sub-CC620592',
 'sub-CC620610',
 'sub-CC620619',
 'sub-CC620659',
 'sub-CC620685',
 'sub-CC620720',
 'sub-CC620785',
 'sub-CC620793',
 'sub-CC620885',
 'sub-CC620919',
 'sub-CC620935',
 'sub-CC621011',
 'sub-CC621080',
 'sub-CC621118',
 'sub-CC621128',
 'sub-CC621184',
 'sub-CC621199',
 'sub-CC621248',
 'sub-CC621284',
 'sub-CC621642',
 'sub-CC710037',
 'sub-CC710088',
 'sub-CC710131',
 'sub-CC710154',
 'sub-CC710176',
 'sub-CC710214',
 'sub-CC710313',
 'sub-CC710342',
 'sub-CC710350',
 'sub-CC710382',
 'sub-CC710429',
 'sub-CC710446',
 'sub-CC710462',
 'sub-CC710486',
 'sub-CC710494',
 'sub-CC710548',
 'sub-CC710551',
 'sub-CC710566',
 'sub-CC710591',
 'sub-CC710664',
 'sub-CC710679',
 'sub-CC710858',
 'sub-CC710982',
 'sub-CC711027',
 'sub-CC711035',
 'sub-CC711128',
 'sub-CC711158',
 'sub-CC711244',
 'sub-CC711245',
 'sub-CC712027',
 'sub-CC720023',
 'sub-CC720071',
 'sub-CC720119',
 'sub-CC720188',
 'sub-CC720238',
 'sub-CC720290',
 'sub-CC720304',
 'sub-CC720329',
 'sub-CC720358',
 'sub-CC720400',
 'sub-CC720407',
 'sub-CC720497',
 'sub-CC720511',
 'sub-CC720516',
 'sub-CC720622',
 'sub-CC720646',
 'sub-CC720670',
 'sub-CC720685',
 'sub-CC720941',
 'sub-CC720986',
 'sub-CC721052',
 'sub-CC721107',
 'sub-CC721114',
 'sub-CC721224',
 'sub-CC721291',
 'sub-CC721292',
 'sub-CC721374',
 'sub-CC721377',
 'sub-CC721392',
 'sub-CC721418',
 'sub-CC721434',
 'sub-CC721504',
 'sub-CC721519',
 'sub-CC721532',
 'sub-CC721585',
 'sub-CC721648',
 'sub-CC721707',
 'sub-CC721729',
 'sub-CC721888',
 'sub-CC721891',
 'sub-CC721894',
 'sub-CC722421',
 'sub-CC722536',
 'sub-CC722542',
 'sub-CC722651',
 'sub-CC722891',
 'sub-CC723197']

subjects = list(map(lambda x: x.removeprefix("sub-CC"), subjects_long))

# Create empty dataframe
COM_coord_subject_df = pd.DataFrame(columns=["subject", "freq", "x", "y", "z"])

for subject in subjects: 
   print(subject)

   # Load stc
   file = f"{base_dir}/meg_outputs/sub-CC{subject}/psd_whitened_beamformer"
   stc = mne.read_source_estimate(file)

   for f in freqs:
      t_stc = stc_one_timepoint(stc, f)

      if hemi=="lh": 
         relevant_data = t_stc.lh_data
      else: 
         relevant_data = t_stc.rh_data

      # If all vertices are 0, set peak to an array of nans
      if np.all(relevant_data==0): 
         COM_coord_subject_df.loc[len(COM_coord_subject_df)] = [subject, f, None, None, None]
      else:
         COM_vertex, _ = t_stc.get_peak(hemi=hemi)
         COM_coord = inflated_surface_rr[COM_vertex] # this gives you an array
         COM_coord_subject_df.loc[len(COM_coord_subject_df)] = [subject, f, COM_coord[0], COM_coord[1], COM_coord[2]]

# Write to file
with open(f"{base_dir}/COM_coord_subject_df_8_to_30_{hemi}.pkl", "wb") as f:
   pickle.dump(COM_coord_subject_df, f)


# %%
#########################################################################
# PLOT
# For each timepoint: 
# 1. create an array of coordinates from all subjects
# 2. take this array and plot it
# 3. as well, add the mean x y z calculated fresh from the individual subjects. 
# 4. save fig

savedir = "C:/meg/params/1211_individual_spread_8-30_normed/"
olds = os.listdir(savedir)
for old in olds: 
   os.remove(savedir + old)

with open("C:/meg/params/COM_coord_subject_df_8_to_30_normalized.pkl", "rb") as f:
   COM_coord_subject_df = pickle.load(f)

for f in freqs:
   current_freq_rows = COM_coord_subject_df[COM_coord_subject_df["freq"] == f]
   make_3d_plot(savedir, current_freq_rows)



# %%
#########################################################################
# What does it look like when normalized?? Normalize, then look at it again.

with open("C:/meg/params/COM_coord_subject_df_8_to_30.pkl", "rb") as f:
   COM_coord_subject_df = pickle.load(f)

# Remove negatives and then normalize
COM_coord_subject_df['x'] = COM_coord_subject_df['x'] + 100
COM_coord_subject_df['x'] = (COM_coord_subject_df['x'] - COM_coord_subject_df['x'].min()) / (COM_coord_subject_df['x'].max() - COM_coord_subject_df['x'].min())
COM_coord_subject_df['y'] = COM_coord_subject_df['y'] + 100
COM_coord_subject_df['y'] = (COM_coord_subject_df['y'] - COM_coord_subject_df['y'].min()) / (COM_coord_subject_df['y'].max() - COM_coord_subject_df['y'].min())
COM_coord_subject_df['z'] = COM_coord_subject_df['z'] + 100
COM_coord_subject_df['z'] = (COM_coord_subject_df['z'] - COM_coord_subject_df['z'].min()) / (COM_coord_subject_df['z'].max() - COM_coord_subject_df['z'].min())
COM_coord_subject_df.head

#for f in freqs:
  # current_freq_rows = COM_coord_subject_df[COM_coord_subject_df["freq"] == f]
  # make_3d_plot_v2(savedir, current_freq_rows)

with open("C:/meg/params/COM_coord_subject_df_8_to_30_normalized.pkl", "wb") as f:
   pickle.dump(COM_coord_subject_df, f)

# %%
# BONUS: plot 3d freesurfer brain
import matplotlib.pyplot as plt
import nibabel.freesurfer.io as fs
import mne

fig = plt.figure()
coords, faces = mne.read_surface("C:/meg/params/fs_subjects/fsaverage/surf/rh.inflated")
sulc = fs.read_morph_data("C:/meg/params/fs_subjects/fsaverage/surf/rh.sulc")
ax2 = fig.add_subplot(1, 2, 1, projection='3d')
ax2.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c=sulc, cmap='Greys', s = 0.2)
ax2.set_zlim(-100, 100)
ax2.set_xlim(-100, 100)
ax2.set_ylim(-100, 100)

# %%
