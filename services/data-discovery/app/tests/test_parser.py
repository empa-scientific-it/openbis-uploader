from datastore.services.parsers.interfaces import OpenbisDatasetParser, process
from pybis.openbis_object import Transaction
from pybis.dataset import DataSet
from pybis import Openbis

class TestParser(OpenbisDatasetParser):
    """
    Stupid test parser
    """
    def process(self, transaction: Transaction, ob: Openbis, dataset: DataSet, a: int, b:str, c:str = 'gala') -> Transaction:
        ob.new_object('ICP-MS-MEASUREMENT', '/MEASUREMENTS/TEST/ICPMS_MEAS1', {'GAS_FLOW':1.2, 'SAMPLE_ID':a})
        return transaction 