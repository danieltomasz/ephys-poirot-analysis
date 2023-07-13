#%% imoorts and functions definition
import re
from glob import glob
from pathlib import Path

import numpy as np
import xarray as xr
import scipy.io as sio

from tqdm import tqdm

# Function to generate subject names
def create_subject_names():
    PATTERN_A = "Subject{}_A"
    PATTERN_B = "Subject{}_B"
    SUBS = []
    for i in range(1, 16):
        padded_num = str(i).zfill(2)
        SUBS.extend(
            (PATTERN_A.format(padded_num), PATTERN_B.format(padded_num))
        )
    return SUBS

# Function to load data for a single subject
def load_single_subject(data_folder, sub):
    """
    Load MEG (magnetoencephalography) data for a single subject, and save the resulting timeseries data in a netCDF file.

    inputs:
        data_folder : a string representing the path to the folder containing the MEG data for the subject
        sub: a string representing the subject ID

    Returns:
        ds: an xarray Dataset object containing the unprocessed MEG timeseries data for the subject
    """
    list_trials = []
    trials = [Path(p) for p in glob(f"{data_folder}/brainstorm/{sub}_*.mat")]
    for trial in trials:
            trial_number = re.findall(r"\d+", str(trial))[-1]
            iter_number = re.findall(r"\d{2}_resample", str(trial))[-1]
            # display(trial_number)
            mstruct =  sio.loadmat(trial)
            values = mstruct["Value"]
            # time = mstruct["Time"][0] - mstruct["Time"][0][0]
            #time = np.linspace(0, 5, 3000)
            time = np.linspace(-2, 2, 2401)
            label_struct = mstruct["Atlas"][
                0, 0]["Scouts"]["Label"].ravel().tolist()
            labels = np.array([item.item() for item in label_struct])
            region_struct = mstruct["Atlas"][
                0, 0]["Scouts"]["Region"].ravel().tolist()
            regions = np.array([item.item() for item in region_struct])
            single_trial = (
                xr.DataArray(
                    values.T,
                    dims= ["time", "labels"],
                    coords={
                        "labels": labels,
                        "time": time,
                        "sub": sub,
                        "iter_number": iter_number,
                        "trial": int(trial_number)
                    })
                .expand_dims('trial')
                .expand_dims("iter_number")
                .expand_dims("sub")
                .assign_coords(regions = ("labels", regions)))
            list_trials.append(single_trial.compute())
    ds = xr.combine_by_coords(list_trials)
    ds.to_netcdf(f"{data_folder}/interim/timeseries/{sub}_MEG_ASSR_times.nc")
    return ds
# %% main run
if __name__ == "__main__":
    DATA_FOLDER = "/Volumes/ExtremePro/Analyses/tDCS_MEG"
    subject_names = create_subject_names()
    for sub in tqdm(subject_names, desc='Loading subject data'):
        ds = load_single_subject(DATA_FOLDER,sub)


# %%
