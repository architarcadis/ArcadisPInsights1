import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import create_spend_chart, create_risk_heatmap, apply_standard_legend_style
from utils.llm_analysis import generate_category_insights, generate_market_insights

def show(session_state):
    """Display the Category Intelligence tab content"""
    st.title("📊 Category Intelligence")
    
    # Get data from session state
    spend_data = session_state.spend_data
    
    # Filters section
    st.subheader("Filters")
    
    col1, col2, col3 = st.columns(3)
    
    # Import our dynamic filter utility
    from utils.dynamic_filters import generate_dynamic_filters, apply_filters
    
    # Auto-generate filters based on detected column types
    # First create containers for each column
    filter_containers = [col1, col2, col3]
    
    # Generate filters based on data column types
    # Prioritize category, business unit, and date if available
    priority_columns = []
    if "Category" in spend_data.columns:
        priority_columns.append("Category")
    if "BusinessUnit" in spend_data.columns:
        priority_columns.append("BusinessUnit")
    if "Date" in spend_data.columns:
        priority_columns.append("Date")
    
    # Generate filters for each container
    all_filters = {}
    selected_category = None
    selected_bu = None
    
    # For backward compatibility, create the original filters if columns are present
    if "Category" in spend_data.columns:
        with col1:
            categories = ["All Categories"] + sorted(spend_data["Category"].unique().tolist())
            selected_category = st.selectbox("Select Category:", categories)
            if selected_category != "All Categories":
                all_filters["Category"] = selected_category
    
    if "BusinessUnit" in spend_data.columns:
        with col2:
            business_units = ["All Business Units"] + sorted(spend_data["BusinessUnit"].unique().tolist())
            selected_bu = st.selectbox("Select Business Unit:", business_units)
            if selected_bu != "All Business Units":
                all_filters["BusinessUnit"] = selected_bu
                
    # For the third column, use dynamic filter generation
    remaining_columns = [col for col in spend_data.columns 
                         if col not in ["Category", "BusinessUnit"] 
                         and col in (
                             spend_data.attrs.get('column_types', {}).get('date', []) +
                             spend_data.attrs.get('column_types', {}).get('monetary', []) +
                             spend_data.attrs.get('column_types', {}).get('categorical', [])
                         )]
    
    if remaining_columns and len(remaining_columns) > 0:
        with col3:
            remaining_filters = generate_dynamic_filters(
                spend_data, 
                columns=[remaining_columns[0]], 
                max_filters=1,
                container=st
            )
            all_filters.update(remaining_filters)
    
    # Apply all filters to data
    filtered_data = apply_filters(spend_data, all_filters)
    
    # Main content area
    if len(filtered_data) == 0:
        st.warning("No data available with the selected filters.")
    else:
        st.subheader("Spending Pattern & Opportunities")
        
        # Calculate key metrics
        total_spend = filtered_data["Amount"].sum()
        avg_transaction = filtered_data["Amount"].mean()
        transaction_count = len(filtered_data)
        supplier_count = filtered_data["Supplier"].nunique()
        
        # Add insight to metrics
        st.markdown(f"""
        *Understanding your spending profile provides the foundation for strategic sourcing decisions.*
        """)
        
        # Display metrics in columns
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        # Format metrics for better readability
        def format_currency(value):
            if value >= 1000000:
                return f"${value/1000000:.1f}M"
            elif value >= 1000:
                return f"${value/1000:.1f}K"
            else:
                return f"${value:.0f}"
                
        with metric_col1:
            st.metric("Total Spend", format_currency(total_spend))
            st.markdown(f"<div style='font-size:0.8em; color:#999'>Full amount: ${total_spend:,.2f}</div>", unsafe_allow_html=True)
        
        with metric_col2:
            st.metric("Suppliers", f"{supplier_count}")
            
        with metric_col3:
            st.metric("Transactions", f"{transaction_count:,}")
        
        with metric_col4:
            st.metric("Avg. Transaction", format_currency(avg_transaction))
            st.markdown(f"<div style='font-size:0.8em; color:#999'>Full amount: ${avg_transaction:,.2f}</div>", unsafe_allow_html=True)
            
        # Add opportunity insight based on metrics
        if supplier_count > 0 and transaction_count > 0:
            transactions_per_supplier = transaction_count / supplier_count
            if transactions_per_supplier < 5:
                st.info(f"⚠️ **Opportunity Alert**: Low transaction volume per supplier ({transactions_per_supplier:.1f}) suggests potential for supplier consolidation to improve efficiency and leverage.")
            elif supplier_count < 3 and total_spend > 500000:
                st.info(f"⚠️ **Risk Alert**: High spend concentration with only {supplier_count} suppliers may represent a supply risk. Consider supplier diversification strategy.")
            elif avg_transaction < 1000 and transaction_count > 100:
                st.info(f"⚠️ **Efficiency Alert**: High volume of small transactions (avg ${avg_transaction:.2f}) indicates opportunity to implement catalog purchasing or consolidate orders.")
        
        # Create charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Dynamic dimension selection based on available data columns
            if "Category" in filtered_data.columns:
                if selected_category == "All Categories" or selected_category is None:
                    dimension = "Category"
                    title = "Spend Distribution by Category"
                    subtitle = "Identify your highest-spend categories for strategic focus"
                elif "SubCategory" in filtered_data.columns:
                    dimension = "SubCategory"
                    title = f"Breaking Down {selected_category}"
                    subtitle = f"Detailed spend within {selected_category}"
                else:
                    dimension = "Supplier"
                    title = f"Suppliers in {selected_category}"
                    subtitle = f"Spend distribution across suppliers"
            elif "Supplier" in filtered_data.columns:
                dimension = "Supplier"
                title = "Spend by Supplier"
                subtitle = "Distribution of spend across suppliers"
            else:
                # Find a suitable categorical column
                categorical_cols = [col for col in filtered_data.columns 
                                   if col != "Amount" and filtered_data[col].dtype == "object"]
                if categorical_cols:
                    dimension = categorical_cols[0]
                    title = f"Spend by {dimension}"
                    subtitle = f"Distribution across {dimension} values"
                else:
                    st.warning("No suitable categorical columns found for chart visualization")
                    dimension = None
            
            # Create chart if dimension is available
            if dimension is not None and dimension in filtered_data.columns:
                try:
                    fig1 = create_spend_chart(filtered_data, dimension=dimension)
                    fig1.update_layout(
                        title={
                            'text': title,
                            'y':0.95,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        legend=dict(
                            orientation="h",       # Horizontal legend
                            yanchor="top",         # Anchor from top of legend box
                            y=-0.3,                # Position well below the chart
                            xanchor="center",      # Center anchor
                            x=0.5                  # Center position
                        ),
                        margin=dict(l=20, r=20, t=50, b=100),  # Extra bottom margin
                        height=550                 # Taller chart
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    st.caption(subtitle)
                except Exception as e:
                    st.error(f"Unable to create chart: {str(e)}")
        
        with chart_col2:
            # Top suppliers chart with added context and insight
            if "Supplier" in filtered_data.columns and "Amount" in filtered_data.columns:
                try:
                    suppliers_df = filtered_data.groupby("Supplier")["Amount"].sum().reset_index()
                    suppliers_df = suppliers_df.sort_values("Amount", ascending=False).head(10)
                    
                    # Calculate concentration metrics for insight
                    total_category_spend = filtered_data["Amount"].sum()
                    top3_spend = suppliers_df.head(3)["Amount"].sum() if len(suppliers_df) >= 3 else suppliers_df["Amount"].sum()
                    top3_concentration = (top3_spend / total_category_spend * 100) if total_category_spend > 0 else 0
                    
                    supplier_title = "Supplier Concentration Analysis"
                    supplier_subtitle = f"Top suppliers represent {top3_concentration:.1f}% of total spend"
                    
                    fig2 = px.bar(
                        suppliers_df,
                        y="Supplier",
                        x="Amount",
                        orientation="h",
                        title=supplier_title,
                        labels={"Amount": "Spend Amount ($)", "Supplier": "Supplier"},
                        color="Amount",
                        color_continuous_scale="Oranges"
                    )
                    
                    fig2.update_layout(
                        yaxis={'categoryorder':'total ascending'},
                        title={
                            'text': supplier_title,
                            'y':0.95,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        legend=dict(
                            orientation="h",       # Horizontal legend
                            yanchor="top",         # Anchor from top of legend box
                            y=-0.3,                # Position well below the chart
                            xanchor="center",      # Center anchor
                            x=0.5                  # Center position
                        ),
                        margin=dict(l=20, r=20, t=50, b=100),  # Extra bottom margin
                        height=550                 # Taller chart
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    st.caption(supplier_subtitle)
                    
                    # Add actionable insight based on concentration
                    if top3_concentration > 75:
                        st.info("⚠️ **High supplier concentration detected.** While this offers potential leverage for negotiations, it also creates dependency risk. Consider developing alternative suppliers to mitigate supply chain risk.")
                    elif top3_concentration < 30 and len(suppliers_df) > 7:
                        st.info("⚠️ **Low supplier concentration detected.** Your spend is highly fragmented across multiple suppliers, potentially limiting negotiation leverage. Consider consolidating spending with preferred suppliers.")
                except Exception as e:
                    st.error(f"Unable to create supplier concentration chart: {str(e)}")
            else:
                st.info("Supplier concentration analysis requires both 'Supplier' and 'Amount' columns in your data.")
        
        # Spend over time analysis with enhanced storytelling
        st.subheader("Spending Patterns & Trends")
        st.markdown("*Identify seasonality, growth patterns, and spending anomalies to inform your procurement strategy*")
        
        # Convert dates to month periods for trend analysis - handle missing date columns
        if "Date" in filtered_data.columns:
            try:
                # Create a copy to avoid SettingWithCopyWarning
                filtered_data = filtered_data.copy()
                filtered_data["Month"] = pd.to_datetime(filtered_data["Date"]).dt.strftime('%Y-%m')
            except Exception as e:
                # If date conversion fails, create a default Month column
                filtered_data["Month"] = "Unknown"
        
        # Group by month and appropriate dimension
        group_dimension = "Supplier" if selected_category != "All Categories" else "Category"
        time_df = filtered_data.groupby(["Month", group_dimension])["Amount"].sum().reset_index()
        
        # Calculate trend statistics
        monthly_totals = filtered_data.groupby("Month")["Amount"].sum().reset_index()
        
        if len(monthly_totals) >= 3:
            first_month = monthly_totals.iloc[0]["Amount"] 
            last_month = monthly_totals.iloc[-1]["Amount"]
            change_pct = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
            
            # Create trend insight box
            if abs(change_pct) < 5:
                trend_color = "info"
                trend_message = f"📊 **Stable Spending Pattern**: Your spending has remained steady (±{abs(change_pct):.1f}%) over this period, suggesting consistent procurement activity."
            elif change_pct > 20:
                trend_color = "warning"
                trend_message = f"📈 **Significant Spending Growth**: Your spending has increased by {change_pct:.1f}% from first to last period. Investigate whether this reflects business growth or potential cost control issues."
            elif change_pct > 0:
                trend_color = "info"
                trend_message = f"📈 **Moderate Spending Growth**: Your spending has increased by {change_pct:.1f}% from first to last period, tracking slightly above inflation."
            elif change_pct < -20:
                trend_color = "success"
                trend_message = f"📉 **Major Spending Reduction**: Your spending has decreased by {abs(change_pct):.1f}% from first to last period. This significant reduction may reflect successful cost-saving initiatives."
            else:
                trend_color = "success"
                trend_message = f"📉 **Spending Reduction**: Your spending has decreased by {abs(change_pct):.1f}% from first to last period, which may indicate effective cost control measures."
            
            if trend_color == "info":
                st.info(trend_message)
            elif trend_color == "warning":
                st.warning(trend_message)
            else:
                st.success(trend_message)
        
        # Create the time series chart with enhanced title
        trend_title = f"Spending Evolution: How Your {selected_category if selected_category != 'All Categories' else 'Categories'} Spend Has Changed"
        
        fig3 = px.line(
            time_df,
            x="Month",
            y="Amount",
            color=group_dimension,
            title=trend_title,
            labels={"Amount": "Spend Amount ($)", "Month": "Month", group_dimension: group_dimension},
            markers=True
        )
        
        fig3.update_layout(
            title={
                'text': trend_title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend=dict(
                orientation="h",       # Horizontal legend
                yanchor="top",         # Anchor from top of legend box
                y=-0.2,                # Position below the chart
                xanchor="center",      # Center anchor
                x=0.5                  # Center position
            ),
            margin=dict(l=20, r=20, t=50, b=100),  # Extra bottom margin
            height=550                 # Taller chart
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Add actionable context based on the data
        if len(time_df[group_dimension].unique()) > 5:
            st.caption("**Pro Tip**: Focus on the top 3-5 spending items for clearer trend analysis. Too many lines can obscure important patterns.")
        
        # Spend distribution heatmap with enhanced storytelling
        st.subheader("Spend Distribution Matrix")
        st.markdown("*Identify spending hotspots and blind spots across your organization*")
        
        # Determine available dimensions for heatmap
        heatmap_dimensions = []
        for col in ['Category', 'SubCategory', 'BusinessUnit', 'Supplier', 'Region', 'Country']:
            if col in filtered_data.columns:
                heatmap_dimensions.append(col)
        
        # Default dimensions if available
        x_dimension = heatmap_dimensions[0] if len(heatmap_dimensions) > 0 else 'Category'
        y_dimension = heatmap_dimensions[1] if len(heatmap_dimensions) > 1 else 'BusinessUnit'
        
        # Set better dimensions if we have the standard columns
        if 'Category' in heatmap_dimensions:
            x_dimension = 'Category'
            if selected_category not in [None, 'All Categories'] and 'SubCategory' in heatmap_dimensions:
                x_dimension = 'SubCategory'
        
        if 'BusinessUnit' in heatmap_dimensions:
            y_dimension = 'BusinessUnit'
            if selected_bu not in [None, 'All Business Units'] and 'Supplier' in heatmap_dimensions:
                y_dimension = 'Supplier'
        
        # Create dynamic heatmap title
        heatmap_title = f"Spend Distribution by {x_dimension} and {y_dimension}"
        heatmap_subtitle = "Identify spending patterns and concentration areas"
        
        # Create heatmap for the appropriate dimensions with robust error handling
        try:
            # Ensure we have the column data we need
            if x_dimension in filtered_data.columns and y_dimension in filtered_data.columns and "Amount" in filtered_data.columns:
                fig4 = create_risk_heatmap(
                    filtered_data, 
                    x_dim=x_dimension, 
                    y_dim=y_dimension, 
                    value="Amount"
                )
            else:
                # Create a placeholder visualization with informative message
                import plotly.graph_objects as go
                
                fig4 = go.Figure()
                
                missing_cols = []
                if x_dimension not in filtered_data.columns:
                    missing_cols.append(x_dimension)
                if y_dimension not in filtered_data.columns:
                    missing_cols.append(y_dimension)
                if "Amount" not in filtered_data.columns:
                    missing_cols.append("Amount")
                
                error_message = f"Cannot create heatmap: Missing columns {', '.join(missing_cols)}"
                
                fig4.add_annotation(
                    text=error_message,
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=14, color="darkred")
                )
                fig4.update_layout(height=400)
        except Exception as e:
            # Fallback for any other error
            import plotly.graph_objects as go
            
            fig4 = go.Figure()
            fig4.add_annotation(
                text=f"Error creating heatmap. Please check your data format.",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="darkred")
            )
            fig4.update_layout(height=400)
        
        # Update layout with better title
        fig4.update_layout(
            title={
                'text': heatmap_title,
                'y':0.97,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        
        st.plotly_chart(fig4, use_container_width=True, key="heatmap_chart")
        st.caption(heatmap_subtitle)
        
        # Add insight based on the heatmap data
        # Get the top combinations
        if len(filtered_data) > 0:
            combo_data = filtered_data.groupby([x_dimension, y_dimension])["Amount"].sum().reset_index()
            combo_data = combo_data.sort_values("Amount", ascending=False)
            
            if len(combo_data) > 0:
                top_combo = combo_data.iloc[0]
                top_combo_pct = (top_combo["Amount"] / filtered_data["Amount"].sum() * 100)
                
                if top_combo_pct > 25:
                    st.info(f"🔍 **Strategic Focus Opportunity**: The combination of {top_combo[x_dimension]} and {top_combo[y_dimension]} represents {top_combo_pct:.1f}% of your total filtered spend. This concentration suggests a high-impact opportunity for strategic sourcing and optimization.")
        
        # AI-Powered Insights Section
        st.subheader("AI-Powered Insights")
        
        # Check if LLM is configured
        llm_provider = st.session_state.get("llm_provider", "None")
        use_llm = llm_provider != "None"
        
        # Create columns for the insights
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.subheader("Category Insights")
            if not use_llm:
                st.info("Enable AI model configuration in the sidebar to get enhanced insights")
                st.markdown(generate_category_insights(selected_category, filtered_data, use_llm=False))
            else:
                with st.spinner("Generating category insights..."):
                    insights = generate_category_insights(selected_category, filtered_data, use_llm=True)
                    st.markdown(insights)
        
        # Market Intelligence section removed as requested
        

