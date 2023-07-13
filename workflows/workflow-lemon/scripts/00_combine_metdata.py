"""
This file contains the code to add the variable combing the age and education
"""
# %%
import pandas as pd
DATA_FOLDER = "/Volumes/ExtremePro/Analyses/LEMON"
BEHAVIORAL_DATA = f"{DATA_FOLDER}/PREPROC/occipital_data_OH_OL_Sonia_2023-04-23.csv"
OUTPUT_FILE = f"{DATA_FOLDER}/PREPROC/occipital_data_OH_OL_Sonia_2023-05_16.csv"


def reorder_columns(df, colname='Y_OH_OL', col_position=1):
    cols = df.columns.tolist()
    # move the column to head of list using index, pop and insert
    cols.insert(col_position, cols.pop(cols.index(colname)))
    # use loc to reorder
    return df[cols]


if __name__ == "__main__":
    final_data = (
        pd.read_csv(BEHAVIORAL_DATA)
        .assign(
            temp_edu=lambda x: x['edu'].replace({'high': 'H', 'low': 'L'}),
            temp_age=lambda x: x['age_group'].replace(
                {'Young': 'Y', 'Old': 'O'}),
            YH_OH_OL=lambda x: x['temp_age'].str.cat(x['temp_edu'], sep="_"))
        .drop(columns=['temp_edu', 'temp_age'])
        .pipe(reorder_columns, colname='Y_OH_OL', col_position=1)
    )
    final_data.to_csv(OUTPUT_FILE, index=False)

# %%
