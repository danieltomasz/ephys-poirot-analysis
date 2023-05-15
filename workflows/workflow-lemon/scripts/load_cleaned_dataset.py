# %%
import pandas as pd
from IPython.display import display


DATA_FOLDER = '~/PhD/Projects/ephys-poirot-analysis/workflows/workflow-lemon/data'

df = pd.read_csv(f'{DATA_FOLDER}/processed/Sonia_2023-04-23.csv')
# %%
display(df.head())
# %%
