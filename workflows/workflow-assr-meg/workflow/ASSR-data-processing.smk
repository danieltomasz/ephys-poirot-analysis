# Define the global Conda environment
conda: "conda-poirot-3.10"

SUBS = ["Subject01_A", "Subject01_B", "Subject02_A", "Subject02_B", "Subject03_A", "Subject03_B", "Subject04_A", "Subject04_B", "Subject05_A", "Subject05_B", "Subject06_A", "Subject06_B", "Subject07_A", "Subject07_B", "Subject08_A", "Subject08_B", "Subject09_A", "Subject09_B", "Subject10_A", "Subject10_B", "Subject11_A", "Subject11_B", "Subject12_A", "Subject12_B", "Subject13_A", "Subject13_B", "Subject14_A", "Subject14_B", "Subject15_A", "Subject15_B"]

DATA_FOLDER = "/Volumes/ExtremePro/Analyses/tDCS_MEG"
ASSR_XARRAY_SCRIPT = "scripts/assr/01_assr_to_xarray.py"

rule all:
    input:
        expand(f"{DATA_FOLDER}/interim/timeseries/{{sub}}_MEG_ASSR_times.nc", sub=SUBS)

rule process_data:
    output:
        out_file = f"{DATA_FOLDER}/interim/timeseries/{{sub}}_MEG_ASSR_times.nc"
    params:
        sub = "{sub}",
        script = ASSR_XARRAY_SCRIPT 
    shell:
        """
        python {params.script} -o {output.out_file}
        """