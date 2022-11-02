import unittest
from web_scraper import is_same_domain, reformat_link, remove_invalid_links, scrape_website, scrape_websites, scrape_google, read_pdf

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

    def test_reformat_link_url_domein_None(self):
        url = None
        domain = None
        self.assertRaises(ValueError, reformat_link, url, domain)
    
    def test_reformat_link_url_empty(self):
        url = ''
        domain = 'https://www.portofantwerpbruges.com'
        self.assertRaises(ValueError, reformat_link, url, domain)
    
    def test_reformat_link_domein_empty(self):
        url = '/nl/business/cargo'
        domain = ''
        self.assertRaises(ValueError, reformat_link, url, domain)
    
    def test_reformat_link_url_domein_empty(self):
        url = ''
        domain = ''
        self.assertRaises(ValueError, reformat_link, url, domain)
    
    def test_reformat_link_url_has_hash(self):
        url = '/nl/business/cargo#'
        domain = 'https://www.portofantwerpbruges.com'
        expected = 'https://www.portofantwerpbruges.com/nl/business/cargo'
        self.assertEqual(reformat_link(url, domain), expected)
    
    def test_reformat_link_url_has_questionmark(self):
        url = '/nl/business/cargo?'
        domain = 'https://www.portofantwerpbruges.com'
        expected = 'https://www.portofantwerpbruges.com/nl/business/cargo'
        self.assertEqual(reformat_link(url, domain), expected)

    def test_remove_invalid_links(self):
        links = ['/nl/business/cargo', 'https://www.portofantwerpbruges.com/nl/business/cargo']
        banned_domains = ['https://www.portofantwerpbruges.com']
        expected = ['/nl/business/cargo']
        self.assertEqual(remove_invalid_links(links, banned_domains), expected)
    
    def test_remove_invalid_links_empty(self):
        links = []
        banned_domains = ['https://www.portofantwerpbruges.com']
        expected = []
        self.assertEqual(remove_invalid_links(links, banned_domains), expected)
    
    def test_remove_invalid_links_banned_domains_empty(self):
        links = ['/nl/business/cargo', 'https://www.portofantwerpbruges.com/nl/business/cargo']
        banned_domains = []
        expected = ['/nl/business/cargo', 'https://www.portofantwerpbruges.com/nl/business/cargo']
        self.assertEqual(remove_invalid_links(links, banned_domains), expected)
    
    def test_remove_invalid_links_links_banned_domains_empty(self):
        links = []
        banned_domains = []
        expected = []
        self.assertEqual(remove_invalid_links(links, banned_domains), expected)
    
    def test_remove_invalid_links_links_None(self):
        links = None
        banned_domains = ['https://www.portofantwerpbruges.com']
        self.assertRaises(ValueError, remove_invalid_links, links, banned_domains)
    
    def test_remove_invalid_links_banned_domains_None(self):
        links = ['/nl/business/cargo', 'https://www.portofantwerpbruges.com/nl/business/cargo']
        banned_domains = None
        self.assertRaises(ValueError, remove_invalid_links, links, banned_domains)
    
    def test_remove_invalid_links_links_banned_domains_None(self):
        links = None
        banned_domains = None
        self.assertRaises(ValueError, remove_invalid_links, links, banned_domains)
    
    def test_remove_invalid_links_links_empty(self):
        links = []
        banned_domains = ['https://www.portofantwerpbruges.com']
        expected = []
        self.assertEqual(remove_invalid_links(links, banned_domains), expected)
    
    def test_scrape_google_company_name_empty(self):
        company_name = ''
        self.assertRaises(ValueError, scrape_google, company_name)
    
    def test_scrape_google_company_name_None(self):
        company_name = None
        self.assertRaises(ValueError, scrape_google, company_name)
    
    def test_scrape_google_company_location_empty(self):
        company_name = 'Port of Antwerp'
        company_location = ''
        self.assertRaises(ValueError, scrape_google, company_name, company_location)
    
    def test_scrape_google_company_location_None(self):
        company_name = 'Port of Antwerp'
        company_location = None
        self.assertRaises(ValueError, scrape_google, company_name, company_location)
    
    def test_scrape_websites_company_name_empty(self):
        company_name = ''
        self.assertRaises(ValueError, scrape_websites, company_name)


if __name__ == '__main__':
    unittest.main()
