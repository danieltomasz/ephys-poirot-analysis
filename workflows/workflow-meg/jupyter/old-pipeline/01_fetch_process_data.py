# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: meg-analysis
#     language: python
#     name: meg-analysis
# ---

# %%

from pathlib import Path
import fooof
import shutil
from pandas.core.frame import DataFrame
import scipy.io  as sio
import numpy as np
import pandas as pd
from fooof import FOOOFGroup,  FOOOF

def get_project_root() -> Path:
    """Return a base path of current folder, similar to R packege 'here'.
        
    Returns:
        Path: Path object pointing to the parent of the folder where the script is located.
            If your script is `/root/scripts/script.py`, the result will be an absolute path '/root'.
    """
    try:
        return Path(__file__).parent.parent
    except NameError as error:
        # This will give you  root folder of the project if this runned through jupyter notebook
        return Path().joinpath().absolute().parents[0]
    except Exception as exception:
        print(exception)

# %% Section for working with data

def process_single_recording_session(path: str) -> DataFrame:
    """[summary]

    Args:
        path (str): [description]

    Returns:
        DataFrame: [description]
    """

    try:    
        data_dict =  mat2dict_scout_psd(path)
        freqs_data  = data_dict["freqs"] 
        powers_data = data_dict["powers"]
        #plot_spectra(freqs_data, powers_data, log_powers=True)
        peaks_df = psd_fooof(freqs_data, powers_data)
        peaks_df = add_columns(peaks_df, data_dict)
        return peaks_df
    except OSError as err:
        print("OS error: {0}".format(err))


def mat2dict_scout_psd(path: str) -> dict:
    """Load content of matfile containg PSD of scouts into Python dict

    Args:
        mat_content (str): Path to file, may be a string or pathlike object

    Returns:
        dict: Dictionary containing all the information  extracted from mat file
    """

    def get_real_names(row_names):
        row_names=  [l.flatten()[0] for l in row_names.flatten()] #flatten
        row_names = [i.split('@')[0] for i in row_names] #delete location
        row_names = [x.strip(' ') for x in row_names]
        row_names = [x.replace(' ', '_') for x in row_names] #remove 
        return row_names

    def split(strng, sep, pos):
        strng = strng.split(sep)
        return sep.join(strng[:pos]), sep.join(strng[pos:])

    #print(sorted(mat_content.keys()))
    #print(mat_content["TF"])
    mat_content = sio.loadmat(path)
    tf = np.ndarray.squeeze(mat_content["TF"])
    row_names = mat_content["RowNames"]
    row_names = get_real_names(row_names)
    freqs = np.ndarray.squeeze(mat_content["Freqs"])
    comment = mat_content["Comment"].tolist()[0].split('|')[1]
    subject_cond = split(comment, "_", 2)[0]
    
    resample = split(split(comment, "_", 5)[1],"_",2)[0]
    condition = comment.split('_Destrieux_')[1]
    data_dict = {'freqs' : freqs, 'powers' : tf, 'row_names' : row_names, 'subject_cond' : subject_cond, 'resample' : resample, 'condition': condition}
    if len(tf)==0:
        print ("TF is empty")
    else:
        return  data_dict  



def fooof2pandas(func):
    """Decorator for fooof function that will transform  foood output into datafram

    Args:
        func ([type]): [description]
    """
    def wrapper(*args, **kwargs):

        fg = func(*args, **kwargs)
        print('Number of model fits: ', len(fg))
        temp_df = pd.DataFrame() # prepare error and slope dataframe
        #temp_df['knee'] = fg.get_params('aperiodic_params', 'knee')
        temp_df['offset'] = fg.get_params('aperiodic_params', 'offset')
        temp_df['exponent'] = fg.get_params('aperiodic_params', 'exponent')

        temp_df['errors']= fg.get_params('error')
        temp_df['r2s']=fg.get_params('r_squared')
        temp_df.insert(0, 'ID', temp_df.index)
        
        peaks = fg.get_params('peak_params') # prepare peaks dataframe
        peaks_df = pd.DataFrame(peaks)
        peaks_df.columns = ['CF', 'PW', 'BW', 'ID']
        peaks_df['ID'] = peaks_df['ID'].astype(int)
        peaks_df = peaks_df.join(temp_df.set_index('ID'), on='ID')
        return peaks_df
    return wrapper


@fooof2pandas
def psd_fooof(freqs, spectra) -> DataFrame:
    """Use FOOOFGroup on data

    Args:
        freqs ([type]): vector with frequencies
        spectra ([type]): Matrix with ROIS x PSD values  #TODO check format

    Returns:
        DataFrame: Fooof values as outputed  in model
    """
    fg = FOOOFGroup(peak_width_limits=[2.5, 8],min_peak_height=0.05, max_n_peaks=6)
    fg.fit(freqs, spectra, freq_range=[3, 48],n_jobs=-1, progress='tqdm')
    return fg


def add_columns(peaks_df: DataFrame, data_dict: DataFrame) -> DataFrame :
    """Add metadata to fooof results

    Args:
        peaks_df (DataFrame): dataframe containing fooof results
        data_dict (DataFrame): dataframe containing metadata related to trial

    Returns:
        DataFrame: [description]
    """
    temp_df = pd.DataFrame()   
    temp_df["ROI"] = data_dict["row_names"]
    temp_df.insert(0, 'ID', temp_df.index)
    temp_df["subject_cond"] = data_dict["subject_cond"]
    temp_df["subjectID"] = data_dict["subject_cond"][:-2]
    temp_df["subject_cond"] = temp_df['subject_cond'].astype('category').str.strip()
    temp_df["condition"] = data_dict["condition"]
    temp_df["S"] = data_dict["condition"]

    temp_df["resample"] = data_dict["resample"]
    x = {'01_resample':'pre', '03_resample':'pre', '02_resample':'post','04_resample':'post'}
    temp_df['P'] = temp_df['resample'].map(x)
    peaks_df = peaks_df.join(temp_df.set_index('ID'), on='ID')
    return peaks_df


def load_conditions_coding(keys_path: str) -> DataFrame:
    """ Load coding telling us what conditions was representing specific recording (Sham or real TDCS)

    Args:
        keys_path (string): Path to file containing matlab struct with the simple mapping

    Returns:
        DataFrame: Dataframe cointaining two rows subject cond like Subject01_A or Subject01_B and condition "sham" or "real"
    """

    keys = sio.loadmat(keys_path)
    row_names = keys["keys"].tolist()[0]
    #row_names=  [l.flatten()[0] for l in lista.flatten()] #fl
    temp_df = pd.DataFrame()   
    temp_df["subject_cond"]  = [l[0].flatten()[0] for l in row_names]
    temp_df["subject_cond"] = temp_df['subject_cond'].astype('category').str.strip()
    temp_df["T"] =  [l[1].flatten()[0] for l in row_names]
    
    return temp_df

def run_pipeline(data_path:str, coding_path: str) -> DataFrame:
    """Load data and output  dataframe

    Returns:
        DataFrame: Values from FOOOF model together with metadata for all subjects
    """

    
    pathlist = Path(data_path).rglob('*.mat')
    pandas_list = []
    for path in pathlist:
        peaks_df=  process_single_recording_session(path)
        pandas_list.append(peaks_df)
    df = pd.concat(pandas_list)
    df2 = load_conditions_coding(coding_path)
    return df.merge(df2, left_on='subject_cond', right_on='subject_cond')


def export_dataframe2csv(final : DataFrame, csv_path: str) -> DataFrame:
    list_of_columns = ['subjectID', 'S', 'T', 'P', 'ROI',	'offset',	'exponent',	'errors',	'r2s'	]
    final_export = final[list_of_columns]
    final_export = final_export.drop_duplicates()
    final_export = final_export.sort_values(by=['subjectID', 'ROI'])
    final_export.to_csv (csv_path, index = False, header=True)
    return final_export

# %%
if __name__ == "__main__":
    root= get_project_root()
    data_path = root / 'data' / 'matlab' / 'tDCS_MEG'
    coding_path = root / 'data' / 'metadata' / 'keys.mat'
    df = run_pipeline(data_path,coding_path)
    csv_path = root / 'data' / 'share' / 'ROI_offset_exponent_dataframe.csv'
    final = export_dataframe2csv(df, csv_path)

# %%
