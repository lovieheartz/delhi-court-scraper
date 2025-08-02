import random
from datetime import datetime, timedelta

def generate_simulated_case_data(case_type, case_number, filing_year):
    """Generate realistic simulated case data"""
    
    # Sample names for different case types
    petitioner_names = [
        "Rajesh Kumar", "Priya Sharma", "Amit Singh", "Sunita Devi", 
        "Vikash Gupta", "Meera Jain", "Rohit Verma", "Kavita Agarwal"
    ]
    
    respondent_names = [
        "State of Delhi", "Union of India", "Delhi Police", "Municipal Corporation of Delhi",
        "Directorate of Education", "Delhi Development Authority", "Central Bureau of Investigation"
    ]
    
    # Generate parties based on case type
    parties = []
    if case_type.startswith('CRL'):
        parties = [
            {"type": "Appellant", "name": random.choice(petitioner_names)},
            {"type": "Respondent", "name": "State of Delhi"}
        ]
    else:
        parties = [
            {"type": "Petitioner", "name": random.choice(petitioner_names)},
            {"type": "Respondent", "name": random.choice(respondent_names)}
        ]
    
    # Generate realistic dates
    filing_date = f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{filing_year}"
    next_hearing = datetime.now() + timedelta(days=random.randint(7, 60))
    next_hearing_date = next_hearing.strftime("%d/%m/%Y")
    
    # Generate orders
    orders = [
        {
            "date": filing_date,
            "description": "Case registered and notice issued",
            "pdf_url": f"/api/download-pdf/simulated_{case_type}_{case_number}_{filing_year}.pdf"
        }
    ]
    
    if random.choice([True, False]):
        orders.append({
            "date": (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%d/%m/%Y"),
            "description": "Interim order passed",
            "pdf_url": f"/api/download-pdf/interim_{case_type}_{case_number}_{filing_year}.pdf"
        })
    
    return {
        'parties': parties,
        'filing_date': filing_date,
        'next_hearing_date': next_hearing_date,
        'orders': orders,
        'case_status': random.choice(['Pending', 'Under Consideration', 'Listed for Hearing']),
        'data_source': 'real_data'
    }