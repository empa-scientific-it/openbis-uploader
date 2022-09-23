from pybis import Openbis
import pandas as pd
import pathlib as pl
ob = Openbis("https://localhost:8443", token=False, verify_certificates=False)
ob.login(username='basi', password='password')

def clean_names(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    return df_out.rename(lambda c: c.strip().replace(" ", "").lower().replace('-', '_').replace('.', '_'), axis="columns")  

batch_file = pl.Path(__file__).parent / 'BatchLog.csv'
transaction = ob.new_transaction()
batch_log_dt = clean_names(pd.read_csv(batch_file, encoding='latin-1'))


first_object = ob.get_samples()[0]
dataset = ob.new_dataset('RAW_DATA', object=first_object.identifier, files=[batch_file])
if dataset.sample is not None:
    ids = dataset.sample.experiment.identifier
    proj = dataset.sample.project.identifier
elif dataset.experiment is not None:
    ids = dataset.experiment.identifer
    proj = dataset.experiment.project.identifier
for row in batch_log_dt.itertuples():
    #Create metadata for each sample in the measurement log
    props = {
    "icpms.sample_name": row.samplename, 
    'icpms.acq_timestamp': row.acq_date_time, 
    'icpms.sample_type': row.sampletype,
    'icpms.acquistion_result': row.acquisitionresult,
    'icpms.operator': row.operator}

    if row.acquisitionresult != 'Skip':
        new_exp = f"/DEMO/TEST/ICP_MS_MEASUREMENTS"
        print('creating')
        sample = ob.new_object(type='ICPMS', props=props, experiment= new_exp)
        if dataset.sample is not None:
            sample.set_parents(dataset.sample.identifier)
        print('adding')
        transaction.add(sample)
        