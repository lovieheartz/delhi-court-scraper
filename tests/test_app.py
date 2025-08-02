import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

class CourtFetcherTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        with app.app_context():
            init_db()
    
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_index_page(self):
        """Test that index page loads correctly"""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Court Data Fetcher', rv.data)
    
    def test_case_types_api(self):
        """Test case types API endpoint"""
        rv = self.app.get('/api/case-types')
        self.assertEqual(rv.status_code, 200)
        
        data = json.loads(rv.data)
        self.assertIsInstance(data, list)
        self.assertIn("CRL.A.", data)
        self.assertIn("W.P.(C)", data)
    
    def test_search_missing_fields(self):
        """Test search API with missing fields"""
        rv = self.app.post('/api/search',
                          data=json.dumps({'case_type': 'CRL.A.'}),
                          content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        
        data = json.loads(rv.data)
        self.assertIn('error', data)
        self.assertIn('All fields are required', data['error'])
    
    @patch('court_scraper.DelhiHighCourtScraper')
    def test_search_success(self, mock_scraper_class):
        """Test successful case search"""
        # Mock scraper instance
        mock_scraper = MagicMock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock successful scraping result
        mock_case_data = {
            'parties': [
                {'type': 'Petitioner', 'name': 'John Doe'},
                {'type': 'Respondent', 'name': 'State of Delhi'}
            ],
            'filing_date': '01/01/2023',
            'next_hearing_date': '15/01/2024',
            'orders': [
                {
                    'date': '01/01/2023',
                    'description': 'Case filed',
                    'pdf_url': 'http://example.com/order.pdf'
                }
            ],
            'case_status': 'Pending'
        }
        
        mock_scraper.scrape_case_data.return_value = mock_case_data
        
        # Test the API
        rv = self.app.post('/api/search',
                          data=json.dumps({
                              'case_type': 'CRL.A.',
                              'case_number': '1234',
                              'filing_year': '2023'
                          }),
                          content_type='application/json')
        
        self.assertEqual(rv.status_code, 200)
        
        data = json.loads(rv.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(len(data['data']['parties']), 2)
        self.assertEqual(data['data']['filing_date'], '01/01/2023')
    
    @patch('court_scraper.DelhiHighCourtScraper')
    def test_search_no_data(self, mock_scraper_class):
        """Test search when no case data is found"""
        mock_scraper = MagicMock()
        mock_scraper_class.return_value = mock_scraper
        mock_scraper.scrape_case_data.return_value = None
        
        rv = self.app.post('/api/search',
                          data=json.dumps({
                              'case_type': 'CRL.A.',
                              'case_number': '9999',
                              'filing_year': '2023'
                          }),
                          content_type='application/json')
        
        self.assertEqual(rv.status_code, 404)
        
        data = json.loads(rv.data)
        self.assertIn('error', data)
        self.assertIn('No case found', data['error'])
    
    def test_history_api(self):
        """Test query history API"""
        rv = self.app.get('/api/history')
        self.assertEqual(rv.status_code, 200)
        
        data = json.loads(rv.data)
        self.assertIsInstance(data, list)

class CourtScraperTestCase(unittest.TestCase):
    
    @patch('selenium.webdriver.Chrome')
    def test_scraper_initialization(self, mock_chrome):
        """Test scraper initialization"""
        from court_scraper import DelhiHighCourtScraper
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        scraper = DelhiHighCourtScraper()
        self.assertIsNotNone(scraper.driver)
        self.assertEqual(scraper.base_url, "https://delhihighcourt.nic.in")
    
    def test_parse_alternative_format(self):
        """Test alternative parsing method"""
        from court_scraper import DelhiHighCourtScraper
        from bs4 import BeautifulSoup
        
        # Mock HTML content
        html_content = """
        <table>
            <tr><td>Petitioner: John Doe</td></tr>
            <tr><td>Respondent: State of Delhi</td></tr>
            <tr><td>Filing Date: 01/01/2023</td></tr>
            <tr><td>Next Date: 15/01/2024</td></tr>
        </table>
        <a href="order.pdf">Download Order</a>
        """
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        with patch('selenium.webdriver.Chrome'):
            scraper = DelhiHighCourtScraper()
            case_data = scraper.parse_alternative_format(soup)
            
            self.assertIsInstance(case_data, dict)
            self.assertIn('parties', case_data)
            self.assertIn('filing_date', case_data)
            self.assertIn('orders', case_data)

if __name__ == '__main__':
    unittest.main()