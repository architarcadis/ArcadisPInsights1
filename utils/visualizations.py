import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def apply_standard_legend_style(fig):
    """
    Apply standardized horizontal legend style to all charts
    
    Parameters:
    fig: plotly figure to update
    
    Returns:
    fig: the updated figure
    """
    # Force horizontal legend at the bottom with much more aggressive settings
    fig.update_layout(
        height=550,                   # Taller charts to accommodate legend below
        legend=dict(
            orientation="h",          # Force horizontal orientation
            y=-0.25,                  # Position much further below the chart
            x=0.5,                    # Center horizontally
            xanchor="center",         # Ensure center anchoring
            yanchor="top",            # Anchor from top of legend area
            font=dict(size=10),       # Readable font size
            bgcolor="rgba(30,30,30,0.8)",
            bordercolor="rgba(255,255,255,0.3)",
            borderwidth=1,
            itemsizing="constant"     # Keep consistent sizing
        ),
        margin=dict(b=120, t=40, l=40, r=40)  # Much more space at bottom
    )
    
    return fig

def create_spend_chart(data, dimension='Category', time_dimension=None, value_column='Amount'):
    """
    Create a spend chart based on the specified dimension
    
    Parameters:
    data: DataFrame containing spend data
    dimension: The dimension to group by (Category, Supplier, etc.)
    time_dimension: Optional time dimension for trend analysis
    value_column: The column containing the values to analyze (defaults to 'Amount')
    
    Returns:
    plotly.graph_objects.Figure: The created chart
    """
    # Handle empty or None data
    if data is None or len(data) == 0 or not isinstance(data, pd.DataFrame):
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="darkred")
        )
        fig.update_layout(height=400)
        return fig
        
    # Validate input parameters - use graceful error handling
    if dimension not in data.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: Dimension column '{dimension}' not found in data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="darkred")
        )
        fig.update_layout(height=400)
        return fig
    
    if value_column not in data.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: Value column '{value_column}' not found in data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="darkred")
        )
        fig.update_layout(height=400)
        return fig
    
    # Make a copy to avoid modifying the original data
    df = data.copy()
        
    # Create appropriate title based on value column
    display_value = value_column.replace("_", " ").title()
    
    # Initialize fig variable
    fig = None
    
    # Check if we have time dimension data
    if time_dimension and time_dimension in df.columns:
        try:
            # Create a time-based trend chart
            # Try to ensure time_dimension is in datetime format
            if not pd.api.types.is_datetime64_any_dtype(df[time_dimension]):
                df[time_dimension] = pd.to_datetime(df[time_dimension])
                    
            df_grouped = df.groupby([time_dimension, dimension])[value_column].sum().reset_index()
            
            # If too many dimension values, limit to top N
            unique_values = df[dimension].nunique()
            if unique_values > 8:
                # Find top values by total amount
                top_values = df.groupby(dimension)[value_column].sum().nlargest(8).index.tolist()
                mask = df_grouped[dimension].isin(top_values)
                df_grouped = df_grouped[mask]
            
            fig = px.line(
                df_grouped, 
                x=time_dimension, 
                y=value_column, 
                color=dimension,
                title=f'{display_value} by {dimension} Over Time',
                labels={value_column: f'{display_value} Value', time_dimension: time_dimension},
                color_discrete_sequence=px.colors.sequential.Oranges
            )
        except Exception as e:
            # If time chart fails, fall back to bar/pie chart
            pass
    
    # If time chart wasn't created or failed, create bar/pie chart
    if fig is None:
        try:
            # Create a simple bar or pie chart
            df_grouped = df.groupby(dimension)[value_column].sum().reset_index().sort_values(value_column, ascending=False)
            
            if len(df_grouped) <= 15:
                # Use horizontal bar chart with percentage labels for better readability
                df_grouped = df_grouped.sort_values(value_column)  # Sort ascending for horizontal bar
                total = df_grouped[value_column].sum()
                df_grouped['Percentage'] = (df_grouped[value_column] / total * 100).round(1)
                
                # Create bar chart with percentage labels
                fig = px.bar(
                    df_grouped, 
                    y=dimension,  # Categories on y-axis for horizontal bars
                    x=value_column,
                    title=f'{display_value} Distribution by {dimension}',
                    color=value_column,
                    color_continuous_scale='Oranges',
                    text=df_grouped['Percentage'].apply(lambda x: f'{x}%'),
                    orientation='h'  # Horizontal bars
                )
                
                # Improve readability
                fig.update_traces(textposition='auto')
                fig.update_layout(
                    xaxis_title=f'{display_value}',
                    yaxis_title=dimension,
                    coloraxis_showscale=False  # Hide color scale
                )
            else:
                # Use bar chart for many categories, showing top 10
                top_df = df_grouped.head(10)
                fig = px.bar(
                    top_df, 
                    x=dimension, 
                    y=value_column,
                    title=f'Top 10 {display_value} by {dimension}',
                    labels={value_column: f'{display_value} Value'},
                    color=value_column,
                    color_continuous_scale='Oranges'
                )
        except Exception as e:
            # Create an empty chart with error message if all else fails
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="darkred")
            )
            fig.update_layout(height=400)
            return fig
    
    # Update layout if we have a valid figure
    if fig is not None:
        fig.update_layout(
            legend_title_text=dimension,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    else:
        # Create a default figure as a fallback
        fig = go.Figure()
        fig.add_annotation(
            text="Could not create visualization with provided data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="darkred")
        )
        fig.update_layout(height=400)
    
    return fig

def create_supplier_chart(performance_data, supplier_data, metric='OverallScore', title=None, top_n=15):
    """
    Create a supplier performance chart
    
    Parameters:
    performance_data: DataFrame containing supplier performance data
    supplier_data: DataFrame containing supplier master data
    metric: The performance metric to visualize
    title: Optional custom title for the chart
    top_n: Number of top suppliers to display (default=15)
    
    Returns:
    plotly.graph_objects.Figure: The created chart
    """
    import plotly.express as px
    
    # Validate input data
    if performance_data is None or supplier_data is None:
        fig = px.bar(title="Missing Data")
        fig.update_layout(
            annotations=[{
                'text': "No performance or supplier data available.",
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5
            }]
        )
        return fig
    
    # Ensure required columns are present
    if 'SupplierID' not in performance_data.columns or 'SupplierID' not in supplier_data.columns:
        fig = px.bar(title="Invalid Data Structure")
        fig.update_layout(
            annotations=[{
                'text': "Performance or supplier data is missing required 'SupplierID' column.",
                'showarrow': False,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5
            }]
        )
        return fig
    
    # Check if the metric exists
    if metric not in performance_data.columns:
        # Try to find a suitable metric
        potential_metrics = ['OverallScore', 'QualityScore', 'DeliveryScore', 'ResponsivenessScore']
        available_metrics = [m for m in potential_metrics if m in performance_data.columns]
        
        if available_metrics:
            metric = available_metrics[0]
        else:
            # Use the first numeric column as a fallback
            numeric_cols = [col for col in performance_data.columns 
                           if pd.api.types.is_numeric_dtype(performance_data[col]) 
                           and col != 'SupplierID']
            
            if numeric_cols:
                metric = numeric_cols[0]
            else:
                fig = px.bar(title="No Metrics Available")
                fig.update_layout(
                    annotations=[{
                        'text': "No suitable performance metrics found in data.",
                        'showarrow': False,
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': 0.5
                    }]
                )
                return fig
    
    # Determine name column in supplier data
    name_column = 'SupplierName' if 'SupplierName' in supplier_data.columns else None
    category_column = 'Category' if 'Category' in supplier_data.columns else None
    
    # Adjust columns to merge based on what's available
    merge_columns = ['SupplierID']
    if name_column:
        merge_columns.append(name_column)
    if category_column:
        merge_columns.append(category_column)
    
    # Merge performance data with supplier information
    merged_data = performance_data.merge(
        supplier_data[merge_columns], 
        on='SupplierID', 
        how='left'
    )
    
    # Group by supplier and calculate average performance
    group_by_cols = ['SupplierID']
    if name_column:
        group_by_cols.append(name_column)
    if category_column:
        group_by_cols.append(category_column)
    
    df_grouped = merged_data.groupby(group_by_cols)[metric].mean().reset_index()
    
    # Sort by performance metric
    df_grouped = df_grouped.sort_values(metric, ascending=False)
    
    # Limit to top N
    if len(df_grouped) > top_n:
        df_display = df_grouped.head(top_n)
    else:
        df_display = df_grouped
    
    # Format metric name for display
    metric_display = metric.replace("Score", " Score").replace("_", " ").title()
    
    # Set chart title
    if title is None:
        title = f'Top {min(top_n, len(df_grouped))} Suppliers by {metric_display}'
    
    # Create horizontal bar chart
    y_axis = name_column if name_column else 'SupplierID'
    
    fig = px.bar(
        df_display, 
        y=y_axis, 
        x=metric,
        color=metric,
        orientation='h',
        title=title,
        labels={metric: f'{metric_display}', y_axis: 'Supplier'},
        color_continuous_scale='Oranges'
    )
    
    # Add a vertical line for the average score
    avg_score = df_grouped[metric].mean()
    fig.add_vline(
        x=avg_score, 
        line_dash="dash", 
        line_color="gray",
        annotation_text=f"Avg: {avg_score:.1f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        height=max(350, 50 + 20 * len(df_display))  # Dynamic height based on number of suppliers
    )
    
    return fig

def create_risk_heatmap(data, x_dim='Category', y_dim='BusinessUnit', value='Amount', title=None):
    """
    Create a heatmap visualization for risk or spend analysis
    
    Parameters:
    data: DataFrame containing the data
    x_dim: The dimension for the x-axis
    y_dim: The dimension for the y-axis
    value: The value to be represented by color intensity
    title: Optional custom title for the chart
    
    Returns:
    plotly.graph_objects.Figure: The created heatmap
    """
    import plotly.graph_objects as go
    import numpy as np
    
    # Create a blank figure for error cases
    def create_error_figure(message, error_title):
        error_fig = go.Figure()
        error_fig.update_layout(
            title=error_title,
            height=400
        )
        error_fig.add_annotation(
            text=message,
            xref="paper", 
            yref="paper",
            x=0.5, 
            y=0.5, 
            showarrow=False
        )
        return error_fig
    
    # Validate input parameters
    for dim in [x_dim, y_dim, value]:
        if dim not in data.columns:
            return create_error_figure(
                f"Column '{dim}' not found in data.<br>Please check your data or select different dimensions.",
                "Data Validation Error"
            )
    
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Ensure value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value]):
        try:
            df[value] = pd.to_numeric(df[value])
        except:
            return create_error_figure(
                f"Column '{value}' must contain numeric values for heatmap visualization.",
                "Data Type Error"
            )
    
    # Handle empty data case
    if df.empty or len(df[x_dim].unique()) < 2 or len(df[y_dim].unique()) < 2:
        return create_error_figure(
            "Not enough data to generate heatmap.<br>Try adjusting your filters.",
            title or f"Distribution by {x_dim} and {y_dim}"
        )
    
    # Identify top values if there are too many unique values
    x_values = df[x_dim].nunique()
    y_values = df[y_dim].nunique()
    
    if x_values > 12 or y_values > 12:
        # If too many unique values, focus on top combinations
        top_x = df.groupby(x_dim)[value].sum().nlargest(12).index.tolist() if x_values > 12 else df[x_dim].unique()
        top_y = df.groupby(y_dim)[value].sum().nlargest(12).index.tolist() if y_values > 12 else df[y_dim].unique()
        
        df = df[df[x_dim].isin(top_x) & df[y_dim].isin(top_y)]
    
    # Group data by the two dimensions
    df_grouped = df.groupby([y_dim, x_dim])[value].sum().reset_index()
    
    # Pivot the data for the heatmap
    df_pivot = df_grouped.pivot(index=y_dim, columns=x_dim, values=value)
    
    # Fill any NaN values with 0
    df_pivot = df_pivot.fillna(0)
    
    # Format values for better readability
    max_value = df_pivot.values.max()
    value_label = value.replace("_", " ").title()
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale='Oranges',
        hoverongaps=False,
        hovertemplate='%{y} - %{x}<br>' + value_label + ': $%{z:,.2f}<extra></extra>'
    ))
    
    # Add text annotations with formatted values
    annotations = []
    for i, row in enumerate(df_pivot.index):
        for j, col in enumerate(df_pivot.columns):
            val = df_pivot.iloc[i, j]
            
            # Skip very small values or zeros
            if val == 0:
                continue
                
            # Format numbers for better display
            if val >= 1000000:
                text = f"${val/1000000:.1f}M"
            elif val >= 1000:
                text = f"${val/1000:.1f}K"
            else:
                text = f"${val:.0f}"
                
            # Set text color based on cell shade
            font_color = 'white' if val > max_value / 2 else 'black'
            
            annotations.append(dict(
                x=col, 
                y=row,
                text=text,
                font=dict(color=font_color, size=10),
                showarrow=False
            ))
    
    # Generate automatic title if none provided
    if title is None:
        title = f'{value_label} Concentration by {y_dim} and {x_dim}'
    
    # Improve layout with better title and formatting
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        height=max(350, 80 + 40 * len(df_pivot.index)),  # Dynamic height based on data size
        margin=dict(l=50, r=50, b=50, t=80),
        annotations=annotations,
        xaxis_title=f'{x_dim}',
        yaxis_title=f'{y_dim}'
    )
    
    return fig

def create_supplier_map(supplier_data, performance_data=None, perf_metric='OverallScore', title=None):
    """
    Create a geographical map of suppliers, optionally colored by performance
    
    Parameters:
    supplier_data: DataFrame containing supplier information with location data
    performance_data: Optional DataFrame with performance metrics
    perf_metric: The performance metric to use for coloring (if performance_data is provided)
    title: Optional custom title for the map
    
    Returns:
    plotly.graph_objects.Figure: The created map
    """
    import plotly.express as px
    
    # Make a copy to avoid modifying the original
    df = supplier_data.copy()
    
    # Default values for plotting parameters
    color = None
    hover_data = []
    color_scale = None
    color_continuous_midpoint = None
    
    # Check for required location columns
    required_cols = ['Latitude', 'Longitude']
    for col in required_cols:
        if col not in df.columns:
            # Create a blank figure with an error message
            fig = px.scatter_geo()
            fig.update_layout(
                title='Map Error'
            )
            fig.add_annotation(
                text=f"Missing required column: '{col}'. Location data is needed for map visualization.",
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.5,
                y=0.5
            )
            return fig
    
    # Ensure location data is numeric
    for col in required_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                # Create a blank figure with an error message
                fig = px.scatter_geo()
                fig.update_layout(
                    title='Map Error'
                )
                fig.add_annotation(
                    text=f"Column '{col}' must contain numeric values for mapping.",
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0.5,
                    y=0.5
                )
                return fig
    
    # If performance data is provided, merge it
    if performance_data is not None and 'SupplierID' in performance_data.columns:
        if perf_metric not in performance_data.columns:
            # Fallback to OverallScore if requested metric not available
            if 'OverallScore' in performance_data.columns:
                perf_metric = 'OverallScore'
            else:
                # Use the first numeric column as a fallback
                numeric_cols = [col for col in performance_data.columns 
                                if pd.api.types.is_numeric_dtype(performance_data[col])]
                if numeric_cols:
                    perf_metric = numeric_cols[0]
                else:
                    # No usable metrics found
                    performance_data = None
        
        if performance_data is not None:
            # Calculate average performance per supplier
            perf_avg = performance_data.groupby('SupplierID')[perf_metric].mean().reset_index()
            df = df.merge(perf_avg, on='SupplierID', how='left')
            color = perf_metric
            hover_data = ['SupplierName', 'Category', perf_metric]
            color_scale = 'Oranges'
            color_continuous_midpoint = df[perf_metric].median() if not df[perf_metric].isna().all() else None
    else:
        # Use Category as color if available, otherwise use a default color
        if 'Category' in df.columns:
            color = 'Category'
            hover_data = ['SupplierName', 'Category']
            color_scale = None
            color_continuous_midpoint = None
        else:
            color = None
            hover_data = ['SupplierName']
            color_scale = None
            color_continuous_midpoint = None
    
    # Determine map title
    if title is None:
        if performance_data is not None:
            metric_display = perf_metric.replace('_', ' ').title()
            title = f'Supplier Locations by {metric_display}'
        else:
            title = 'Supplier Geographical Distribution'
    
    # Create the map
    fig = px.scatter_geo(
        df,
        lat='Latitude',
        lon='Longitude',
        color=color,
        hover_name='SupplierName' if 'SupplierName' in df.columns else None,
        hover_data=hover_data,
        projection='natural earth',
        title=title,
        color_continuous_scale=color_scale,
        color_continuous_midpoint=color_continuous_midpoint
    )
    
    # Apply consistent styling
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        )
    )
    
    return fig
