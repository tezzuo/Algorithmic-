import unittest

import pandas as pd

from src.util.read_file import read_file

class TestReadFile(unittest.TestCase):

    def test_read_csv(self):
        file_path = '../data/sp500_adj_close_prices.csv'
        data = read_file(file_path)
        self.assertIsInstance(data, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
