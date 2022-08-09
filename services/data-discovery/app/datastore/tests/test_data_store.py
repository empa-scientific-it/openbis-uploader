import unittest
from utils import settings, files  

import pathlib as pl
import tempfile as tf

from .. import main

def temp_yml(fc) -> pl.Path:
    with tf.NamedTemporaryFile() as ntf:
        ntf.writelines(fc)
    return pl.Path(ntf.file.name)
    


class TestSettings(unittest.TestCase):


    # def test_read_config(self):
    #     fc = \
    #     """
    #     base_path = '/tmp/'
    #     instances = ['502', '402']
    #     """
    #     ym = temp_yml(fc)
    #     settings.DataStoreSettings().parse_file(ym)

    def test_auth(self):
        app = main.app
    

TestSettings().subTest()