from datastore.services.parsers.interfaces import OpenbisDatasetParser
import pathlib as pl
from tkinter.ttk import Separator
import pandas as pd
import argparse as ap
import matplotlib as mpl
import matplotlib.figure as mpf
import dataclasses
from pydantic import BaseModel, fields
import datetime as dt
from pybis import Openbis 
from pybis.openbis_object import Transaction
from pybis.dataset import DataSet

class AdministrativeInformation(BaseModel):
    exported: dt.datetime = fields.Field(alias='Export Date')
    locale: str = fields.Field(alias='Culture')
    separator: str = fields.Field(alias='Decimal separator')
    workspace: str = fields.Field(alias='Workspace name')
    workspace_path: pl.Path = fields.Field(alias='Workspace path')
    file: str = fields.Field(alias='File name')


def find_metadata(header: str, data: pd.DataFrame) -> pd.DataFrame:
    """
    Given the header, finds the block of data containing the desired 
    metadata
    """
    start_row = (data.iloc[:, 0] == header).idxmax()
    end_row = (data.iloc[start_row:, 0].isna()).idxmax()
    block = data.iloc[(start_row + 1):end_row, :]
    block_names = block.iloc[0, :]
    block_data = block.iloc[1:, :]
    block_data.rename(
        columns={idx: val for idx, val in enumerate(block_names.to_list())})
    return block_data



def import_gcp_data(path: pl.Path) -> pd.DataFrame:
    raw_data = pd.read_excel(path, sheet_name=1, header=None)
    detector_metadata = find_metadata("Sample Channel Information", raw_data)
    start_row = (raw_data.iloc[:, 0] == 'Raw Data').idxmax() + 1
    raw_data_plot = raw_data.iloc[start_row:, :]
    raw_data_names = raw_data_plot.iloc[0, :]
    raw_data_values = raw_data_plot.iloc[1:, :]
    return raw_data_values.rename(columns=lambda x:  detector_metadata.iloc[x-1, 1] if x > 0 else 'RT')


def plot_gcp_data(fig: mpf.Figure, dt: pd.DataFrame) -> mpf.Figure:
    gs = fig.add_gridspec(2, 2)
    for i in range(1, 5):
        ax = fig.add_subplot(gs[i-1])
        ax.plot(dt['RT'], dt.iloc[:, i])
        ax.set_ylabel(dt.columns[i])
        ax.set_xlabel(dt.columns[0])
    return fig



class GCPParser(OpenbisDatasetParser):
    """
    This parser extract plots from GCP data
    """
    def process(self, ob: Openbis, transaction: Transaction, dataset: DataSet, *args, **kwargs) -> Transaction:
        return super().process(ob, transaction, dataset, *args, **kwargs)



