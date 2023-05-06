""" 
The following Python code loads Matlab files, extracts relevant data and metadata,
applies labels to the data using xarray, and combines the labeled data 
from individual trials into a single xarray dataset. 
The final step of the process involves saving the combined dataset
as a NetCDF file for further analysis.
"""
import re

from glob import glob
from pathlib import Path
import numpy as np
import xarray as xr
import scipy.io as sio
from tqdm import tqdm

DATA_FOLDER = "/Volumes/ExtremePro/Analyses/ASP0"

SUBS = ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 
        'S008', 'S009', 'S010', 'S011', 'S012', 'S013', 'S014', 'S015']
sessions = ["Session1", "Session2"]

PATTERN = "S{}"
subject_list = [] 
for i in range(1, 16):
    padded_num = str(i).zfill(3)
    x = PATTERN.format(padded_num)
    subject_list.append(x)
print(subject_list)

if __name__ == "__main__":
    with tqdm(total=len(SUBS)) as pbar:
        for sub in SUBS:
            list_y = []
            for session in sessions:
                trials = [
                    Path(p) for p in glob(f"{DATA_FOLDER}/brainstorm/ASP0_{sub}_{session}_*.mat")
                ]
                for trial in trials:
                    trial_number = re.findall(r"\d+", str(trial))[-1]
                    iter_number = re.findall(r"\d+", str(trial))[-2]
                    # display(trial_number)
                    mstruct = sio.loadmat(trial)
                    values = mstruct["Value"]
                    # time = mstruct["Time"][0] - mstruct["Time"][0][0]
                    time = np.linspace(0, 5, 3000)
                    label_struct = mstruct["Atlas"][
                        0, 0]["Scouts"]["Label"].ravel().tolist()
                    labels = np.array([item.item() for item in label_struct])
                    region_struct = mstruct["Atlas"][
                        0, 0]["Scouts"]["Region"].ravel().tolist()
                    regions = np.array([item.item() for item in region_struct])
                    y = (
                        xr.DataArray(
                            values.T,
                            dims= ["time", "labels"],
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
                        .assign_coords(regions = ("labels", regions)))
                    list_y.append(y)      
            ds = xr.combine_by_coords(list_y)
            ds.to_netcdf(f"{DATA_FOLDER}/interim/timeseries/{sub}_MEG_ASSR_times.nc")
            pbar.update(1)

