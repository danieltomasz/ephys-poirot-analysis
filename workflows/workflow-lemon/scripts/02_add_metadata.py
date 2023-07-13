# %%
import argparse
import sys
import xarray as xr
import pandas as pd


from poirot.translate import define_region_dict, prepare_grouping


def add_coordinate(da, coordinate, partition_dict, new_coordinate):
    temp = prepare_grouping(da, coordinate, partition_dict)
    return da.assign_coords({new_coordinate: (coordinate, temp)})


def map_regions():
    # function to go from a dict with regions roi to pandas dataframe
    my_dict = define_region_dict()

    df_list = []
    for key, value in my_dict.items():
        df = pd.DataFrame({"roi_names": value}).assign(regions=key)
        df_list.append(df)
    return pd.concat(df_list)


BEHAVIORAL_DATA = ("/Volumes/ExtremePro/Analyses/LEMON/"
                   + "PREPROC/occipital_data_OH_OL_Sonia_2023-05_16.csv")
OUTPUT_FOLDER = "/Volumes/ExtremePro/Analyses/LEMON/OUTPUT"

# Check if the script is running interactively (e.g., in a Jupyter notebook)
if not hasattr(sys, 'ps1'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--behavioral_data",
                        default=BEHAVIORAL_DATA, help="Path to data folder")
    parser.add_argument("-o", "--output_folder",
                        default=OUTPUT_FOLDER, help="Path to output folder")
    args = parser.parse_args()
    BEHAVIORAL_DATA = args.behavioral_data
    OUTPUT_FOLDER = args.output_folder

POWER_SERIES = f"{OUTPUT_FOLDER}/LEMON_power.nc"

if __name__ == "__main__":
    df_average = pd.read_csv(BEHAVIORAL_DATA).rename(
        columns={"mean_offset": "offset", "mean_exponent": "exponent"}
    )

    sub_list = df_average["subject"].values.tolist()

    age_edu_dict = {
        level: df_average.query("`Y_OH_OL` == @level")
        .loc[:, ["subject"]]
        .T.values.tolist()[0]
        for level in ["O_H", "O_L", "Y_H"]
    }

    map_subjects = df_average.loc[:, ["subject", "Y_OH_OL"]]

    da = (  # concatenate all subjects, add aditiona information about regions and grouping
        # xr.concat(regions_psd, dim="sub", coords="all", join="override")
        xr.load_dataarray(POWER_SERIES)
        .pipe(
            add_coordinate,
            coordinate="roi_names",
            partition_dict=define_region_dict(),
            new_coordinate="regions",
        )
        .sel(sub=sub_list)
        .pipe(
            add_coordinate,
            coordinate="sub",
            partition_dict=age_edu_dict,
            new_coordinate="Y_OH_OL",
        )
    )

    da.to_netcdf(f"{OUTPUT_FOLDER}/LEMON_annotated_power.nc")
# %%
