# %% Step 1: Load the data from the matlab files to list of xarray
from glob import glob
import argparse
import re
import sys
from pathlib import Path
import xarray as xr

from poirot.load_data import load_mat_file

# Parse command line arguments
# Default data folder
DATA_FOLDER = "/Volumes/ExtremePro/Analyses/LEMON"
OUTPUT_FOLDER = Path(f"{DATA_FOLDER}/OUTPUT")

if __name__ == "__main__":
    # Check if the script is running interactively (e.g., in a Jupyter notebook)
    if not hasattr(sys, 'ps1'):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--data_folder",
                            default=DATA_FOLDER, help="Path to data folder")
        parser.add_argument("-o", "--output_folder",
                            default=OUTPUT_FOLDER, help="Path to output folder")
        args = parser.parse_args()
        DATA_FOLDER = args.data_folder
        OUTPUT_FOLDER = Path(args.output_folder)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    RAW_FOLDER = f"{DATA_FOLDER}/RAW"
    DATASET_FOLDER = f"{RAW_FOLDER}/lemon_rsEEG_dataset"

    pandas_list = []
    files_EC = [Path(p) for p in glob(f"{DATASET_FOLDER}/*/*EO.mat")]

    regions_psd = []
    for path_mat in files_EC:
        sub = re.findall("sub-[0-9]{6}", str(path_mat))
        temp = load_mat_file(path_mat, sub)
        # temp_regions = temp
        if temp.freqs.values.size > 51:
            regions_psd.append(temp)

    da = xr.concat(regions_psd, dim="sub", coords="all", join="override")
    da.to_netcdf(OUTPUT_FOLDER / "LEMON_power.nc")


# %%
