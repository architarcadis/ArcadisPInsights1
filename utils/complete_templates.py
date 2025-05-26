import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime, timedelta
import random
import csv
import os

def generate_spend_data_template():
    """Generate a comprehensive spend data template with all required fields"""
    
    # Define column headers
    headers = [
        "Supplier", "SupplierID", "Category", "SubCategory", "BusinessUnit", 
        "Date", "Amount", "InvoiceID", "POID", "PaymentTerms", "Currency",
        "ContractID", "Region", "RiskScore", "SavingsOpportunity"
    ]
    
    # Define sample data ranges
    categories = [
        "Infrastructure & Assets", "Technology & IT", "Professional & Consultancy Services", 
        "Operational Consumables", "Business Services", "Utilities & Energy",
        "Fleet & Logistics", "Maintenance & Repair"
    ]
    
    subcategories = {
        "Infrastructure & Assets": ["Pipeline Renewal", "Treatment Plant Upgrades", "New Connections", "Reservoir Construction"],
        "Technology & IT": ["Cloud Hosting", "Cybersecurity Services", "SCADA Systems", "Billing Software Licenses", "Data Analytics Platforms"],
        "Professional & Consultancy Services": ["Engineering Design", "Legal Counsel", "Financial Audit", "Environmental Impact Assessment", "Leakage Consultancy"],
        "Operational Consumables": ["Water Treatment Chemicals", "Office Supplies", "Pipe Fittings", "Safety Equipment"],
        "Business Services": ["HR & Payroll Services", "Training & Development", "Customer Call Centre Services"],
        "Utilities & Energy": ["Electricity", "Renewable Energy Generation"],
        "Fleet & Logistics": ["Vehicle Maintenance", "Fuel Costs", "Equipment Rental", "Logistics & Haulage"],
        "Maintenance & Repair": ["Scheduled Maintenance Works", "Emergency Repairs", "Equipment Servicing"]
    }
    
    business_units = [
        "Water Production & Treatment", "Wastewater Collection & Treatment", 
        "Network Operations & Maintenance", "Customer Operations & Retail",
        "IT & Digital Transformation", "Human Resources", "Finance & Regulation",
        "Procurement & Supply Chain", "Strategic Resource Planning", 
        "Capital Delivery Programmes", "Asset Management Strategy", "Health, Safety & Environment"
    ]
    
    regions = ["North", "South", "East", "West", "Central", "International"]
    
    payment_terms = ["Net 30", "Net 45", "Net 60", "Net 90"]
    currencies = ["GBP", "USD", "EUR"]
    
    # Generate supplier names and IDs
    base_names = [
        "Aqua", "Hydro", "Flow", "Pipe", "Clear", "Thames", "Severn", "Kennet", 
        "Southern", "UK", "London", "Tech", "Digital", "Cyber", "Data", "Enviro", "Chem"
    ]
    
    suffixes = [
        "Solutions", "Systems", "Ltd", "Group", "PLC", "Services", "Engineering", 
        "Technologies", "Dynamics", "Partners", "Consulting", "Advisory", "Water", 
        "Utilities", "Tech"
    ]
    
    supplier_names = []
    for i in range(50):
        # Create a mix of single company names and hyphenated names
        if random.random() < 0.5:
            name = f"{random.choice(base_names)} {random.choice(['', random.choice(base_names) + '-'])}{random.choice(suffixes)}"
        else:
            name = f"{random.choice(base_names)} {random.choice(['Smith', 'Jones', 'Williams', 'Brown', 'Taylor', 'Davies', 'Evans', 'Wilson', 'Thomas', 'Roberts'])} {random.choice(suffixes)}"
        
        # Add variation with numbers for similar suppliers
        if random.random() < 0.2 and i > 0:
            name = f"{random.choice(supplier_names).split(' ')[0]} Insight {random.choice(['Consulting', 'Advisory', 'Partners'])} {random.randint(1, 3)}"
        
        supplier_names.append(name)
    
    # Generate random data
    rows = []
    for _ in range(200):
        category = random.choice(categories)
        subcategory = random.choice(subcategories[category])
        
        # Generate a random date within the last 4 years
        days_ago = random.randint(0, 365*4)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        supplier_name = random.choice(supplier_names)
        supplier_id = f"TW_SUP_{random.randint(1000, 9999)}"
        
        # Infrastructure and technology have higher amounts
        if category in ["Infrastructure & Assets", "Technology & IT"]:
            amount = round(random.uniform(50000, 750000))
        else:
            amount = round(random.uniform(500, 150000))
        
        invoice_id = f"TW_INV_{format(random.getrandbits(32), 'X')}"
        po_id = f"TW_PO_{format(random.getrandbits(32), 'X')}"
        contract_id = f"TW_CON_{format(random.getrandbits(28), 'X')}"
        
        risk_score = round(random.uniform(1, 100))
        savings_opportunity = round(amount * random.uniform(0.01, 0.15))  # 1-15% potential savings
        
        row = [
            supplier_name,
            supplier_id,
            category,
            subcategory,
            random.choice(business_units),
            date,
            amount,
            invoice_id,
            po_id,
            random.choice(payment_terms),
            random.choice(currencies),
            contract_id,
            random.choice(regions),
            risk_score,
            savings_opportunity
        ]
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Return as CSV string
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    return csv_output.getvalue()

def generate_supplier_master_template():
    """Generate a comprehensive supplier master data template with all required fields"""
    
    # Define column headers
    headers = [
        "SupplierID", "SupplierName", "Category", "Country", "City", 
        "ContactName", "ContactEmail", "ContactPhone", "AnnualRevenue", 
        "PaymentTerms", "Active", "RelationshipStartDate", "TierRanking",
        "DiversityStatus", "SustainabilityRating", "RiskCategory",
        "Region", "Latitude", "Longitude"
    ]
    
    # Sample data
    categories = [
        "Chemicals Supply", "Pipeline & Network Maintenance", "Water Treatment Plant Operations",
        "Waste Management & Sludge Treatment", "Mechanical & Electrical Engineering",
        "Heavy Plant & Equipment Hire", "IT & Technology Solutions", "Facilities Management",
        "Professional Services (Legal/HR)", "Customer Service Solutions",
        "Civil Engineering & Construction", "Research & Development", "Leakage Detection Services",
        "Renewable Energy Solutions", "Environmental Consultancy", "Health & Safety Consultancy",
        "Engineering Design Services", "Fleet Management & Logistics", "Metering Technology & Services"
    ]
    
    countries = ["United Kingdom", "United States", "Germany", "France", "Netherlands", "Ireland", "Spain"]
    
    uk_cities = [
        "London", "Manchester", "Birmingham", "Leeds", "Glasgow", "Edinburgh", "Liverpool",
        "Bristol", "Oxford", "Cambridge", "Reading", "Southampton", "Luton", "Aylesbury",
        "Guildford", "Chelmsford", "Basingstoke", "Swindon", "Winchester", "Slough", "Maidstone"
    ]
    
    # For simplicity, mapping all international cities to their countries
    international_cities = {
        "United States": ["New York", "Chicago", "Los Angeles", "Boston", "Atlanta", "Dallas"],
        "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
        "France": ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille"],
        "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht"],
        "Ireland": ["Dublin", "Cork", "Galway", "Limerick"],
        "Spain": ["Madrid", "Barcelona", "Valencia", "Seville"]
    }
    
    payment_terms = ["Net 30", "Net 45", "Net 60", "Net 90"]
    tier_rankings = ["Tier 1", "Tier 2", "Tier 3"]
    diversity_statuses = ["Minority-Owned", "Women-Owned", "Veteran-Owned", "Small Business", "Not Applicable"]
    sustainability_ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "Not Rated"]
    risk_categories = ["Low", "Medium", "High", "Critical"]
    regions = ["North", "South", "East", "West", "Central", "International"]
    
    # Sample names for contacts
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emma", "James", "Olivia", 
        "Robert", "Sophia", "William", "Emily", "Richard", "Ava", "Joseph", "Mia",
        "Thomas", "Charlotte", "Christopher", "Amelia", "Daniel", "Abigail", 
        "Matthew", "Elizabeth", "Anthony", "Harper", "Mark", "Evelyn", "Donald",
        "Ella", "Steven", "Grace", "Andrew", "Chloe", "Paul", "Victoria", "Joshua",
        "Penelope", "Kenneth", "Lily", "Kevin", "Natalie", "Brian", "Samantha", 
        "George", "Eva", "Timothy", "Anna", "Stephen", "Hannah", "Eric", "Caroline",
        "Jason", "Alexis", "Liam", "Allison", "Noah", "Gabriella", "Benjamin", 
        "Maria", "Samuel", "Alice", "Ryan", "Nicole", "Nicholas", "Avery", "Tyler", 
        "Madison", "Jacob", "Emma", "Ethan", "Rebecca", "Alexander", "Claire", 
        "Jonathan", "Stella", "Dylan", "Leah", "Adam", "Skylar", "Caleb", "Lila"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
        "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Green",
        "Baker", "Adams", "Nelson", "Hill", "Ramirez", "Campbell", "Mitchell", "Roberts",
        "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins", "Edwards",
        "Stewart", "Flores", "Morris", "Nguyen", "Murphy", "Rivera", "Cook", "Rogers",
        "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly",
        "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood", "Watson", "Brooks",
        "Bennett", "Gray", "James", "Reyes", "Cruz", "Hughes", "Price", "Myers",
        "Long", "Foster", "Sanders", "Ross", "Morales", "Powell", "Sullivan", "Russell",
        "Ortiz", "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes", "Fisher", "Clarke"
    ]
    
    # Generate supplier data
    rows = []
    for i in range(1, 151):
        supplier_id = f"TW_SUP_{i:04d}"
        
        # Generate supplier name
        base_names = [
            "Aqua", "Hydro", "Flow", "Pipe", "Clear", "Thames", "Severn", "Kennet", 
            "Southern", "UK", "London", "Tech", "Digital", "Cyber", "Data", "Enviro", "Chem"
        ]
        
        suffixes = [
            "Solutions", "Systems", "Ltd", "Group", "PLC", "Services", "Engineering", 
            "Technologies", "Dynamics", "Partners", "Consulting", "Advisory", "Water", 
            "Utilities", "Tech"
        ]
        
        # Randomize the supplier name format
        name_type = random.randint(1, 4)
        if name_type == 1:
            supplier_name = f"{random.choice(base_names)} {random.choice(last_names)} {random.choice(suffixes)}"
        elif name_type == 2:
            supplier_name = f"{random.choice(base_names)} {random.choice(last_names)}-{random.choice(last_names)} {random.choice(suffixes)}"
        elif name_type == 3:
            supplier_name = f"{random.choice(last_names)} & {random.choice(last_names)} {random.choice(['Consulting', 'Advisory', 'Partners'])}"
        else:
            supplier_name = f"{random.choice(base_names)} {random.choice(suffixes)}"
        
        # For a few entries, create named instances
        if random.random() < 0.1:
            supplier_name = f"{random.choice(base_names)} Insight {random.choice(['Consulting', 'Advisory', 'Partners'])} {random.randint(1, 3)}"
        
        # Randomly choose country with UK being more common
        if random.random() < 0.8:
            country = "United Kingdom"
            city = random.choice(uk_cities)
            region = random.choice(regions[:-1])  # Exclude "International"
        else:
            country = random.choice(countries[1:])  # non-UK countries
            city = random.choice(international_cities[country])
            region = "International"
        
        # Generate UK coordinates (simplified)
        if country == "United Kingdom":
            latitude = random.uniform(50.0, 58.0)
            longitude = random.uniform(-6.0, 1.8)
        else:
            # Generate random international coordinates (simplified)
            latitude = random.uniform(25.0, 60.0)
            longitude = random.uniform(-120.0, 40.0)
        
        # Generate contact information
        contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        contact_email = f"{contact_name.lower().replace(' ', '.')}@{supplier_name.lower().split(' ')[0]}.co.uk"
        contact_phone = f"+44 {random.randint(1000, 9999)} {random.randint(100000, 999999)}"
        
        # Generate company data
        category = random.choice(categories)
        annual_revenue = random.randint(100000, 400000000)
        payment_terms = random.choice(payment_terms)
        active = random.choices([True, False], weights=[0.85, 0.15])[0]
        
        # Generate relationship start date within last 8 years
        days_ago = random.randint(365*1, 365*8)
        relationship_start_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Generate other classification fields
        tier_ranking = random.choice(tier_rankings)
        diversity_status = random.choice(diversity_statuses)
        sustainability_rating = random.choice(sustainability_ratings)
        risk_category = random.choice(risk_categories)
        
        # Create the complete row
        row = [
            supplier_id,
            supplier_name,
            category,
            country,
            city,
            contact_name,
            contact_email,
            contact_phone,
            annual_revenue,
            payment_terms,
            active,
            relationship_start_date,
            tier_ranking,
            diversity_status,
            sustainability_rating,
            risk_category,
            region,
            latitude,
            longitude
        ]
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Return as CSV string
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    return csv_output.getvalue()

def generate_contract_data_template():
    """Generate a comprehensive contract data template with all required fields"""
    
    # Define column headers
    headers = [
        "ContractID", "SupplierID", "SupplierName", "Category", "StartDate", 
        "EndDate", "RenewalDate", "Value", "AnnualValue", "Status", "Owner",
        "Department", "ContractType", "TerminationNoticePeriod", "AutoRenewal",
        "EscalationClause", "PaymentTerms", "Currency", "RiskRating"
    ]
    
    # Sample data
    categories = [
        "Chemicals Supply", "Pipeline & Network Maintenance", "Water Treatment Plant Operations",
        "Waste Management & Sludge Treatment", "Mechanical & Electrical Engineering",
        "Heavy Plant & Equipment Hire", "IT & Technology Solutions", "Facilities Management",
        "Professional Services", "Customer Service Solutions", "Civil Engineering & Construction",
        "Research & Development", "Leakage Detection Services", "Renewable Energy Solutions",
        "Environmental Consultancy", "Health & Safety Consultancy", "Engineering Design"
    ]
    
    statuses = ["Active", "Expired", "Pending Renewal", "In Negotiation", "Terminated"]
    departments = [
        "Water Production & Treatment", "Wastewater Collection & Treatment", 
        "Network Operations & Maintenance", "Customer Operations & Retail",
        "IT & Digital Transformation", "Human Resources", "Finance & Regulation",
        "Procurement & Supply Chain", "Strategic Resource Planning", 
        "Capital Delivery Programmes", "Asset Management Strategy", "Health, Safety & Environment"
    ]
    
    contract_types = ["Fixed Price", "Time & Materials", "Cost Plus", "Framework Agreement", "Service Level Agreement"]
    notice_periods = ["30 days", "60 days", "90 days", "6 months", "1 year"]
    escalation_clauses = ["Annual CPI", "Fixed 2%", "Fixed 3%", "Fixed 5%", "No Escalation", "Negotiable"]
    payment_terms = ["Net 30", "Net 45", "Net 60", "Net 90"]
    currencies = ["GBP", "USD", "EUR"]
    
    # Sample names for contract owners
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
        "Donald", "Steven", "Andrew", "Paul", "Joshua", "Mary", "Patricia", "Jennifer",
        "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa",
        "Nancy", "Betty", "Sandra", "Margaret", "Ashley", "Kimberly", "Emily", "Donna"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
        "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Green"
    ]
    
    # Generate contracts
    rows = []
    for i in range(1, 201):
        contract_id = f"TW_CON_{i:04d}"
        
        # Link to a supplier
        supplier_id = f"TW_SUP_{random.randint(1, 150):04d}"
        supplier_name = f"Supplier {supplier_id[7:]}"  # Placeholder - this would normally be looked up
        
        # Generate dates
        years_ago = random.randint(0, 5)
        months_ago = random.randint(0, 11)
        
        start_date = datetime.now() - timedelta(days=(years_ago*365 + months_ago*30))
        contract_length_years = random.randint(1, 5)
        end_date = start_date + timedelta(days=contract_length_years*365)
        renewal_date = end_date - timedelta(days=random.randint(30, 90))  # Typically renew 1-3 months before expiry
        
        # Format dates
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        renewal_date_str = renewal_date.strftime("%Y-%m-%d")
        
        # Generate values
        annual_value = random.randint(10000, 2000000)
        value = annual_value * contract_length_years
        
        # Determine status based on dates
        if start_date > datetime.now():
            status = "Pending"
        elif end_date < datetime.now():
            status = "Expired"
        elif renewal_date < datetime.now():
            status = "Pending Renewal"
        else:
            status = "Active"
        
        # Randomly override a few statuses
        if random.random() < 0.1:
            status = random.choice(["In Negotiation", "Terminated"])
        
        # Generate owner name
        owner = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Other contract details
        department = random.choice(departments)
        contract_type = random.choice(contract_types)
        notice_period = random.choice(notice_periods)
        auto_renewal = random.choice([True, False])
        escalation_clause = random.choice(escalation_clauses)
        payment_terms = random.choice(payment_terms)
        currency = random.choice(currencies)
        risk_rating = random.randint(1, 100)
        
        # Create the complete row
        row = [
            contract_id,
            supplier_id,
            supplier_name,
            random.choice(categories),
            start_date_str,
            end_date_str,
            renewal_date_str,
            value,
            annual_value,
            status,
            owner,
            department,
            contract_type,
            notice_period,
            auto_renewal,
            escalation_clause,
            payment_terms,
            currency,
            risk_rating
        ]
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Replace placeholder supplier names with more realistic ones
    supplier_patterns = [
        "Aqua", "Hydro", "Flow", "Pipe", "Clear", "Thames", "Severn", "Kennet", 
        "Southern", "UK", "London", "Tech", "Digital", "Cyber", "Data", "Enviro", "Chem"
    ]
    
    suffixes = [
        "Solutions", "Systems", "Ltd", "Group", "PLC", "Services", "Engineering", 
        "Dynamics", "Partners", "Consulting", "Advisory", "Water", "Utilities", "Tech"
    ]
    
    for index, row in df.iterrows():
        supplier_id_num = int(row['SupplierID'][7:])
        
        # Use a deterministic pattern based on supplier ID
        pattern_index = supplier_id_num % len(supplier_patterns)
        suffix_index = (supplier_id_num // len(supplier_patterns)) % len(suffixes)
        
        df.at[index, 'SupplierName'] = f"{supplier_patterns[pattern_index]} {random.choice(['', 'Group ', 'Inc. ', 'Corp. '])}{suffixes[suffix_index]}"
    
    # Return as CSV string
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    return csv_output.getvalue()

def generate_supplier_performance_template():
    """Generate a comprehensive supplier performance data template with all required fields"""
    
    # Define column headers
    headers = [
        "SupplierID", "SupplierName", "EvaluationDate", "EvaluationPeriod", 
        "QualityScore", "DeliveryScore", "CostScore", "InnovationScore", 
        "ResponsivenessScore", "SustainabilityScore", "OverallScore",
        "Category", "BusinessUnit", "Evaluator", "Comments",
        "ImprovementPlan", "NextReviewDate", "TrendIndicator"
    ]
    
    # Sample data
    categories = [
        "Chemicals Supply", "Pipeline & Network Maintenance", "Water Treatment Plant Operations",
        "Waste Management & Sludge Treatment", "Mechanical & Electrical Engineering",
        "Heavy Plant & Equipment Hire", "IT & Technology Solutions", "Facilities Management",
        "Professional Services", "Customer Service Solutions", "Civil Engineering & Construction",
        "Research & Development", "Leakage Detection Services", "Renewable Energy Solutions"
    ]
    
    business_units = [
        "Water Production & Treatment", "Wastewater Collection & Treatment", 
        "Network Operations & Maintenance", "Customer Operations & Retail",
        "IT & Digital Transformation", "Human Resources", "Finance & Regulation",
        "Procurement & Supply Chain", "Strategic Resource Planning", 
        "Capital Delivery Programmes", "Asset Management Strategy", "Health, Safety & Environment"
    ]
    
    evaluation_periods = ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "H1 2023", "H2 2023", "H1 2024", "Annual 2023"]
    trend_indicators = ["Improving", "Stable", "Declining", "Significantly Improving", "Significantly Declining"]
    
    # Sample comments based on overall score
    comments_excellent = [
        "Consistently exceeds expectations in all performance areas.",
        "Outstanding performance, a truly strategic partner.",
        "Exemplary service delivery with innovative solutions.",
        "Best-in-class supplier with exceptional quality and delivery.",
        "Proactive partner delivering significant value above contract requirements."
    ]
    
    comments_good = [
        "Reliable performance with occasional excellence in key areas.",
        "Solid service delivery with good communication.",
        "Consistently meets requirements with some areas of strength.",
        "Good overall performance with room for improvement in innovation.",
        "Dependable supplier with strong operational delivery."
    ]
    
    comments_average = [
        "Meets basic requirements but lacks consistency.",
        "Acceptable performance with some service delivery issues.",
        "Standard service with occasional quality concerns.",
        "Adequate performance but minimal value-added contributions.",
        "Meets contractual obligations with little additional value."
    ]
    
    comments_poor = [
        "Frequent service delivery issues requiring intervention.",
        "Inconsistent quality and reliability causing operational impacts.",
        "Multiple performance failures requiring formal improvement plan.",
        "Below standard performance with significant quality issues.",
        "Poor response times and inadequate problem resolution."
    ]
    
    improvement_plans = [
        "Weekly performance review meetings for 3 months",
        "Formal improvement plan with 90-day reassessment",
        "Corrective action required within 60 days",
        "Supplier development program participation required",
        "No improvement plan needed - performance exceeds requirements",
        "Quality management system review",
        "Joint process improvement workshops scheduled",
        "Monthly executive reviews until performance stabilizes",
        "None required - continue current approach",
        "Delivery process review and optimization"
    ]
    
    # Sample names for evaluators
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", 
        "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
        "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Green"
    ]
    
    # Generate performance data
    rows = []
    for _ in range(500):  # Generate plenty of performance data points
        supplier_id = f"TW_SUP_{random.randint(1, 150):04d}"
        
        # Generate evaluation date within last 2 years
        days_ago = random.randint(0, 730)
        evaluation_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Pick an evaluation period that roughly corresponds to the evaluation date
        if days_ago < 90:
            evaluation_period = "Q2 2024"
        elif days_ago < 180:
            evaluation_period = "Q1 2024"
        elif days_ago < 270:
            evaluation_period = "Q4 2023"
        elif days_ago < 360:
            evaluation_period = "Q3 2023"
        elif days_ago < 450:
            evaluation_period = "Q2 2023"
        elif days_ago < 540:
            evaluation_period = "Q1 2023"
        elif days_ago < 630:
            evaluation_period = "Q4 2022"
        else:
            evaluation_period = "Q3 2022"
        
        # Generate scores (1-10 scale)
        quality_score = random.randint(3, 10)
        delivery_score = random.randint(3, 10)
        cost_score = random.randint(3, 10)
        innovation_score = random.randint(2, 10)
        responsiveness_score = random.randint(3, 10)
        sustainability_score = random.randint(2, 10)
        
        # Calculate overall score (weighted average)
        overall_score = round((quality_score * 0.25 + 
                               delivery_score * 0.25 + 
                               cost_score * 0.2 + 
                               innovation_score * 0.1 + 
                               responsiveness_score * 0.1 + 
                               sustainability_score * 0.1), 1)
        
        # Select comments based on overall score
        if overall_score >= 8.5:
            comment = random.choice(comments_excellent)
            improvement_plan = "None required - continue current approach"
            trend = random.choices(["Improving", "Stable", "Significantly Improving"], weights=[0.4, 0.5, 0.1])[0]
        elif overall_score >= 7.0:
            comment = random.choice(comments_good)
            improvement_plan = random.choices(improvement_plans, weights=[0.1, 0.1, 0.1, 0.1, 0.3, 0.1, 0.1, 0.05, 0.05, 0.0])[0]
            trend = random.choices(["Improving", "Stable", "Declining"], weights=[0.3, 0.6, 0.1])[0]
        elif overall_score >= 5.0:
            comment = random.choice(comments_average)
            improvement_plan = random.choices(improvement_plans, weights=[0.2, 0.2, 0.1, 0.2, 0.0, 0.1, 0.1, 0.05, 0.0, 0.05])[0]
            trend = random.choices(["Improving", "Stable", "Declining"], weights=[0.2, 0.5, 0.3])[0]
        else:
            comment = random.choice(comments_poor)
            improvement_plan = random.choices(improvement_plans, weights=[0.3, 0.3, 0.2, 0.1, 0.0, 0.05, 0.0, 0.05, 0.0, 0.0])[0]
            trend = random.choices(["Stable", "Declining", "Significantly Declining"], weights=[0.1, 0.5, 0.4])[0]
        
        # Generate next review date (typically 3-6 months after evaluation)
        next_review_days = random.randint(90, 180)
        next_review_date = (datetime.now() - timedelta(days=days_ago) + timedelta(days=next_review_days)).strftime("%Y-%m-%d")
        
        # Generate evaluator name
        evaluator = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Create supplier name pattern based on ID
        supplier_id_num = int(supplier_id[7:])
        supplier_prefixes = ["Aqua", "Hydro", "Flow", "Pipe", "Clear", "Thames", "Severn", "Kennet", "Southern", "UK", "London", "Tech", "Digital", "Cyber", "Data", "Enviro", "Chem"]
        supplier_suffix = ["Solutions", "Systems", "Ltd", "Group", "PLC", "Services", "Engineering", "Dynamics", "Consulting", "Water"]
        
        prefix_index = supplier_id_num % len(supplier_prefixes)
        suffix_index = (supplier_id_num // len(supplier_prefixes)) % len(supplier_suffix)
        
        supplier_name = f"{supplier_prefixes[prefix_index]} {random.choice(last_names)} {supplier_suffix[suffix_index]}"
        
        # Create the complete row
        row = [
            supplier_id,
            supplier_name,
            evaluation_date,
            evaluation_period,
            quality_score,
            delivery_score,
            cost_score,
            innovation_score,
            responsiveness_score,
            sustainability_score,
            overall_score,
            random.choice(categories),
            random.choice(business_units),
            evaluator,
            comment,
            improvement_plan,
            next_review_date,
            trend
        ]
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Return as CSV string
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    return csv_output.getvalue()

def save_templates_to_csv():
    """Save all template data to CSV files in the attached_assets directory"""
    
    templates = {
        "spend_data_template.csv": generate_spend_data_template(),
        "supplier_master_data_template.csv": generate_supplier_master_template(),
        "contract_data_template.csv": generate_contract_data_template(),
        "supplier_performance_data_template.csv": generate_supplier_performance_template()
    }
    
    dir_path = "attached_assets"
    for filename, data in templates.items():
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'w', newline='') as file:
            file.write(data)
        print(f"Created template file: {filepath}")

def generate_requirements_doc():
    """Generate a comprehensive template requirements document"""
    
    requirements = """# Comprehensive Template Requirements

## 1. Spend Data Template
Required Fields:
- Supplier (text): Company name
- SupplierID (text): Unique identifier that links to supplier master data
- Category (text): Primary spend category 
- SubCategory (text): Secondary spend category
- BusinessUnit (text): Department or division
- Date (date): Transaction date in YYYY-MM-DD format
- Amount (numeric): Monetary value
- InvoiceID (text): Unique invoice identifier
- POID (text): Purchase order reference
- PaymentTerms (text): Payment terms (Net 30, Net 45, etc.)
- Currency (text): Transaction currency
- ContractID (text): Related contract identifier
- Region (text): Geographic region
- RiskScore (numeric): Risk rating 1-100
- SavingsOpportunity (numeric): Potential savings value

## 2. Supplier Master Data Template
Required Fields:
- SupplierID (text): Unique supplier identifier
- SupplierName (text): Company name
- Category (text): Primary supply category
- Country (text): Country of operation
- City (text): City of operation
- ContactName (text): Primary contact name
- ContactEmail (text): Contact email
- ContactPhone (text): Contact phone number
- AnnualRevenue (numeric): Supplier's annual revenue
- PaymentTerms (text): Standard payment terms
- Active (boolean): Current active status (True/False)
- RelationshipStartDate (date): Partnership start date
- TierRanking (text): Strategic importance ranking (Tier 1, 2, 3)
- DiversityStatus (text): Diversity classification
- SustainabilityRating (text): Environmental rating
- RiskCategory (text): Risk classification
- Region (text): Geographic region
- Latitude (numeric): Geographic coordinate for mapping
- Longitude (numeric): Geographic coordinate for mapping

## 3. Contract Data Template
Required Fields:
- ContractID (text): Unique contract identifier
- SupplierID (text): Links to supplier master data
- SupplierName (text): Company name
- Category (text): Category of contract
- StartDate (date): Contract start date
- EndDate (date): Contract end date
- RenewalDate (date): Next renewal date
- Value (numeric): Total contract value
- AnnualValue (numeric): Annual contract value
- Status (text): Current status (Active, Expired, etc.)
- Owner (text): Contract manager name
- Department (text): Responsible department
- ContractType (text): Type classification
- TerminationNoticePeriod (text): Notice period required
- AutoRenewal (boolean): Auto-renewal status (True/False)
- EscalationClause (text): Price escalation terms
- PaymentTerms (text): Payment terms
- Currency (text): Contract currency
- RiskRating (numeric): Risk assessment score

## 4. Supplier Performance Data Template
Required Fields:
- SupplierID (text): Links to supplier master data
- SupplierName (text): Company name
- EvaluationDate (date): Assessment date
- EvaluationPeriod (text): Period covered (e.g., "Q1 2024")
- QualityScore (numeric): Quality rating (1-10)
- DeliveryScore (numeric): Delivery performance (1-10)
- CostScore (numeric): Cost competitiveness (1-10)
- InnovationScore (numeric): Innovation rating (1-10)
- ResponsivenessScore (numeric): Response time rating (1-10)
- SustainabilityScore (numeric): Environmental rating (1-10)
- OverallScore (numeric): Composite performance score
- Category (text): Primary supply category
- BusinessUnit (text): Department rating the supplier
- Evaluator (text): Person conducting evaluation
- Comments (text): Assessment notes
- ImprovementPlan (text): Action plan if applicable
- NextReviewDate (date): Follow-up review date
- TrendIndicator (text): Performance trend (Improving, Stable, Declining)
"""
    
    # Write requirements document
    with open("attached_assets/template_requirements.md", 'w') as file:
        file.write(requirements)
    
    print("Created template requirements document: attached_assets/template_requirements.md")

if __name__ == "__main__":
    save_templates_to_csv()
    generate_requirements_doc()