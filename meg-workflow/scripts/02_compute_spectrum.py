import argparse
import json
import xarray as xr
import pandas as pd
import numpy as np
from fooof import FOOOFGroup
from tqdm import tqdm
from poirot.spectrum import my_compute_spectrum

def compute_spectrum(subject: str, data_folder: str, config: dict):
    fs = 600

    fg = FOOOFGroup(
        peak_width_limits=config['peak_width_limits'],
        min_peak_height=config['min_peak_height'],
        max_n_peaks=config['max_n_peaks'],
    )

    freq_range = config['freq_range']
    stacked_cols = config['stacked_cols']
    df_list = []

    ds = xr.open_dataarray(f"{data_folder}/interim/timeseries/{subject}_MEG_ASSR_times.nc")
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
    temp_df.to_netcdf(f"{data_folder}/interim/power/{subject}_MEG_ASSR_power.nc")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute spectrum for a subject.')
    parser.add_argument('-s','--sub', type=str, help='Subject')
    parser.add_argument('-d','--datafolder', type=str, help='Data folder')
    parser.add_argument('-c','--config', type=str, help='Configuration file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    compute_spectrum(args.sub, args.datafolder, config)
