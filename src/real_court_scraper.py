import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from urllib.parse import urljoin
import json

logger = logging.getLogger(__name__)

class RealDelhiCourtScraper:
    def __init__(self):
        self.base_url = "https://delhihighcourt.nic.in"
        self.search_url = "https://delhihighcourt.nic.in/dhcqrydisp_o.asp"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_captcha_and_form_data(self):
        """Get form data and attempt CAPTCHA bypass"""
        try:
            # Try multiple URLs
            urls_to_try = [
                "https://delhihighcourt.nic.in/case_status.asp",
                "https://delhihighcourt.nic.in/case_status",
                "https://delhihighcourt.nic.in/casestatus.asp",
                "https://delhihighcourt.nic.in/"
            ]
            
            response = None
            working_url = None
            
            for url in urls_to_try:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        working_url = url
                        self.search_url = url
                        break
                except:
                    continue
            
            if not response or response.status_code != 200:
                raise Exception(f"Court website not accessible - all URLs failed")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find form elements
            form_data = {}
            
            # Get all input fields
            inputs = soup.find_all('input')
            for inp in inputs:
                name = inp.get('name')
                value = inp.get('value', '')
                if name:
                    form_data[name] = value
            
            # Get select options
            selects = soup.find_all('select')
            for select in selects:
                name = select.get('name')
                if name:
                    options = select.find_all('option')
                    if options:
                        form_data[name] = options[0].get('value', '')
            
            return form_data, soup
            
        except Exception as e:
            logger.error(f"Error getting form data: {str(e)}")
            raise
    
    def solve_simple_captcha(self, soup):
        """Attempt to solve simple text-based CAPTCHA"""
        try:
            # Look for CAPTCHA image
            captcha_img = soup.find('img', src=re.compile(r'captcha', re.IGNORECASE))
            if not captcha_img:
                return "BYPASS"
            
            # Try to get CAPTCHA image
            captcha_src = captcha_img.get('src')
            if captcha_src:
                captcha_url = urljoin(self.base_url, captcha_src)
                
                # Download CAPTCHA image
                img_response = self.session.get(captcha_url, timeout=10)
                if img_response.status_code == 200:
                    # Simple pattern matching for common CAPTCHAs
                    # This is a basic approach - in production, use OCR or CAPTCHA service
                    
                    # Try common CAPTCHA patterns
                    common_captchas = ["12345", "ABCDE", "TEST", "DEMO", "COURT"]
                    return common_captchas[0]  # Return first attempt
            
            return "BYPASS"
            
        except Exception as e:
            logger.warning(f"CAPTCHA solving failed: {str(e)}")
            return "BYPASS"
    
    def scrape_real_case_data(self, case_type, case_number, filing_year):
        """Scrape actual case data from Delhi High Court"""
        try:
            logger.info(f"Attempting real scrape: {case_type} {case_number}/{filing_year}")
            
            # Try multiple working URLs for Delhi High Court
            working_urls = [
                "https://delhihighcourt.nic.in/dhcqrydisp_o.asp",
                "https://delhihighcourt.nic.in/dhcqrydisp.asp", 
                "https://delhihighcourt.nic.in/case_status.asp",
                "https://delhihighcourt.nic.in/"
            ]
            
            case_status_response = None
            working_url = None
            
            for url in working_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200 and ('case' in response.text.lower() or 'search' in response.text.lower()):
                        case_status_response = response
                        working_url = url
                        self.search_url = url
                        break
                except:
                    continue
            
            if not case_status_response:
                raise Exception("Delhi High Court case search page not accessible")
            
            soup = BeautifulSoup(case_status_response.content, 'html.parser')
            
            # Try direct parameter approach first
            search_params = {
                'case_type': case_type,
                'case_no': case_number, 
                'case_year': filing_year,
                'submit': 'Submit'
            }
            
            # Try GET request with parameters
            search_response = self.session.get(
                working_url,
                params=search_params,
                timeout=15
            )
            
            if search_response.status_code == 200:
                result = self.parse_real_results(search_response.content, case_type, case_number, filing_year)
                if result:
                    return result
            
            # If GET fails, try POST with form data
            form_data = search_params.copy()
            
            # Add any hidden form fields
            for input_tag in soup.find_all('input', type='hidden'):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    form_data[name] = value
            
            # Submit POST request
            search_response = self.session.post(
                working_url,
                data=form_data,
                timeout=15
            )
            
            if search_response.status_code != 200:
                raise Exception(f"Court website returned error {search_response.status_code}")
            
            return self.parse_real_results(search_response.content, case_type, case_number, filing_year)
            
        except Exception as e:
            logger.error(f"Real scraping failed: {str(e)}")
            raise Exception(f"Unable to extract real data: {str(e)}")
    
    def parse_real_results(self, html_content, case_type, case_number, filing_year):
        """Parse actual court website results - ONLY REAL DATA"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for error messages
            if any(phrase in page_text for phrase in ['no record found', 'no case found', 'invalid captcha', 'captcha mismatch']):
                raise Exception("No case found with provided details")
            
            # Check if CAPTCHA is blocking us
            if 'captcha' in page_text and 'enter' in page_text:
                raise Exception("CAPTCHA protection is blocking access to real data")
            
            # Look for actual case data indicators
            has_case_data = any(word in page_text for word in [
                'petitioner', 'respondent', 'appellant', 'case no', 'filing date', 
                'next date', 'hearing', 'order', 'judgment'
            ])
            
            if not has_case_data:
                raise Exception("No real case data found - website may require authentication")
            
            case_data = {
                'parties': [],
                'filing_date': '',
                'next_hearing_date': '',
                'orders': [],
                'case_status': '',
                'data_source': 'real_scraped'
            }
            
            # Extract real data from tables
            tables = soup.find_all('table')
            data_found = False
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if value and value != '-' and len(value) > 1:
                            data_found = True
                            
                            if any(word in label for word in ['petitioner', 'appellant']):
                                case_data['parties'].append({
                                    'type': 'Petitioner/Appellant',
                                    'name': value
                                })
                            elif 'respondent' in label:
                                case_data['parties'].append({
                                    'type': 'Respondent',
                                    'name': value
                                })
                            elif 'filing' in label and 'date' in label:
                                case_data['filing_date'] = value
                            elif 'next' in label and 'date' in label:
                                case_data['next_hearing_date'] = value
                            elif 'status' in label:
                                case_data['case_status'] = value
            
            # Extract real PDF links
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf', re.IGNORECASE))
            for link in pdf_links:
                href = link.get('href')
                if href and 'order' in href.lower():
                    data_found = True
                    case_data['orders'].append({
                        'date': '',
                        'description': link.get_text(strip=True) or 'Court Order',
                        'pdf_url': href if href.startswith('http') else f"{self.base_url}{href}"
                    })
            
            if not data_found:
                raise Exception("No real case data extracted from website response")
            
            # Only return if we have actual data
            if case_data['parties'] or case_data['orders'] or case_data['filing_date']:
                return case_data
            else:
                raise Exception("Real data extraction failed - no valid case information found")
                
        except Exception as e:
            logger.error(f"Real data parsing failed: {str(e)}")
            raise
    
    def download_real_pdf(self, pdf_url):
        """Download actual PDF from court website"""
        try:
            response = self.session.get(pdf_url, timeout=30)
            if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                return response.content
            return None
        except Exception as e:
            logger.error(f"PDF download failed: {str(e)}")
            return None