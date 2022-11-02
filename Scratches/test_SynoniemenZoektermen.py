import unittest
from SynoniemenZoektermen import get_synoniemen

class TestWebScraper(unittest.TestCase):
    def test_get_synoniemen_dict_empty():
        zoekterm = ''
        self.assertRaises(ValueError, get_synoniemen, zoekterm)
    def test_get_synoniemen_dict_None():
        zoekterm = None
        self.assertRaises(ValueError, get_synoniemen, zoekterm)


if __name__ == '__main__':
    unittest.main()
