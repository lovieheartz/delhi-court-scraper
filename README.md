# Court Data Fetcher & Mini-Dashboard

A comprehensive web application for fetching and displaying case information from the Delhi High Court. This application provides a user-friendly interface to search for case details, view parties information, important dates, and download court orders/judgments.

## 🏛️ Court Targeted

**Delhi High Court** (https://delhihighcourt.nic.in/)

This application specifically targets the Delhi High Court's case status system, providing access to case information through automated web scraping with intelligent CAPTCHA handling.

## ✨ Features

- **Case Search**: Search by Case Type, Case Number, and Filing Year
- **Comprehensive Data**: Extract parties' names, filing dates, next hearing dates, and case status
- **Document Access**: Download PDF orders and judgments
- **Query Logging**: All searches are logged in SQLite database with timestamps
- **Search History**: View recent searches with status indicators
- **Error Handling**: User-friendly error messages for invalid cases or site issues
- **Responsive UI**: Modern, mobile-friendly interface
- **CAPTCHA Bypass**: Automated CAPTCHA solving using OCR technology

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Chrome/Chromium browser
- Tesseract OCR

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/court-data-fetcher.git
   cd court-data-fetcher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open http://localhost:5000 in your browser

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Using Docker directly

```bash
# Build the image
docker build -t court-fetcher .

# Run the container
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data court-fetcher
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Flask secret key | `your-secret-key-here` |
| `DATABASE_URL` | Database connection string | `sqlite:///court_data.db` |
| `HEADLESS_MODE` | Run browser in headless mode | `True` |
| `CAPTCHA_RETRY_ATTEMPTS` | Number of CAPTCHA retry attempts | `3` |
| `REQUEST_TIMEOUT` | HTTP request timeout (seconds) | `30` |

### Supported Case Types

- CRL.A. (Criminal Appeal)
- CRL.REV.P. (Criminal Revision Petition)
- CRL.M.C. (Criminal Miscellaneous)
- W.P.(C) (Writ Petition Civil)
- W.P.(CRL) (Writ Petition Criminal)
- FAO (First Appeal from Order)
- RFA (Regular First Appeal)
- CS(OS) (Civil Suit Original Side)
- CS(COMM) (Commercial Suit)
- ARB.P. (Arbitration Petition)
- CONT.CAS(C) (Contempt Case Civil)
- CRL.O.P. (Criminal Original Petition)
- BAIL APPLN. (Bail Application)
- CRL.BAIL (Criminal Bail)
- CRL.MISC. (Criminal Miscellaneous)
- MAT.APP. (Matrimonial Appeal)

## 🤖 CAPTCHA Strategy

The application employs a multi-layered approach to handle CAPTCHAs:

### 1. OCR-Based Solution
- **Primary Method**: Uses Tesseract OCR with image preprocessing
- **Image Enhancement**: Grayscale conversion, upscaling, and noise reduction
- **Character Recognition**: Optimized for alphanumeric CAPTCHAs
- **Success Rate**: ~70-80% for simple text-based CAPTCHAs

### 2. Retry Mechanism
- **Multiple Attempts**: Up to 3 retry attempts per search
- **Fresh CAPTCHA**: Refreshes page to get new CAPTCHA on failure
- **Graceful Degradation**: Clear error messages when all attempts fail

### 3. Future Enhancements
- Integration with CAPTCHA-solving services (2captcha, Anti-Captcha)
- Machine learning models for better recognition
- Manual CAPTCHA input option for complex cases

## 📊 Database Schema

### Queries Table
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT NOT NULL,
    case_number TEXT NOT NULL,
    filing_year TEXT NOT NULL,
    query_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_data TEXT,
    status TEXT,
    error_message TEXT
);
```

### Case Data Table
```sql
CREATE TABLE case_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type TEXT NOT NULL,
    case_number TEXT NOT NULL,
    filing_year TEXT NOT NULL,
    parties_names TEXT,
    filing_date TEXT,
    next_hearing_date TEXT,
    orders_data TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/ -v
```

### Run with Coverage
```bash
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Test Categories
- **API Tests**: Flask endpoint functionality
- **Scraper Tests**: Web scraping logic
- **Database Tests**: Data persistence and retrieval
- **Integration Tests**: End-to-end workflows

## 📁 Project Structure

```
court-data-fetcher/
├── app.py                 # Main Flask application
├── court_scraper.py       # Web scraping logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example          # Environment variables template
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Main UI template
├── tests/
│   └── test_app.py       # Unit tests
├── .github/
│   └── workflows/
│       └── ci.yml        # CI/CD pipeline
├── data/                 # SQLite database storage
└── logs/                 # Application logs
```

## 🔒 Security Considerations

### Data Protection
- No sensitive user data is stored
- All queries are logged for debugging purposes only
- PDF downloads are proxied through the application

### Web Scraping Ethics
- Respects robots.txt guidelines
- Implements reasonable delays between requests
- Uses public APIs where available
- Complies with court website terms of service

### Input Validation
- Sanitizes all user inputs
- Validates case numbers and years
- Prevents SQL injection attacks
- Implements CSRF protection

## 🚦 API Endpoints

### GET /
- **Description**: Main application interface
- **Response**: HTML page

### GET /api/case-types
- **Description**: Get available case types
- **Response**: JSON array of case types

### POST /api/search
- **Description**: Search for case information
- **Request Body**:
  ```json
  {
    "case_type": "CRL.A.",
    "case_number": "1234",
    "filing_year": "2023"
  }
  ```
- **Response**: Case data or error message

### GET /api/download-pdf/<path:pdf_url>
- **Description**: Download PDF documents
- **Response**: PDF file or error message

### GET /api/history
- **Description**: Get search history
- **Response**: JSON array of recent searches

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Update Chrome driver
   pip install --upgrade webdriver-manager
   ```

2. **CAPTCHA Recognition Failures**
   ```bash
   # Install/update Tesseract
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   ```

3. **Database Permissions**
   ```bash
   # Ensure write permissions
   chmod 755 data/
   ```

4. **Port Already in Use**
   ```bash
   # Kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

### Debug Mode

Enable debug logging by setting:
```bash
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
```

## 📈 Performance Optimization

### Caching Strategy
- Case data caching for repeated searches
- PDF download caching
- Database query optimization

### Scalability Considerations
- Horizontal scaling with load balancers
- Database migration to PostgreSQL for production
- Redis for session management and caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Delhi High Court for providing public access to case information
- Selenium and BeautifulSoup communities for excellent web scraping tools
- Tesseract OCR project for CAPTCHA recognition capabilities
- Flask community for the robust web framework

## 📞 Support

For support, email rehanfarooque51@gmail.com or create an issue in the GitHub repository.

## 🔄 Version History

- **v1.0.0** - Initial release with basic functionality
- **v1.1.0** - Added CAPTCHA handling and PDF downloads
- **v1.2.0** - Implemented search history and improved UI
- **v1.3.0** - Added Docker support and CI/CD pipeline

---

**Note**: This application is for educational and research purposes. Please ensure compliance with the court website's terms of service and applicable laws when using this tool.