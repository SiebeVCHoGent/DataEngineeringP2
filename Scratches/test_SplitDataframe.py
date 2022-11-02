import unittest
import pandas as pd
from SplitDataframe import split_dataframe_in_x, save_dataframe_as_csv

class TestSplitDataframe(unittest.TestCase):
    def test_split_dataframe_in_x(self):
        df = pd.read_csv("kmos.csv", sep=",")
        df = split_dataframe_in_x(df, 5)
        self.assertEqual(len(df), 5)

    def test_split_dataframe_in_0(self):
        df = pd.read_csv("kmos.csv", sep=",")
        self.assertRaises(ValueError, split_dataframe_in_x, df, 0)

    def test_split_dataframe_in_None(self):
        df = pd.read_csv("kmos.csv", sep=",")
        self.assertRaises(ValueError, split_dataframe_in_x, df, None)

    def test_split_dataframe_in_x_is_string(self):
        df = pd.read_csv("kmos.csv", sep=",")
        self.assertRaises(ValueError, split_dataframe_in_x, df, "test")
    
    def test_split_dataframe_in_NoneDf(self):
        self.assertRaises(ValueError, split_dataframe_in_x, None, 5)
    
    def test_save_dataframe_as_csv(self):
        df = pd.read_csv("kmos.csv", sep=",")
        save_dataframe_as_csv("test.csv", df)
        self.assertTrue(True)
    
    def test_save_dataframe_as_csv_NoneDf(self):
        self.assertRaises(ValueError, save_dataframe_as_csv, "test.csv", None)
    
    def test_save_dataframe_as_csv_NoneName(self):
        df = pd.read_csv("kmos.csv", sep=",")
        self.assertRaises(ValueError, save_dataframe_as_csv, None, df)

    def test_save_dataframe_as_csv_emptyName(self):
        df = pd.read_csv("kmos.csv", sep=",")
        self.assertRaises(ValueError, save_dataframe_as_csv, "", df)
    
    def test_save_dataframe_as_csv_NoneNameAndDf(self):
        self.assertRaises(ValueError, save_dataframe_as_csv, None, None)
    


if __name__ == '__main__':
    unittest.main()