import streamlit as st
import pandas as pd
import numpy as np

def generate_dynamic_filters(data, columns=None, max_filters=3, container=None):
    """
    Generate dynamic filters based on the dataset's column types
    
    Parameters:
    data: DataFrame containing the data
    columns: Optional list of specific columns to use for filtering
    max_filters: Maximum number of filters to display
    container: Optional streamlit container to render filters in (ignored for now)
    
    Returns:
    dict: Filter selections that can be applied to the dataframe
    """
    # Note: Ignoring container parameter for now as it's causing issues
    
    filters = {}
    filter_count = 0
    
    # If no data provided, return empty filters
    if data is None or data.empty:
        return filters
    
    # Check for column types in data attributes
    if hasattr(data, 'attrs') and 'column_types' in data.attrs:
        column_types = data.attrs['column_types']
        unique_values = data.attrs.get('unique_values', {})
        
        # Create filters for categorical columns first
        for col in column_types.get('categorical', []):
            if columns is not None and col not in columns:
                continue
                
            if filter_count >= max_filters:
                break
                
            # Get values from stored unique values or recalculate
            if col in unique_values:
                values = unique_values[col]
            else:
                values = sorted(data[col].dropna().unique().tolist())
                
            if len(values) <= 100:  # Don't create filter for columns with too many values
                # Create a selectbox with "All" option
                all_option = f"All {col}"
                options = [all_option] + values
                
                # Create selectbox directly with st
                selected = st.selectbox(f"Filter by {col}:", options, key=f"filter_{col}_{filter_count}")
                
                if selected != all_option:
                    filters[col] = selected
                    
                filter_count += 1
        
        # Then add date range filters
        for col in column_types.get('datetime', []):
            if columns is not None and col not in columns:
                continue
                
            if filter_count >= max_filters:
                break
                
            # Create a date range slider
            try:
                min_date = data[col].min().date()
                max_date = data[col].max().date()
                
                if min_date != max_date:
                    st.write(f"Filter by {col} date range:")
                    date_range = st.date_input(
                        f"Select range for {col}:",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key=f"date_range_{col}_{filter_count}"
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        filters[f"{col}_start"] = pd.to_datetime(start_date)
                        filters[f"{col}_end"] = pd.to_datetime(end_date)
                        
                    filter_count += 1
            except Exception as e:
                st.error(f"Error creating date filter for {col}: {e}")
                
        # Finally add numeric range sliders
        for col in column_types.get('numeric', []):
            if columns is not None and col not in columns:
                continue
                
            if filter_count >= max_filters:
                break
                
            try:
                min_val = float(data[col].min())
                max_val = float(data[col].max())
                
                if min_val != max_val:
                    st.write(f"Filter by {col} range:")
                    
                    # Determine appropriate step size
                    range_size = max_val - min_val
                    if range_size > 1000:
                        step = range_size / 100
                    elif range_size > 100:
                        step = 1.0
                    elif range_size > 10:
                        step = 0.1
                    else:
                        step = 0.01
                        
                    # Create a slider directly with st
                    range_values = st.slider(
                        f"Select range for {col}:",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=step,
                        key=f"range_{col}_{filter_count}"
                    )
                    
                    min_selected, max_selected = range_values
                    if min_selected > min_val or max_selected < max_val:
                        filters[f"{col}_min"] = min_selected
                        filters[f"{col}_max"] = max_selected
                        
                    filter_count += 1
            except Exception as e:
                st.error(f"Error creating numeric filter for {col}: {e}")
    
    # If no column_types in metadata, create basic filters
    else:
        # Get columns of likely categorical type
        cat_cols = []
        for col in data.columns:
            if columns is not None and col not in columns:
                continue
                
            if data[col].dtype == 'object' or len(data[col].unique()) < 10:
                cat_cols.append(col)
                
        # Only use the first max_filters columns
        for col in cat_cols[:max_filters]:
            values = sorted(data[col].dropna().unique().tolist())
            
            if len(values) <= 100:  # Don't create filter for columns with too many values
                # Create a selectbox with "All" option
                all_option = f"All {col}"
                options = [all_option] + values
                
                # Create selectbox directly with st
                selected = st.selectbox(f"Filter by {col}:", options, key=f"basic_filter_{col}")
                
                if selected != all_option:
                    filters[col] = selected
    
    return filters

def apply_filters(data, filters):
    """
    Apply generated filters to a dataframe
    
    Parameters:
    data: DataFrame to filter
    filters: Dict of filters from generate_dynamic_filters
    
    Returns:
    DataFrame: Filtered data
    """
    if not filters or data is None or data.empty:
        return data
        
    filtered_data = data.copy()
    
    for key, value in filters.items():
        if key.endswith('_min'):
            col = key[:-4]  # Remove '_min' suffix
            filtered_data = filtered_data[filtered_data[col] >= value]
        elif key.endswith('_max'):
            col = key[:-4]  # Remove '_max' suffix
            filtered_data = filtered_data[filtered_data[col] <= value]
        elif key.endswith('_start'):
            col = key[:-6]  # Remove '_start' suffix
            filtered_data = filtered_data[filtered_data[col] >= value]
        elif key.endswith('_end'):
            col = key[:-4]  # Remove '_end' suffix
            filtered_data = filtered_data[filtered_data[col] <= value]
        else:
            # Direct equality filter
            filtered_data = filtered_data[filtered_data[key] == value]
    
    return filtered_data