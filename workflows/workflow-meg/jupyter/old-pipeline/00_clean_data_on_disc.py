# %%
from pathlib import Path
import fooof
import shutil
from pandas.core.frame import DataFrame
import scipy.io  as sio
import numpy as np
import pandas as pd

def copy_without_patterns(input_path, destination_path, list_of_patterns):
    shutil.copytree(input_path, destination_path, ignore=shutil.ignore_patterns(*list_of_patterns))

def copy_all_data():
    # Copy the data from backup to fresh folder
    input_path = "/media/daniel/TOSHIBA EXT1/BACKUP DATA/tDCS_MEG_Marinazzo/data/" # source path 
    destination_path = "/media/daniel/ExtremePro1/tDCS_MEG/data/" # destination path
    patterns = ["@raw*", "matrix_scout*", "results*"] #pattern to exclude
    copy_without_patterns(input_path,destination_path, patterns)

def remove_brainstorm():
    """After copying data into Brainstorm project, Brainstorm config need to be deleted, not doing that will cause error when running pipeline

    """
    def remove_folder(folder_path):
        """Function for removing folders 
        
        """    
        try:
            shutil.rmtree(folder_path)
        except OSError as e:
            print("Error: %s : %s" % (folder_path, e.strerror))

    brainstorm_path = "/home/daniel/.brainstorm"
    remove_folder(brainstorm_path)

if __name__ == "__main__":
    pass
    #remove_brainstorm()
# %% copy all data
    copy_all_data()

# %%
