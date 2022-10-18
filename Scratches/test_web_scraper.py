import unittest
from web_scraper import is_same_domain, reformat_link

class TestWebScraper(unittest.TestCase):
    def test_same_domain_True(self):
        url1 = 'https://www.google.com'
        url2 = 'https://www.google.com/info'

        self.assertTrue(is_same_domain(url1, url2))

    def test_same_domain_False(self):
        url1 = 'https://www.google.com'
        url2 = 'https://www.facebook.com/info'

        self.assertFalse(is_same_domain(url1, url2))

    def test_same_domain_One_(self):
        url1 = 'https://www.google.com'
        url2 = ''

        self.assertFalse(is_same_domain(url1, url2))

    def test_same_domain_One_None(self):
        url1 = 'https://www.google.com'
        url2 = None

        self.assertFalse(is_same_domain(url1, url2))

    def test_reformat_link(self):
        url = '/nl/business/cargo'
        domain = 'https://www.portofantwerpbruges.com'
        expected = 'https://www.portofantwerpbruges.com/nl/business/cargo'
        self.assertEqual(reformat_link(url, domain), expected)

    def test_reformat_link_url_None(self):
        url = None
        domain = 'https://www.portofantwerpbruges.com'
        self.assertRaises(ValueError, reformat_link, url, domain)

    def test_reformat_link_domein_None(self):
        url = '/nl/business/cargo'
        domain = None
        self.assertRaises(ValueError, reformat_link, url, domain)



if __name__ == '__main__':
    unittest.main()
