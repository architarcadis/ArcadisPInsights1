import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualizations import apply_standard_legend_style
from utils.visualizations import create_supplier_chart
from utils.llm_analysis import generate_supplier_insights

def show(session_state):
    """Display the Supplier Risk Analysis tab content"""
    st.title("🔍 Supplier Risk Analysis")
    
    # Get data from session state
    supplier_data = session_state.supplier_data
    performance_data = session_state.performance_data
    spend_data = session_state.spend_data
    
    # Filter controls
    st.subheader("Filter Suppliers")
    
    col1, col2, col3 = st.columns(3)
    
    # Function to get filtered data based on available columns
    def get_filtered_suppliers(data, filters):
        filtered = data.copy()
        for col, value in filters.items():
            if col in data.columns and value is not None and not (isinstance(value, str) and value.startswith("All ")):
                filtered = filtered[filtered[col] == value]
        return filtered
    
    filters = {}
    selected_category = None
    selected_country = None
    
    with col1:
        # Dynamic Category filter based on available data
        if "Category" in supplier_data.columns:
            categories = ["All Categories"] + sorted(supplier_data["Category"].unique().tolist())
            selected_category = st.selectbox("Select Category:", categories, key="risk_category")
            filters["Category"] = selected_category if selected_category != "All Categories" else None
        else:
            st.info("Category data not available in current dataset")
    
    with col2:
        # Dynamic Country/Region filter based on available data
        if "Country" in supplier_data.columns:
            countries = ["All Countries"] + sorted(supplier_data["Country"].unique().tolist())
            selected_country = st.selectbox("Select Country:", countries)
            filters["Country"] = selected_country if selected_country != "All Countries" else None
        elif "Region" in supplier_data.columns:
            regions = ["All Regions"] + sorted(supplier_data["Region"].unique().tolist())
            selected_region = st.selectbox("Select Region:", regions)
            filters["Region"] = selected_region if selected_region != "All Regions" else None
        else:
            st.info("Location data not available in current dataset")
    
    with col3:
        # Dynamic Performance Score Range slider if performance data is available
        if not performance_data.empty and "OverallScore" in performance_data.columns:
            # Round values to nearest 0.5 to match step size
            min_score = round(float(performance_data["OverallScore"].min()) * 2) / 2
            max_score = round(float(performance_data["OverallScore"].max()) * 2) / 2
            
            # Default to a reasonable range if available
            default_min = max(min_score, 5.0) if min_score < 5.0 else min_score
            default_max = max_score
            
            # Ensure min and max are different values
            if min_score == max_score:
                max_score += 0.5
            
            score_range = st.slider(
                "Performance Score Range:",
                min_value=min_score,
                max_value=max_score,
                value=(default_min, default_max),
                step=0.5
            )
        else:
            st.info("Performance score data not available")
            score_range = None
    
    # Apply filters to supplier data
    filtered_suppliers = get_filtered_suppliers(supplier_data, filters)
    
    # Check if we have performance data available
    if not performance_data.empty and "SupplierID" in performance_data.columns:
        # Determine the time/date column for performance data
        time_column = None
        for col_name in ["Quarter", "EvaluationDate", "Date", "Period"]:
            if col_name in performance_data.columns:
                time_column = col_name
                break
        
        if time_column:
            # Get latest performance scores
            latest_period = performance_data[time_column].max()
            latest_performance = performance_data[performance_data[time_column] == latest_period]
        else:
            # If no time column, use all performance data
            latest_performance = performance_data
            
        # Determine available performance metrics
        perf_metrics = []
        for metric in ["OverallScore", "DeliveryScore", "QualityScore", "ResponsivenessScore", 
                      "CostScore", "InnovationScore", "SustainabilityScore"]:
            if metric in performance_data.columns:
                perf_metrics.append(metric)
        
        if not perf_metrics:
            # If no standard metrics found, look for any numeric columns
            for col in performance_data.columns:
                if col != "SupplierID" and pd.api.types.is_numeric_dtype(performance_data[col]):
                    perf_metrics.append(col)
        
        # For merging, select only available columns
        merge_columns = ["SupplierID"] + perf_metrics
        available_merge_columns = [col for col in merge_columns if col in latest_performance.columns]
        
        # Merge supplier and performance data
        supplier_performance = filtered_suppliers.merge(
            latest_performance[available_merge_columns],
            on="SupplierID",
            how="left"
        )
        
        # Apply performance score filter if it exists
        if score_range is not None and "OverallScore" in supplier_performance.columns:
            min_score, max_score = score_range
            supplier_performance = supplier_performance[
                (supplier_performance["OverallScore"] >= min_score) &
                (supplier_performance["OverallScore"] <= max_score)
            ]
    else:
        # If no performance data, just use supplier data
        supplier_performance = filtered_suppliers.copy()
        perf_metrics = []
    
    # Main content area
    if len(supplier_performance) == 0:
        st.warning("No suppliers match the selected filters.")
    else:
        # Tiered Supplier Analysis
        st.subheader("Tiered Supplier Analysis")
        
        # Determine if we have tier ranking data
        has_tier_data = "TierRanking" in supplier_performance.columns
        
        # If tier data is not available, create a synthetic tier based on spend or revenue
        if not has_tier_data:
            if "AnnualRevenue" in supplier_performance.columns:
                # Sorting by revenue size
                supplier_performance = supplier_performance.sort_values("AnnualRevenue", ascending=False)
                
                # Create tier groups based on percentiles (top 10% = Tier 1, next 20% = Tier 2, rest = Tier 3)
                top_10_percent = int(len(supplier_performance) * 0.1)
                next_20_percent = int(len(supplier_performance) * 0.3)
                
                supplier_performance["TierRanking"] = "Tier 3"
                supplier_performance.iloc[:top_10_percent, supplier_performance.columns.get_loc("TierRanking")] = "Tier 1"
                supplier_performance.iloc[top_10_percent:next_20_percent, supplier_performance.columns.get_loc("TierRanking")] = "Tier 2"
                
                tier_message = "Tiers calculated based on Annual Revenue"
            elif "Amount" in supplier_performance.columns or any(col for col in supplier_performance.columns if "Spend" in col):
                # Find the spend column
                spend_col = "Amount" if "Amount" in supplier_performance.columns else next(col for col in supplier_performance.columns if "Spend" in col)
                
                # Group by supplier ID and sum spend
                spend_by_supplier = supplier_performance.groupby("SupplierID")[spend_col].sum().reset_index()
                spend_by_supplier = spend_by_supplier.sort_values(spend_col, ascending=False)
                
                # Create tier groups based on Pareto principle (80/20 rule)
                total_spend = spend_by_supplier[spend_col].sum()
                cumulative_spend = spend_by_supplier[spend_col].cumsum()
                spend_percentage = cumulative_spend / total_spend
                
                # Tier 1: Top suppliers accounting for 80% of spend
                # Tier 2: Next group accounting for 15% of spend
                # Tier 3: Remaining suppliers accounting for 5% of spend
                spend_by_supplier["TierRanking"] = "Tier 3"
                spend_by_supplier.loc[spend_percentage <= 0.8, "TierRanking"] = "Tier 1"
                spend_by_supplier.loc[(spend_percentage > 0.8) & (spend_percentage <= 0.95), "TierRanking"] = "Tier 2"
                
                # Merge back to the main dataset
                supplier_performance = supplier_performance.merge(
                    spend_by_supplier[["SupplierID", "TierRanking"]],
                    on="SupplierID",
                    how="left"
                )
                
                tier_message = "Tiers calculated based on Spend (Pareto principle: Tier 1 = 80% of spend, Tier 2 = next 15%, Tier 3 = remaining 5%)"
            else:
                # If no financial data, create equal tiers
                supplier_performance["TierRanking"] = "Tier 3"
                third = len(supplier_performance) // 3
                supplier_performance.iloc[:third, supplier_performance.columns.get_loc("TierRanking")] = "Tier 1"
                supplier_performance.iloc[third:2*third, supplier_performance.columns.get_loc("TierRanking")] = "Tier 2"
                
                tier_message = "Tiers calculated based on equal distribution (no financial data available)"
            
            st.info(tier_message)
            has_tier_data = True
        
        # Create tier summary statistics
        if has_tier_data:
            tier_summary = supplier_performance.groupby("TierRanking").agg({
                "SupplierID": "count"
            }).reset_index()
            
            tier_summary = tier_summary.rename(columns={"SupplierID": "Count"})
            
            # Add risk metrics if available
            if "RiskCategory" in supplier_performance.columns:
                risk_by_tier = supplier_performance.groupby(["TierRanking", "RiskCategory"]).size().unstack(fill_value=0)
                
                # Calculate risk percentages
                for risk_category in risk_by_tier.columns:
                    tier_summary[f"{risk_category} Risk %"] = 0
                    
                for idx, tier in tier_summary.iterrows():
                    if tier["TierRanking"] in risk_by_tier.index:
                        total = risk_by_tier.loc[tier["TierRanking"]].sum()
                        for risk_category in risk_by_tier.columns:
                            tier_summary.at[idx, f"{risk_category} Risk %"] = round((risk_by_tier.loc[tier["TierRanking"], risk_category] / total) * 100)
            
            # Add performance metrics if available
            for metric in perf_metrics:
                if metric in supplier_performance.columns:
                    metric_by_tier = supplier_performance.groupby("TierRanking")[metric].mean()
                    
                    for idx, tier in tier_summary.iterrows():
                        if tier["TierRanking"] in metric_by_tier.index:
                            tier_summary.at[idx, f"Avg {metric}"] = round(metric_by_tier[tier["TierRanking"]], 2)
            
            # Display tier summary
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.write("Supplier Tier Summary")
                st.dataframe(tier_summary, use_container_width=True)
            
            with col2:
                # Create tiered supplier distribution chart
                tier_counts = supplier_performance["TierRanking"].value_counts().reset_index()
                tier_counts.columns = ["Tier", "Count"]
                
                # Sort tiers in correct order
                tier_order = ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]
                tier_counts["Tier"] = pd.Categorical(tier_counts["Tier"], categories=tier_order, ordered=True)
                tier_counts = tier_counts.sort_values("Tier")
                
                # Create colors based on tier (Tier 1 = darkest)
                colors = ["#FF6B35", "#FF8C61", "#FFAC8C", "#FFCDB8", "#FFE6DD"]
                
                fig = px.bar(
                    tier_counts,
                    x="Tier",
                    y="Count",
                    title="Suppliers by Tier",
                    color="Tier",
                    color_discrete_map={tier: color for tier, color in zip(tier_order, colors)},
                    text="Count"
                )
                
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
        
        # Risk Visualization by Tier
        st.subheader("Risk Profile by Supplier Tier")
        
        if has_tier_data:
            # Risk Matrix by Tier
            if "RiskCategory" in supplier_performance.columns and "RiskScore" in supplier_performance.columns:
                # Tier-based risk matrix
                st.write("Risk Distribution by Tier")
                
                tier_risk_fig = px.scatter(
                    supplier_performance,
                    x="RiskScore",
                    y="TierRanking",
                    color="RiskCategory",
                    size="RiskScore",
                    hover_name="SupplierName",
                    title="Risk Profile by Supplier Tier",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    labels={"RiskScore": "Risk Score (Higher = More Risk)", "TierRanking": "Supplier Tier", "RiskCategory": "Risk Category"}
                )
                
                # Position the legend directly below the chart with simple formatting
                tier_risk_fig.update_layout(
                    height=500,  # Taller chart
                    legend=dict(
                        orientation="h",         # Horizontal orientation
                        y=-0.4,                  # More space below
                        x=0.5,                   # Centered
                        xanchor="center",
                        yanchor="top",
                        font=dict(size=9)        # Smaller font
                    ),
                    margin=dict(b=150)           # Much more bottom margin
                )
                
                st.plotly_chart(tier_risk_fig, use_container_width=True)
            elif any(metric in supplier_performance.columns for metric in perf_metrics):
                # If we have performance metrics but no risk scores, show performance by tier
                available_metric = next(metric for metric in perf_metrics if metric in supplier_performance.columns)
                
                tier_perf_fig = px.box(
                    supplier_performance,
                    x="TierRanking",
                    y=available_metric,
                    color="TierRanking",
                    title=f"Performance Distribution by Tier ({available_metric})",
                    labels={"TierRanking": "Supplier Tier"}
                )
                
                # Position the legend directly below the chart with simple formatting
                tier_perf_fig.update_layout(
                    height=500,  # Taller chart
                    legend=dict(
                        orientation="h",         # Horizontal orientation
                        y=-0.4,                  # More space below
                        x=0.5,                   # Centered
                        xanchor="center",
                        yanchor="top"
                    ),
                    margin=dict(b=150)           # Much more bottom margin
                )
                
                st.plotly_chart(tier_perf_fig, use_container_width=True)
            else:
                st.info("Risk or performance metrics not available in the current dataset")
        
        # Payment Terms Analysis Section
        st.subheader("Payment Terms Analysis")
        
        # Check if payment terms information is available
        has_payment_terms = "PaymentTerms" in supplier_performance.columns
        
        if has_payment_terms:
            # Group suppliers by payment terms
            payment_terms_data = supplier_performance.dropna(subset=["PaymentTerms"])
            payment_terms_counts = payment_terms_data.groupby("PaymentTerms").size().reset_index(name="Count")
            payment_terms_counts = payment_terms_counts.sort_values("Count", ascending=False)
            
            # Extract days from payment terms for analysis
            payment_terms_data["PaymentDays"] = 0
            for idx, row in payment_terms_data.iterrows():
                payment_terms = row["PaymentTerms"]
                if isinstance(payment_terms, str) and "Net" in payment_terms:
                    try:
                        payment_days = int(''.join(filter(str.isdigit, payment_terms)))
                        payment_terms_data.at[idx, "PaymentDays"] = payment_days
                    except:
                        pass
            
            # Calculate average payment days
            avg_payment_days = payment_terms_data["PaymentDays"].mean()
            
            # Display payment terms distribution
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.write("Distribution of Payment Terms")
                st.dataframe(payment_terms_counts, use_container_width=True)
                
                # Payment term statistics
                payment_stats = {
                    "Average Payment Days": f"{avg_payment_days:.1f}",
                    "Most Common Terms": payment_terms_counts.iloc[0]["PaymentTerms"],
                    "Suppliers with No Terms": len(supplier_performance) - len(payment_terms_data)
                }
                
                st.write("Payment Terms Statistics")
                st.dataframe(pd.DataFrame([payment_stats]), use_container_width=True)
                
                # Add payment terms optimization insights
                if avg_payment_days > 30:
                    st.success(f"Average payment terms of {avg_payment_days:.1f} days offers good cash flow advantage.")
                else:
                    st.warning(f"Current average payment terms of {avg_payment_days:.1f} days may present cash flow challenges. Consider negotiating longer terms with strategic suppliers.")
            
            with col2:
                # Create visualization of payment terms distribution
                fig = px.bar(
                    payment_terms_counts.head(10),
                    x="PaymentTerms",
                    y="Count",
                    title="Payment Terms Distribution",
                    color="Count",
                    color_continuous_scale="Oranges",
                    text="Count"
                )
                
                # Position colorbar at bottom horizontally
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        orientation="h",
                        len=0.8
                    ),
                    margin=dict(l=20, r=20, t=50, b=100),
                    height=500
                )
                
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # If we have tier data, show payment terms by tier
                if "TierRanking" in supplier_performance.columns:
                    payment_by_tier = payment_terms_data.groupby(["TierRanking"])["PaymentDays"].mean().reset_index()
                    payment_by_tier = payment_by_tier.sort_values("PaymentDays", ascending=False)
                    
                    tier_fig = px.bar(
                        payment_by_tier,
                        x="TierRanking",
                        y="PaymentDays",
                        title="Average Payment Days by Supplier Tier",
                        color="PaymentDays",
                        color_continuous_scale="Oranges",
                        text=payment_by_tier["PaymentDays"].round(1)
                    )
                    
                    # Position colorbar at bottom horizontally
                    tier_fig.update_layout(
                        coloraxis_colorbar=dict(
                            yanchor="top",
                            y=-0.2,
                            xanchor="center",
                            x=0.5,
                            orientation="h",
                            len=0.8
                        ),
                        margin=dict(l=20, r=20, t=50, b=100),
                        height=500
                    )
                    
                    tier_fig.update_traces(textposition='outside')
                    st.plotly_chart(tier_fig, use_container_width=True)
                    
                    # Add strategic insights
                    if payment_by_tier["TierRanking"].nunique() > 1:
                        tier1_days = payment_by_tier[payment_by_tier["TierRanking"] == "Tier 1"]["PaymentDays"].values
                        tier3_days = payment_by_tier[payment_by_tier["TierRanking"] == "Tier 3"]["PaymentDays"].values
                        
                        if len(tier1_days) > 0 and len(tier3_days) > 0 and tier1_days[0] < tier3_days[0]:
                            st.info("**Payment Terms Optimization Opportunity**: Strategic (Tier 1) suppliers have shorter payment terms than non-strategic suppliers. Consider negotiating improved terms with key suppliers.")
        else:
            st.info("Payment terms data is not available in the current dataset. Upload supplier master data with payment terms information to enable this analysis.")
        
        # Supplier Performance Dashboard (original content)
        st.subheader("Supplier Performance Dashboard")
        
        # Check if we have performance metrics available
        if perf_metrics:
            # Create tabs for available performance metrics
            tab_names = []
            for metric in perf_metrics:
                # Format metric name for display
                display_name = metric.replace("Score", "").replace("_", " ").title()
                tab_names.append(display_name)
            
            # Create tabs dynamically based on available metrics
            performance_tabs = st.tabs(tab_names)
            
            # Create charts for each metric
            for i, metric in enumerate(perf_metrics):
                with performance_tabs[i]:
                    try:
                        # Use our flexible chart function
                        fig = create_supplier_chart(
                            performance_data, 
                            filtered_suppliers, 
                            metric=metric,
                            title=f"Top Suppliers by {tab_names[i]} Performance"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Unable to create chart for {tab_names[i]}: {str(e)}")
        else:
            # No performance metrics available
            st.info("Performance metrics are not available in the current dataset. Upload performance data to see supplier performance analysis.")
        
        # Performance Trend Analysis
        st.subheader("Performance Trend Analysis")
        
        # Check if we have performance data and it's not empty
        if not performance_data.empty and len(supplier_performance) > 0 and "SupplierID" in supplier_performance.columns:
            # Supplier selector for trend analysis
            try:
                selected_supplier_id = st.selectbox(
                    "Select Supplier for Trend Analysis:",
                    options=supplier_performance["SupplierID"].tolist(),
                    format_func=lambda x: supplier_performance[supplier_performance["SupplierID"] == x]["SupplierName"].iloc[0] 
                        if "SupplierName" in supplier_performance.columns 
                        else x
                )
                
                # Get performance history for selected supplier
                supplier_history = performance_data[performance_data["SupplierID"] == selected_supplier_id]
                
                # Determine time dimension column
                time_dimension = None
                for col in ["Quarter", "EvaluationDate", "Date", "Period"]:
                    if col in supplier_history.columns:
                        time_dimension = col
                        break
                
                if len(supplier_history) > 0 and time_dimension is not None:
                    # Determine available metrics
                    available_metrics = []
                    for metric in ["OverallScore", "DeliveryScore", "QualityScore", "ResponsivenessScore", 
                                  "CostScore", "InnovationScore", "SustainabilityScore"]:
                        if metric in supplier_history.columns:
                            available_metrics.append(metric)
                    
                    if available_metrics:
                        # Create a long format dataframe for the line chart
                        history_long = pd.melt(
                            supplier_history,
                            id_vars=["SupplierID", time_dimension],
                            value_vars=available_metrics,
                            var_name="Metric",
                            value_name="Score"
                        )
            
                        # Create a more readable label for the metrics
                        metric_labels = {}
                        for metric in available_metrics:
                            # Convert camelCase to Space Separated Text
                            label = metric.replace("Score", "").replace("_", " ").title()
                            metric_labels[metric] = label
                        
                        history_long["Metric"] = history_long["Metric"].replace(metric_labels)
                        
                        # Get supplier name for title
                        if "SupplierName" in supplier_performance.columns:
                            supplier_name = supplier_performance[supplier_performance["SupplierID"] == selected_supplier_id]["SupplierName"].iloc[0]
                        else:
                            supplier_name = f"Supplier {selected_supplier_id}"
                        
                        # Create the trend chart
                        fig5 = px.line(
                            history_long,
                            x=time_dimension,
                            y="Score",
                            color="Metric",
                            title=f"Performance Trend for {supplier_name}",
                            labels={"Score": "Performance Score", time_dimension: time_dimension, "Metric": "Metric"},
                            markers=True
                        )
                        
                        # Auto-scale y-axis based on data range, with some padding
                        max_score = history_long["Score"].max()
                        min_score = history_long["Score"].min()
                        y_range = [max(0, min_score - 0.5), min(10.5, max_score + 0.5)]
                        
                        fig5.update_layout(
                            yaxis=dict(range=y_range),
                            hovermode="x unified"
                        )
                        
                        st.plotly_chart(fig5, use_container_width=True)
                    else:
                        st.info("No performance metrics available for trend analysis")
                else:
                    st.info(f"No performance history available for this supplier")
            except Exception as e:
                st.error(f"Error creating performance trend chart: {str(e)}")
        else:
            st.info("Performance data is required for trend analysis. Please upload supplier performance data.")
        
        # Public Risk Indicators
        st.subheader("Public Risk Indicators (Simulated)")
        
        # Create simulated risk indicators
        supplier_performance["FinancialRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["ESGRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["ComplianceRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        supplier_performance["GeopoliticalRisk"] = np.random.uniform(1, 10, len(supplier_performance))
        
        # Create a risk score (lower is better for risk scores)
        supplier_performance["RiskScore"] = (
            supplier_performance["FinancialRisk"] * 0.4 +
            supplier_performance["ESGRisk"] * 0.3 +
            supplier_performance["ComplianceRisk"] * 0.2 +
            supplier_performance["GeopoliticalRisk"] * 0.1
        )
        
        # Create two columns layout
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            # Create a scatter plot of performance vs risk
            fig6 = px.scatter(
                supplier_performance,
                x="RiskScore",
                y="OverallScore",
                color="Category",
                size="AnnualRevenue",
                hover_name="SupplierName",
                title="Supplier Performance vs. Risk Matrix",
                labels={
                    "RiskScore": "Risk Score (Lower is Better)",
                    "OverallScore": "Performance Score (Higher is Better)",
                    "Category": "Category"
                },
                custom_data=["SupplierID", "SupplierName"]
            )
            
            # Directly position legend at bottom with clear settings
            fig6.update_layout(
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
            
            # Add quadrant lines
            fig6.add_hline(y=7.5, line_width=1, line_dash="dash", line_color="gray")
            fig6.add_vline(x=5, line_width=1, line_dash="dash", line_color="gray")
            
            # Add quadrant annotations
            fig6.add_annotation(x=2.5, y=8.75, text="Strategic Partners", showarrow=False, font=dict(size=12, color="green"))
            fig6.add_annotation(x=7.5, y=8.75, text="Performance Concerns", showarrow=False, font=dict(size=12, color="orange"))
            fig6.add_annotation(x=2.5, y=3.75, text="Reliable", showarrow=False, font=dict(size=12, color="blue"))
            fig6.add_annotation(x=7.5, y=3.75, text="High Risk", showarrow=False, font=dict(size=12, color="red"))
            
            st.plotly_chart(fig6, use_container_width=True)
        
        with risk_col2:
            # Top 10 suppliers by risk
            high_risk_suppliers = supplier_performance.sort_values("RiskScore", ascending=False).head(10)
            
            fig7 = px.bar(
                high_risk_suppliers,
                y="SupplierName",
                x="RiskScore",
                orientation="h",
                color="RiskScore",
                title="Top 10 Suppliers by Risk Score",
                labels={"SupplierName": "Supplier", "RiskScore": "Risk Score"},
                color_continuous_scale="Oranges_r"  # Reversed scale since higher risk is worse
            )
            
            fig7.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig7, use_container_width=True)
        
        # Detailed Risk Profile for a selected supplier
        st.subheader("Detailed Risk Profile")
        
        selected_supplier_id_risk = st.selectbox(
            "Select Supplier for Detailed Risk Analysis:",
            options=supplier_performance["SupplierID"].tolist(),
            format_func=lambda x: supplier_performance[supplier_performance["SupplierID"] == x]["SupplierName"].iloc[0],
            key="risk_supplier_selector"
        )
        
        # Get the selected supplier data
        selected_supplier = supplier_performance[supplier_performance["SupplierID"] == selected_supplier_id_risk].iloc[0]
        
        # Create columns for risk profile
        profile_col1, profile_col2 = st.columns(2)
        
        with profile_col1:
            # Create a radar chart for risk dimensions
            risk_dimensions = ["FinancialRisk", "ESGRisk", "ComplianceRisk", "GeopoliticalRisk"]
            risk_values = [selected_supplier[dim] for dim in risk_dimensions]
            
            fig8 = go.Figure()
            
            fig8.add_trace(go.Scatterpolar(
                r=risk_values,
                theta=["Financial", "ESG", "Compliance", "Geopolitical"],
                fill='toself',
                name='Risk Profile',
                line_color='orange'
            ))
            
            fig8.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=False,
                title=f"Risk Profile for {selected_supplier['SupplierName']}"
            )
            
            st.plotly_chart(fig8, use_container_width=True)
        
        with profile_col2:
            # Create a gauge chart for overall risk
            risk_score = selected_supplier["RiskScore"]
            
            fig9 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": "Overall Risk Score"},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 3.33], 'color': "green"},
                        {'range': [3.33, 6.66], 'color': "yellow"},
                        {'range': [6.66, 10], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score
                    }
                }
            ))
            
            st.plotly_chart(fig9, use_container_width=True)
        
        # Risk alerts and recommendations
        st.subheader("Risk Alerts & Recommendations")
        
        # Simulated risk alerts based on the selected supplier
        alerts = []
        
        if selected_supplier["FinancialRisk"] > 7:
            alerts.append({
                "type": "Financial",
                "severity": "High",
                "description": f"Financial stability concerns detected for {selected_supplier['SupplierName']}.",
                "recommendation": "Consider requiring financial guarantees or adjusting payment terms."
            })
        
        if selected_supplier["ESGRisk"] > 7:
            alerts.append({
                "type": "ESG",
                "severity": "High",
                "description": f"Environmental or social compliance issues identified for {selected_supplier['SupplierName']}.",
                "recommendation": "Request ESG compliance documentation and schedule an audit."
            })
        
        if selected_supplier["DeliveryScore"] < 6:
            alerts.append({
                "type": "Performance",
                "severity": "Medium",
                "description": f"Consistent delivery issues with {selected_supplier['SupplierName']}.",
                "recommendation": "Implement a performance improvement plan with monthly reviews."
            })
        
        if len(alerts) == 0:
            st.success(f"No significant risk alerts for {selected_supplier['SupplierName']}.")
        else:
            for alert in alerts:
                severity_color = "red" if alert["severity"] == "High" else ("orange" if alert["severity"] == "Medium" else "blue")
                st.warning(
                    f"**{alert['type']} Risk - {alert['severity']} Severity**\n\n"
                    f"{alert['description']}\n\n"
                    f"**Recommendation:** {alert['recommendation']}"
                )
        
        # AI-Powered Supplier Risk Analysis
        st.subheader("AI-Powered Supplier Risk Analysis")
        
        # Check if LLM is configured
        llm_provider = st.session_state.get("llm_provider", "None")
        use_llm = llm_provider != "None"
        
        if not use_llm:
            st.info("Enable AI model configuration in the sidebar to get enhanced supplier risk analysis")
        else:
            with st.spinner("Generating advanced risk insights..."):
                # Get the supplier insights using LLM
                supplier_insights = generate_supplier_insights(
                    selected_supplier_id_risk, 
                    supplier_data, 
                    performance_data, 
                    spend_data, 
                    use_llm=True
                )
                
                # Display the AI-generated insights
                st.markdown(supplier_insights)
                
                # Ask user if they want to generate a risk mitigation plan
                if st.button("Generate Risk Mitigation Plan", key="gen_risk_plan"):
                    with st.spinner("Generating comprehensive risk mitigation plan..."):
                        # This would call an additional LLM function to generate a risk plan
                        st.success("Risk mitigation plan functionality will be implemented in the next update")
                        st.info("This feature would generate a detailed risk mitigation plan using AI analysis of the supplier's risk profile")
