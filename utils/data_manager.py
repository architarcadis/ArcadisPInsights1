import pandas as pd
import numpy as np
from io import BytesIO

def load_data(file, file_type=None):
    """
    Load data from uploaded file and perform intelligent column type detection
    
    Parameters:
    file: The uploaded file object
    file_type: The type of file (csv or excel)
    
    Returns:
    pd.DataFrame: The loaded data with detected column types in attrs
    """
    if file_type is None:
        # Try to infer file type from name
        if file.name.endswith('.csv'):
            file_type = 'csv'
        elif file.name.endswith('.xlsx'):
            file_type = 'excel'
        else:
            raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
    
    # Load the data
    if file_type == 'csv':
        df = pd.read_csv(file)
    elif file_type == 'excel':
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
    
    # Perform intelligent column type detection
    detect_column_types(df)
    
    return df

def detect_column_types(df):
    """
    Intelligently detect column types and store metadata in dataframe attrs
    
    Parameters:
    df: The pandas DataFrame to analyze
    
    Returns:
    None (modifies df.attrs in place)
    """
    # Initialize column type containers
    numeric_cols = []
    date_cols = []
    monetary_cols = []
    categorical_cols = []
    id_cols = []
    text_cols = []
    
    # Store unique values for categorical columns
    unique_values = {}
    
    # Analyze each column
    for col in df.columns:
        # Skip columns with all missing values
        if df[col].isna().all():
            continue
            
        # Check if column name suggests an ID field
        if any(id_term in col.lower() for id_term in ['id', 'code', 'number', 'no.', 'key']):
            id_cols.append(col)
            continue
            
        # Check if column is already numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check if it might be monetary
            col_name_lower = col.lower()
            if any(money_term in col_name_lower for money_term in ['amount', 'price', 'cost', 'value', 'spend', 'budget', 'revenue']):
                monetary_cols.append(col)
            else:
                numeric_cols.append(col)
            continue
            
        # Try to convert to datetime
        try:
            # Check if column name suggests a date field
            if any(date_term in col.lower() for date_term in ['date', 'day', 'month', 'year', 'time', 'period', 'quarter']):
                pd.to_datetime(df[col])
                date_cols.append(col)
                continue
        except:
            pass
            
        # Check number of unique values to determine if categorical
        n_unique = df[col].nunique()
        n_total = len(df[col].dropna())
        
        if n_unique <= 50 or (n_unique / n_total <= 0.2 and n_unique <= 100):
            categorical_cols.append(col)
            # Store unique values for filtering
            unique_values[col] = sorted(df[col].dropna().unique().tolist())
        else:
            # Likely a text field
            text_cols.append(col)
    
    # Store detected types in dataframe attrs
    df.attrs['column_types'] = {
        'numeric': numeric_cols,
        'date': date_cols,
        'monetary': monetary_cols,
        'categorical': categorical_cols,
        'id': id_cols,
        'text': text_cols
    }
    
    # Store unique values for categorical columns
    df.attrs['unique_values'] = unique_values

def validate_data(file, data_type):
    """
    Validate uploaded data based on expected structure for data type
    
    Parameters:
    file: The uploaded file object
    data_type: The type of data being uploaded (Spend Data, Supplier Master, etc.)
    
    Returns:
    tuple: (is_valid, message, data)
    """
    try:
        # Determine file type from extension
        file_type = None
        if file.name.endswith('.csv'):
            file_type = 'csv'
        elif file.name.endswith('.xlsx'):
            file_type = 'excel'
        else:
            return False, "Unsupported file type. Please upload a CSV or Excel file.", None
        
        # Load the data
        data = load_data(file, file_type)
        
        # Define schemas for each data type - updated for exact template formats
        schemas = {
            "Spend Data": {
                "required": ['Supplier', 'Category'],  # Simplified required fields
                "numeric": ['Amount'],
                "date": ['Date'],
                "categorical": ['Supplier', 'Category', 'SubCategory', 'BusinessUnit']
            },
            "Supplier Master Data": {
                "required": ['SupplierID'],  # Just need one field to identify
                "numeric": ['AnnualRevenue'],
                "date": ['RelationshipStartDate'],
                "categorical": ['Category', 'Country', 'City', 'Active']
            },
            "Contract Data": {
                "required": ['ContractID'],  # Just need one field to identify
                "numeric": ['Value', 'NoticePeriodDays'],
                "date": ['StartDate', 'EndDate'],
                "categorical": ['Status', 'AutoRenewal']
            },
            "Performance Data": {
                "required": ['SupplierID'],  # Just need one field to identify
                "numeric": ['DeliveryScore', 'QualityScore', 'ResponsivenessScore', 'OverallScore'],
                "date": [],
                "categorical": ['Quarter']
            }
        }
        
        # Validate based on data type
        if data_type in schemas:
            schema = schemas[data_type]
            required_columns = schema["required"]
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
            
            # Process numeric columns
            for col in schema["numeric"]:
                if col in data.columns:
                    try:
                        data[col] = pd.to_numeric(data[col])
                    except:
                        return False, f"Column '{col}' must contain numeric values", None
            
            # Process date columns
            for col in schema["date"]:
                if col in data.columns:
                    try:
                        data[col] = pd.to_datetime(data[col])
                    except:
                        return False, f"Column '{col}' must contain valid dates", None
            
            # Additional validation for specific data types
            if data_type == "Spend Data":
                # Check for null values in critical columns
                null_suppliers = data['Supplier'].isnull().sum()
                if null_suppliers > 0:
                    return False, f"Found {null_suppliers} rows with missing supplier information", None
            
            # Store metadata in DataFrame for dynamic UI generation
            data.attrs["schema"] = schema
            
            # Store unique values for categorical columns 
            data.attrs["unique_values"] = {}
            for col in schema["categorical"]:
                if col in data.columns:
                    data.attrs["unique_values"][col] = sorted(data[col].unique().tolist())
            
            # Store column types for dynamic visualization
            data.attrs["column_types"] = {
                "numeric": [col for col in schema["numeric"] if col in data.columns],
                "date": [col for col in schema["date"] if col in data.columns],
                "categorical": [col for col in schema["categorical"] if col in data.columns]
            }
            
            return True, f"{data_type} validated successfully", data
        
        else:
            return False, f"Unknown data type: {data_type}", None
    
    except Exception as e:
        return False, f"Error during validation: {str(e)}", None
