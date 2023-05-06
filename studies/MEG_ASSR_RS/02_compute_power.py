import xarray as xr
import pandas as pd
import numpy as np
from fooof import  FOOOFGroup

from tqdm import tqdm


from poirot.spectrum import  my_compute_spectrum

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

#%% Compute spectrum and save to netcdf


if __name__ == "__main__":
    for subject in tqdm(SUBS, desc='Progress', position=0, leave=False):
        ds = xr.open_dataarray(f"{DATA_FOLDER}/interim/timeseries/{subject}_MEG_ASSR_times.nc")
        ds.close()
        temp_df = (
            xr.apply_ufunc(
                my_compute_spectrum, ds, 
                vectorize=True,
                input_core_dims=[['time']],
                output_core_dims=[['freqs']],
                kwargs = {"fs" :fs, "nperseg":4*fs})
            .assign_coords(freqs = lambda x: np.linspace(0,fs/2, len(x.freqs)))
        )
        temp_df.to_netcdf(f"{DATA_FOLDER}/interim/power/{subject}_MEG_ASSR_power.nc")
