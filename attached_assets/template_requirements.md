# Comprehensive Template Requirements

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
