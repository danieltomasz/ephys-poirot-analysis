import re
import argparse
from typing import List, Union
import numpy as np
import xarray as xr
import scipy.io as sio
from tqdm import tqdm
from pathlib import Path
from glob import glob

SESSIONS = ["Session1", "Session2"]

def get_trials(sub: str, session: str, data_folder: str) -> List[Path]:
    return [Path(p) for p in glob(f"{data_folder}/brainstorm/ASP0_{sub}_{session}_*.mat")]

def load_matlab_file(trial: Path) -> dict:
    return sio.loadmat(trial)

def process_trial(trial: Path, sub: str, session: str) -> xr.DataArray:
    trial_number = re.findall(r"\d+", str(trial))[-1]
    iter_number = re.findall(r"\d+", str(trial))[-2]

    mstruct = load_matlab_file(trial)
    values = mstruct["Value"]
    time = np.linspace(0, 5, 3000)

    label_struct = mstruct["Atlas"][0, 0]["Scouts"]["Label"].ravel().tolist()
    labels = np.array([item.item() for item in label_struct])

    region_struct = mstruct["Atlas"][0, 0]["Scouts"]["Region"].ravel().tolist()
    regions = np.array([item.item() for item in region_struct])
    return (
        xr.DataArray(
            values.T,
            dims=["time", "labels"],
            coords={
                "labels": labels,
                "time": time,
                "sub": sub,
                "session": session,
                "iter_number": int(iter_number),
                "trial": int(trial_number)
            })
        .expand_dims('trial')
        .expand_dims("iter_number")
        .expand_dims("sub")
        .expand_dims("session")
        .assign_coords(regions=("labels", regions))
    )


def process_sub(sub: str, data_folder: str) -> List[xr.DataArray]:
    list_y = []
    for session in SESSIONS:
        trials = get_trials(sub, session, data_folder)
        for trial in trials:
            y = process_trial(trial, sub, session)
            list_y.append(y)
    return list_y

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process matlab data.')
    parser.add_argument('-s','--sub', type=str, help='Subject to process')
    parser.add_argument('-d','--data_folder', type=str, help='Folder containing the data')
    parser.add_argument('-o','--output_folder', type=str, help='Folder containing the data')
    args = parser.parse_args()
    list_y = process_sub(args.sub, args.data_folder)
    ds = xr.combine_by_coords(list_y)
    ds.to_netcdf(args.output_folder)
