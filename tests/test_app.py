import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

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
    
    @patch('real_court_scraper.RealDelhiCourtScraper')
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
        
        mock_scraper.scrape_real_case_data.return_value = mock_case_data
        
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
    
    @patch('real_court_scraper.RealDelhiCourtScraper')
    def test_search_no_data(self, mock_scraper_class):
        """Test search when no case data is found"""
        mock_scraper = MagicMock()
        mock_scraper_class.return_value = mock_scraper
        mock_scraper.scrape_real_case_data.side_effect = Exception("No case found")
        
        rv = self.app.post('/api/search',
                          data=json.dumps({
                              'case_type': 'CRL.A.',
                              'case_number': '9999',
                              'filing_year': '2023'
                          }),
                          content_type='application/json')
        
        self.assertEqual(rv.status_code, 200)
        
        data = json.loads(rv.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_history_api(self):
        """Test query history API"""
        rv = self.app.get('/api/history')
        self.assertEqual(rv.status_code, 200)
        
        data = json.loads(rv.data)
        self.assertIsInstance(data, list)

class SimulatedDataTestCase(unittest.TestCase):
    
    def test_simulated_data_generation(self):
        """Test simulated data generation"""
        from simulated_data import generate_simulated_case_data
        
        case_data = generate_simulated_case_data("CRL.A.", "1234", "2023")
        
        self.assertIsInstance(case_data, dict)
        self.assertIn('parties', case_data)
        self.assertIn('filing_date', case_data)
        self.assertIn('orders', case_data)
        self.assertIn('case_status', case_data)

if __name__ == '__main__':
    unittest.main()