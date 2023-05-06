import xarray as xr
import pandas as pd
import numpy as np
import tqdm as tqdm
from fooof import  FOOOFGroup

from poirot.spectrum import  specparam_attributes, my_compute_spectrum

DATA_FOLDER = "/Volumes/ExtremePro/Analyses/ASP0"

SUBS = ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 
        'S008', 'S009', 'S010', 'S011', 'S012', 'S013', 'S014', 'S015']

sessions = ["Session1", "Session2"]

fs = 600

fg = FOOOFGroup(
    peak_width_limits=[2, 8],
    min_peak_height=0.1,
    max_n_peaks=6,
)

freq_range = [2, 48]
stacked_cols = ['labels','sub','session']

df_list = []

#%% Compute parameters

#for subject in tqdm(subs, desc='Progress', position=0, leave=False):
if __name__ == "__main__":
    for subject in SUBS:
        ds = xr.open_dataarray(f"{DATA_FOLDER }/interim/timeseries/{subject}_MEG_ASSR_times.nc")
        ds.close()
        temp_df = (
            xr.apply_ufunc(
                my_compute_spectrum, ds, 
                vectorize=True,
                input_core_dims=[['time']],
                output_core_dims=[['freqs']],
                kwargs = {"fs" :fs, "nperseg":4*fs})
            .assign_coords(freqs = lambda x: np.linspace(0,fs/2, len(x.freqs)))
            .mean("trial")
            .mean("iter_number")
            .pipe(
                specparam_attributes,
                stacked_cols=stacked_cols,
                fg=fg,
                freq_range=freq_range,
            )
        )
        df_list.append(temp_df)
        #pbar.update(1)
    # Save to HDF5
    df = pd.concat(df_list)
    with pd.HDFStore("MEG_ASSR_specparams.h5", 'w') as store:
        store.put('specparam', df, format='fixed')

# TODO: #1 Write parameters used in analysis when saving specparam  dataframe into h5 storage