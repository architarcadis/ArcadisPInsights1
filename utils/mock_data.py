import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_mock_spend_data():
    """Generate mock spend data for demonstration purposes"""
    # Define constants for mock data
    suppliers = [
        "Supplier Alpha", "Supplier Beta", "Supplier Gamma", 
        "Supplier Delta", "Supplier Epsilon", "Supplier Zeta",
        "Supplier Eta", "Supplier Theta", "Supplier Iota",
        "Supplier Kappa", "Supplier Lambda", "Supplier Mu",
        "Supplier Nu", "Supplier Xi", "Supplier Omicron"
    ]
    
    categories = [
        "Category A", "Category B", "Category C", "Category D", 
        "Category E", "Category F", "Category G",
        "Category H", "Equipment", "Safety Products"
    ]
    
    subcategories = {
        "Category A": ["Type A1", "Type A2", "Type A3", "Type A4", "Type A5"],
        "Category B": ["Type B1", "Type B2", "Type B3", "Type B4", "Type B5"],
        "Category C": ["Type C1", "Type C2", "Type C3", "Type C4", "Type C5"],
        "Category D": ["Type D1", "Type D2", "Type D3", "Type D4", "Type D5"],
        "Category E": ["Type E1", "Type E2", "Type E3", "Type E4", "Type E5"],
        "Category F": ["Type F1", "Type F2", "Type F3", "Type F4", "Type F5"],
        "Category G": ["Type G1", "Type G2", "Type G3", "Type G4", "Type G5"],
        "Category H": ["Type H1", "Type H2", "Type H3", "Type H4", "Type H5"],
        "Equipment": ["Equipment Type 1", "Equipment Type 2", "Equipment Type 3", "Equipment Type 4", "Equipment Type 5"],
        "Safety Products": ["Safety Item 1", "Safety Item 2", "Safety Item 3", "Safety Item 4", "Safety Item 5"]
    }
    
    business_units = ["Division A", "Division B", "Division C", "Division D", "Division E", "Division F", "Division G"]
    
    # Generate dates for the last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate 500 random transactions
    num_transactions = 500
    data = []
    
    for _ in range(num_transactions):
        supplier = random.choice(suppliers)
        category = random.choice(categories)
        subcategory = random.choice(subcategories[category])
        business_unit = random.choice(business_units)
        date = random.choice(date_range)
        
        # Generate amount based on category (specific spend patterns)
        base_amount = {
            "Category A": 15000,
            "Category B": 12000,
            "Category C": 8000,
            "Category D": 18000,
            "Category E": 25000,
            "Category F": 9000,
            "Category G": 22000,
            "Category H": 7500,
            "Equipment": 14000,
            "Safety Products": 5000
        }
        
        amount = random.uniform(0.5, 1.5) * base_amount[category]
        
        # Add random invoice and PO numbers
        invoice_id = f"INV-{random.randint(10000, 99999)}"
        po_id = f"PO-{random.randint(10000, 99999)}"
        
        data.append({
            "Supplier": supplier,
            "Category": category,
            "SubCategory": subcategory,
            "BusinessUnit": business_unit,
            "Date": date,
            "Amount": round(amount, 2),
            "InvoiceID": invoice_id,
            "POID": po_id,
            "PaymentTerms": random.choice(["Net 30", "Net 45", "Net 60"]),
            "Currency": "USD"
        })
    
    return pd.DataFrame(data)

def get_mock_supplier_data():
    """Generate mock supplier data for demonstration purposes"""
    # Define constants for suppliers
    suppliers = [
        {"name": "Supplier Alpha", "category": "Category E", "country": "USA", "city": "Chicago", "lat": 41.8781, "lon": -87.6298},
        {"name": "Supplier Beta", "category": "Category B", "country": "France", "city": "Paris", "lat": 48.8566, "lon": 2.3522},
        {"name": "Supplier Gamma", "category": "Category E", "country": "Germany", "city": "Berlin", "lat": 52.5200, "lon": 13.4050},
        {"name": "Supplier Delta", "category": "Category D", "country": "USA", "city": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Supplier Epsilon", "category": "Category D", "country": "USA", "city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"name": "Supplier Zeta", "category": "Category D", "country": "Japan", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
        {"name": "Supplier Eta", "category": "Category E", "country": "USA", "city": "Miami", "lat": 25.7617, "lon": -80.1918},
        {"name": "Supplier Theta", "category": "Category B", "country": "Switzerland", "city": "Zurich", "lat": 47.3769, "lon": 8.5417},
        {"name": "Supplier Iota", "category": "Category C", "country": "Finland", "city": "Helsinki", "lat": 60.1699, "lon": 24.9384},
        {"name": "Supplier Kappa", "category": "Category C", "country": "USA", "city": "Atlanta", "lat": 33.7490, "lon": -84.3880},
        {"name": "Supplier Lambda", "category": "Category C", "country": "Germany", "city": "Munich", "lat": 48.1351, "lon": 11.5820},
        {"name": "Supplier Mu", "category": "Category A", "country": "Denmark", "city": "Copenhagen", "lat": 55.6761, "lon": 12.5683},
        {"name": "Supplier Nu", "category": "Category B", "country": "Ireland", "city": "Dublin", "lat": 53.3498, "lon": -6.2603},
        {"name": "Supplier Xi", "category": "Category F", "country": "USA", "city": "Boston", "lat": 42.3601, "lon": -71.0589},
        {"name": "Supplier Omicron", "category": "Category D", "country": "Japan", "city": "Osaka", "lat": 34.6937, "lon": 135.5023},
    ]
    
    data = []
    
    for i, supplier in enumerate(suppliers):
        # Generate a supplier ID
        supplier_id = f"S{str(i+1).zfill(4)}"
        
        # Generate contact information
        contact_name = f"{random.choice(['John', 'Jane', 'Robert', 'Mary', 'David', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller'])}"
        contact_email = f"{contact_name.lower().replace(' ', '.')}@{supplier['name'].lower().replace(' ', '')}.com"
        contact_phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Generate financial details
        annual_revenue = random.randint(1, 50) * 1000000
        
        # Generate performance metrics
        payment_terms = random.choice(["Net 30", "Net 45", "Net 60"])
        
        data.append({
            "SupplierID": supplier_id,
            "SupplierName": supplier["name"],
            "Category": supplier["category"],
            "Country": supplier["country"],
            "City": supplier["city"],
            "Latitude": supplier["lat"],
            "Longitude": supplier["lon"],
            "ContactName": contact_name,
            "ContactEmail": contact_email,
            "ContactPhone": contact_phone,
            "AnnualRevenue": annual_revenue,
            "PaymentTerms": payment_terms,
            "Active": True,
            "RelationshipStartDate": f"{random.randint(2010, 2021)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        })
    
    return pd.DataFrame(data)

def get_mock_contract_data():
    """Generate mock contract data for demonstration purposes"""
    # Base the contracts on the supplier data
    supplier_data = get_mock_supplier_data()
    
    data = []
    
    # Current date for reference
    current_date = datetime.now()
    
    # Create 2-3 contracts per supplier
    for _, supplier in supplier_data.iterrows():
        num_contracts = random.randint(1, 3)
        
        for j in range(num_contracts):
            # Generate contract ID
            contract_id = f"C{supplier['SupplierID'][1:]}{j+1}"
            
            # Contract type based on construction industry needs
            contract_type = random.choice(["Equipment", "Service & Maintenance", "Installation", "System Integration", "Parts & Materials", "Design Services"])
            
            # Generate start and end dates
            years_ago = random.randint(0, 3)
            months_ago = random.randint(0, 11)
            start_date = current_date - timedelta(days=365*years_ago + 30*months_ago)
            
            duration_years = random.randint(1, 5)
            end_date = start_date + timedelta(days=365*duration_years)
            
            # Format dates as strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Generate contract value
            base_value = random.randint(10000, 1000000)
            value = round(base_value, -3)  # Round to nearest thousand
            
            # Status based on end date
            if end_date < current_date:
                status = "Expired"
            elif start_date > current_date:
                status = "Future"
            else:
                status = "Active"
            
            # Auto-renewal
            auto_renewal = random.choice([True, False])
            
            # Notice period
            notice_period_days = random.choice([30, 60, 90])
            
            data.append({
                "ContractID": contract_id,
                "SupplierID": supplier["SupplierID"],
                "SupplierName": supplier["SupplierName"],
                "Category": supplier["Category"],
                "ContractType": contract_type,
                "StartDate": start_date_str,
                "EndDate": end_date_str,
                "Value": value,
                "Currency": "USD",
                "Status": status,
                "AutoRenewal": auto_renewal,
                "NoticePeriodDays": notice_period_days
            })
    
    return pd.DataFrame(data)

def get_mock_performance_data():
    """Generate mock supplier performance data for demonstration purposes"""
    # Base the performance data on the supplier data
    supplier_data = get_mock_supplier_data()
    
    data = []
    
    # Generate performance data for the last 8 quarters
    quarters = ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4", 
                "2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4"]
    
    for _, supplier in supplier_data.iterrows():
        for quarter in quarters:
            # Generate random scores with some correlation between quarters
            if quarter == quarters[0]:
                # First quarter scores are completely random
                delivery_score = round(random.uniform(5.0, 10.0), 1)
                quality_score = round(random.uniform(5.0, 10.0), 1)
                responsiveness_score = round(random.uniform(5.0, 10.0), 1)
            else:
                # Subsequent quarters are somewhat correlated with the previous
                prev_data = [d for d in data if d["SupplierID"] == supplier["SupplierID"] and d["Quarter"] == quarters[quarters.index(quarter)-1]]
                if prev_data:
                    prev = prev_data[0]
                    # Score fluctuates by up to ±1.5 points
                    delivery_score = round(max(1, min(10, prev["DeliveryScore"] + random.uniform(-1.5, 1.5))), 1)
                    quality_score = round(max(1, min(10, prev["QualityScore"] + random.uniform(-1.5, 1.5))), 1)
                    responsiveness_score = round(max(1, min(10, prev["ResponsivenessScore"] + random.uniform(-1.5, 1.5))), 1)
                else:
                    # Fallback if previous quarter data is missing
                    delivery_score = round(random.uniform(5.0, 10.0), 1)
                    quality_score = round(random.uniform(5.0, 10.0), 1)
                    responsiveness_score = round(random.uniform(5.0, 10.0), 1)
            
            # Calculate overall score as weighted average
            overall_score = round((delivery_score * 0.4 + quality_score * 0.4 + responsiveness_score * 0.2), 1)
            
            data.append({
                "SupplierID": supplier["SupplierID"],
                "Quarter": quarter,
                "DeliveryScore": delivery_score,
                "QualityScore": quality_score,
                "ResponsivenessScore": responsiveness_score,
                "OverallScore": overall_score,
                "Comments": generate_performance_comment(overall_score)
            })
    
    return pd.DataFrame(data)

def generate_performance_comment(score):
    """Generate a performance comment based on the overall score"""
    if score >= 9.0:
        return random.choice([
            "Exceptional installation quality and project delivery.",
            "Outstanding compliance with specifications and industry standards.",
            "Excellent coordination with other departments and project teams.",
            "Superior technical expertise and system implementation.",
            "Exceptional safety record and quality control procedures."
        ])
    elif score >= 8.0:
        return random.choice([
            "Very good system performance with minor commissioning adjustments needed.",
            "Strong technical documentation and as-built drawings provided.",
            "Consistently good coordination with project schedule requirements.",
            "Reliable equipment quality with good warranty support.",
            "Effective project management with good communication."
        ])
    elif score >= 7.0:
        return random.choice([
            "Good installation quality with some minor rework required.",
            "Satisfactory adherence to specifications with occasional clarifications needed.",
            "Meets expectations for system performance with some optimization potential.",
            "Generally reliable on schedule with occasional delays.",
            "Acceptable safety procedures with room for improvement."
        ])
    elif score >= 5.0:
        return random.choice([
            "Average installation quality with several deficiencies requiring correction.",
            "Some technical issues with equipment and system integration.",
            "Performance below target on project schedule adherence.",
            "Multiple RFIs and change orders requiring attention.",
            "Quality inconsistencies between different installation areas."
        ])
    else:
        return random.choice([
            "Significant system performance issues requiring remediation.",
            "Multiple code compliance and specification deviation issues.",
            "Substantial delays impacting overall project schedule.",
            "Poor coordination with other trades causing conflicts.",
            "Serious quality control and safety procedure concerns."
        ])
