import argparse
import json
import xarray as xr
import pandas as pd
import numpy as np
from fooof import FOOOFGroup
from poirot.spectrum import my_compute_spectrum

def compute_spectrum(data_input: str, data_output: str,  config: dict):
    fg = FOOOFGroup(
        peak_width_limits=config['peak_width_limits'],
        min_peak_height=config['min_peak_height'],
        max_n_peaks=config['max_n_peaks'],
    )
    freq_range = config['freq_range']
    stacked_cols = config['stacked_cols']
    fs= config['fs']
    
    df_list = []

    ds = xr.open_dataarray(data_input)
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
    temp_df.to_netcdf(data_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute spectrum for a subject.')
    parser.add_argument('-i','--data_input', type=str, help='Folder with timeseries to process')
    parser.add_argument('-o','--data_output', type=str, help='File to save spectrum')
    parser.add_argument('-c','--config', type=str, help='Configuration file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    compute_spectrum(args.data_input, args.data_output, config)
