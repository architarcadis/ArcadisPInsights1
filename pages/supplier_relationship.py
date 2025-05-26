import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.visualizations import apply_standard_legend_style

def show(session_state):
    """Display the Supplier Relationship Management tab content"""
    st.title("🤝 Supplier Relationship Management")
    
    # Get data from session state
    supplier_data = session_state.supplier_data
    performance_data = session_state.performance_data
    spend_data = session_state.spend_data
    contract_data = session_state.contract_data
    
    # Supplier selector
    st.subheader("Supplier 360° View")
    
    # Dropdown to select supplier
    selected_supplier_id = st.selectbox(
        "Select Supplier:",
        options=supplier_data["SupplierID"].tolist(),
        format_func=lambda x: supplier_data[supplier_data["SupplierID"] == x]["SupplierName"].iloc[0]
    )
    
    # Get supplier details
    supplier_details = supplier_data[supplier_data["SupplierID"] == selected_supplier_id].iloc[0]
    
    # Create columns for supplier details and metrics
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"### {supplier_details['SupplierName']}")
        st.markdown(f"**Category:** {supplier_details['Category']}")
        st.markdown(f"**Location:** {supplier_details['City']}, {supplier_details['Country']}")
        st.markdown(f"**Contact:** {supplier_details['ContactName']}")
        st.markdown(f"**Email:** {supplier_details['ContactEmail']}")
        st.markdown(f"**Phone:** {supplier_details['ContactPhone']}")
        st.markdown(f"**Relationship Since:** {supplier_details['RelationshipStartDate']}")
        
        # Add payment terms information
        if 'PaymentTerms' in supplier_details and not pd.isna(supplier_details['PaymentTerms']):
            payment_terms = supplier_details['PaymentTerms']
            # Extract days from common payment terms formats (Net 30, Net 45, etc.)
            payment_days = None
            if isinstance(payment_terms, str) and "Net" in payment_terms:
                try:
                    payment_days = int(''.join(filter(str.isdigit, payment_terms)))
                except:
                    pass
            
            # Display payment terms as text
            st.markdown(f"**Payment Terms:** {payment_terms}")
            
            # Create a more readable visual representation of payment terms using a horizontal bar
            if payment_days:
                # Determine color and category based on days
                if payment_days <= 15:
                    term_color = "#26B887"  # Green - Excellent
                    term_category = "Excellent"
                elif payment_days <= 30:
                    term_color = "#9DB839"  # Yellow-Green - Standard
                    term_category = "Standard"
                elif payment_days <= 60:
                    term_color = "#DDBE12"  # Amber - Extended
                    term_category = "Extended"
                else:
                    term_color = "#D96B0B"  # Orange-Red - Long
                    term_category = "Long"
                
                # Create a custom horizontal progress bar for payment terms
                st.markdown(f"""
                <style>
                .payment-terms-container {{
                    margin-top: 10px;
                    margin-bottom: 20px;
                }}
                .payment-terms-label {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }}
                .payment-terms-track {{
                    height: 10px;
                    background-color: rgba(50, 50, 50, 0.3);
                    border-radius: 5px;
                    position: relative;
                }}
                .payment-terms-progress {{
                    height: 10px;
                    width: {min(100, payment_days / 90 * 100)}%;
                    background-color: {term_color};
                    border-radius: 5px;
                }}
                .payment-terms-value {{
                    margin-top: 8px;
                    font-weight: 600;
                    font-size: 1.2rem;
                    color: {term_color};
                }}
                .payment-terms-range {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.8rem;
                    color: rgba(255, 255, 255, 0.7);
                    margin-top: 3px;
                }}
                .payment-terms-category {{
                    background-color: {term_color};
                    color: rgba(0, 0, 0, 0.8);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    display: inline-block;
                    margin-left: 10px;
                    vertical-align: middle;
                }}
                </style>
                
                <div class="payment-terms-container">
                    <div class="payment-terms-label">
                        <span>Payment Terms</span>
                        <div class="payment-terms-value">{payment_days} days <span class="payment-terms-category">{term_category}</span></div>
                    </div>
                    <div class="payment-terms-track">
                        <div class="payment-terms-progress"></div>
                    </div>
                    <div class="payment-terms-range">
                        <span>Immediate</span>
                        <span>30 days</span>
                        <span>60 days</span>
                        <span>90+ days</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Calculate supplier metrics
        
        # 1. Performance metrics
        latest_quarter = performance_data["Quarter"].max()
        latest_performance = performance_data[
            (performance_data["SupplierID"] == selected_supplier_id) & 
            (performance_data["Quarter"] == latest_quarter)
        ]
        
        if len(latest_performance) > 0:
            overall_score = latest_performance["OverallScore"].iloc[0]
            delivery_score = latest_performance["DeliveryScore"].iloc[0]
            quality_score = latest_performance["QualityScore"].iloc[0]
            responsiveness_score = latest_performance["ResponsivenessScore"].iloc[0]
        else:
            overall_score = delivery_score = quality_score = responsiveness_score = "N/A"
        
        # 2. Spend metrics
        supplier_spend = spend_data[spend_data["Supplier"] == supplier_details["SupplierName"]]
        total_spend = supplier_spend["Amount"].sum() if len(supplier_spend) > 0 else 0
        
        # 3. Contract metrics
        supplier_contracts = contract_data[contract_data["SupplierID"] == selected_supplier_id]
        active_contracts = len(supplier_contracts[supplier_contracts["Status"] == "Active"])
        
        # Use a completely different approach for metrics - custom HTML/CSS cards
        # Determine supplier tier
        if len(supplier_spend) > 0:
            spend_percentile = (spend_data.groupby("Supplier")["Amount"].sum() <= total_spend).mean() * 100
            tier = "Strategic" if spend_percentile >= 80 else ("Key" if spend_percentile >= 50 else "Standard")
            tier_color = "#FF6B35" if tier == "Strategic" else ("#FFA07A" if tier == "Key" else "#E9967A")
        else:
            tier = "Unknown"
            tier_color = "#A9A9A9"
            
        # Format spend amount
        if total_spend > 1000000:
            spend_display = f"${total_spend/1000000:.1f}M"
        elif total_spend > 1000:
            spend_display = f"${total_spend/1000:.1f}K"
        else:
            spend_display = f"${total_spend:.0f}"
        
        # Format overall score
        score_display = f"{overall_score:.1f}" if isinstance(overall_score, (int, float)) else "N/A"
        
        # Create HTML/CSS card-based metrics
        st.markdown("""
        <style>
        .metric-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: rgba(30, 30, 30, 0.7);
            border-radius: 8px;
            padding: 16px;
            min-width: 120px;
            flex: 1;
            border-left: 4px solid #FF6B35;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        .metric-name {
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 8px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 4px;
        }
        .supplier-tier {
            border-left: 4px solid """ + tier_color + """;
        }
        </style>
        
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-name">Overall Score</div>
                <div class="metric-value">""" + score_display + """</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">Total Spend</div>
                <div class="metric-value">""" + spend_display + """</div>
            </div>
            <div class="metric-card">
                <div class="metric-name">Active Contracts</div>
                <div class="metric-value">""" + str(active_contracts) + """</div>
            </div>
            <div class="metric-card supplier-tier">
                <div class="metric-name">Supplier Tier</div>
                <div class="metric-value">""" + tier + """</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance scores chart
    if isinstance(overall_score, (int, float)):
        # Create a bullet chart for performance metrics
        fig1 = go.Figure()
        
        # Add performance metrics as bullet charts
        metrics = [
            {"name": "Overall", "score": overall_score},
            {"name": "Delivery", "score": delivery_score},
            {"name": "Quality", "score": quality_score},
            {"name": "Responsiveness", "score": responsiveness_score}
        ]
        
        for i, metric in enumerate(metrics):
            fig1.add_trace(go.Indicator(
                mode="number+gauge",
                value=metric["score"],
                domain={'x': [0, 1], 'y': [i/len(metrics), (i+0.8)/len(metrics)]},
                title={'text': metric["name"], 'font': {'size': 14}},
                gauge={
                    'shape': "bullet",
                    'axis': {'range': [0, 10]},
                    'threshold': {
                        'line': {'color': "red", 'width': 2},
                        'thickness': 0.75,
                        'value': 7
                    },
                    'steps': [
                        {'range': [0, 5], 'color': "lightgray"},
                        {'range': [5, 7], 'color': "gray"}
                    ],
                    'bar': {'color': "#FF6B35"}
                },
                number = {
                    'font': {'size': 26, 'color': 'white'},
                    'valueformat': '.1f'  # Format to 1 decimal place without suffix
                }
            ))
        
        fig1.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        # Apply standardized horizontal legend style
        apply_standard_legend_style(fig1)
        
        st.plotly_chart(fig1, use_container_width=True, key="performance_score_chart")
    
    # Create tabs for detailed information
    tab1, tab2, tab3, tab4 = st.tabs(["Performance Trend", "Spend Analysis", "Contracts", "Relationship Notes"])
    
    # Performance Trend Tab
    with tab1:
        # Get performance history for the selected supplier
        supplier_history = performance_data[performance_data["SupplierID"] == selected_supplier_id]
        
        if len(supplier_history) > 0:
            # Create a long format dataframe for the line chart
            metrics = ["OverallScore", "DeliveryScore", "QualityScore", "ResponsivenessScore"]
            history_long = pd.melt(
                supplier_history,
                id_vars=["SupplierID", "Quarter"],
                value_vars=metrics,
                var_name="Metric",
                value_name="Score"
            )
            
            # Create a more readable label for the metrics
            history_long["Metric"] = history_long["Metric"].replace({
                "OverallScore": "Overall",
                "DeliveryScore": "Delivery",
                "QualityScore": "Quality",
                "ResponsivenessScore": "Responsiveness"
            })
            
            # Create the trend chart
            fig2 = px.line(
                history_long,
                x="Quarter",
                y="Score",
                color="Metric",
                title=f"Performance Trend for {supplier_details['SupplierName']}",
                labels={"Score": "Performance Score (1-10)", "Quarter": "Quarter", "Metric": "Metric"},
                markers=True
            )
            
            fig2.update_layout(
                yaxis=dict(range=[0, 10.5]),
                hovermode="x unified",
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
            # Legend is already set to be horizontal at the bottom
            
            st.plotly_chart(fig2, use_container_width=True, key="perf_trend_chart")
            
            # Display comments in a timeline
            st.subheader("Performance Assessment Timeline")
            
            supplier_history_sorted = supplier_history.sort_values("Quarter", ascending=False)
            for _, row in supplier_history_sorted.iterrows():
                st.markdown(f"**{row['Quarter']}:** {row['Comments']} (Score: {row['OverallScore']}/10)")
        else:
            st.warning("No performance history available for this supplier.")
    
    # Spend Analysis Tab
    with tab2:
        # Filter spend data for the selected supplier
        supplier_spend = spend_data[spend_data["Supplier"] == supplier_details["SupplierName"]]
        
        if len(supplier_spend) > 0:
            # Calculate total spend
            total_spend = supplier_spend["Amount"].sum()
            
            # Create columns for metrics
            spend_col1, spend_col2 = st.columns(2)
            
            with spend_col1:
                # Spend by category
                spend_by_category = supplier_spend.groupby("Category")["Amount"].sum().reset_index()
                spend_by_category = spend_by_category.sort_values("Amount", ascending=False)
                
                fig3 = px.pie(
                    spend_by_category,
                    values="Amount",
                    names="Category",
                    title=f"Spend by Category with {supplier_details['SupplierName']}",
                    color_discrete_sequence=px.colors.sequential.Oranges
                )
                
                # Manually position legend at bottom
                fig3.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.5,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=9),
                        bgcolor="rgba(30,30,30,0.7)",
                        bordercolor="rgba(255,255,255,0.2)",
                        borderwidth=1
                    ),
                    margin=dict(l=20, r=20, t=50, b=120)
                )
                
                st.plotly_chart(fig3, use_container_width=True, key="spend_category_chart")
            
            with spend_col2:
                # Spend trend over time - use proper DataFrame methods to avoid warnings
                supplier_spend = supplier_spend.copy()  # Create a copy to avoid the SettingWithCopyWarning
                supplier_spend.loc[:, "Month"] = pd.to_datetime(supplier_spend["Date"]).dt.strftime('%Y-%m')
                spend_by_month = supplier_spend.groupby("Month")["Amount"].sum().reset_index()
                
                fig4 = px.line(
                    spend_by_month,
                    x="Month",
                    y="Amount",
                    title=f"Spend Trend with {supplier_details['SupplierName']}",
                    labels={"Amount": "Spend Amount ($)", "Month": "Month"},
                    markers=True
                )
                
                st.plotly_chart(fig4, use_container_width=True, key="spend_trend_chart")
            
            # Spend by business unit
            spend_by_bu = supplier_spend.groupby("BusinessUnit")["Amount"].sum().reset_index()
            spend_by_bu = spend_by_bu.sort_values("Amount", ascending=False)
            
            fig5 = px.bar(
                spend_by_bu,
                x="BusinessUnit",
                y="Amount",
                title=f"Spend by Business Unit with {supplier_details['SupplierName']}",
                labels={"Amount": "Spend Amount ($)", "BusinessUnit": "Business Unit"},
                color="Amount",
                color_continuous_scale="Oranges"
            )
            
            st.plotly_chart(fig5, use_container_width=True, key="spend_by_bu_chart")
            
            # Invoice table
            st.subheader("Recent Transactions")
            
            recent_transactions = supplier_spend.sort_values("Date", ascending=False).head(10)
            st.dataframe(
                recent_transactions[["Date", "InvoiceID", "POID", "Category", "Amount", "BusinessUnit"]],
                hide_index=True
            )
        else:
            st.warning("No spend data available for this supplier.")
    
    # Contracts Tab
    with tab3:
        # Filter contract data for the selected supplier
        supplier_contracts = contract_data[contract_data["SupplierID"] == selected_supplier_id]
        
        if len(supplier_contracts) > 0:
            # Contract metrics
            active_contracts = supplier_contracts[supplier_contracts["Status"] == "Active"]
            expiring_soon = []
            renewal_alert = []
            
            current_date = datetime.now()
            
            for _, contract in active_contracts.iterrows():
                end_date = datetime.strptime(contract["EndDate"], "%Y-%m-%d")
                days_until_expiry = (end_date - current_date).days
                
                if days_until_expiry <= 90:  # Within 90 days
                    expiring_soon.append({
                        "ContractID": contract["ContractID"],
                        "Type": contract["ContractType"],
                        "EndDate": contract["EndDate"],
                        "DaysRemaining": days_until_expiry,
                        "Value": contract["Value"]
                    })
                
                if contract["AutoRenewal"] and days_until_expiry <= contract["NoticePeriodDays"]:
                    renewal_alert.append({
                        "ContractID": contract["ContractID"],
                        "Type": contract["ContractType"],
                        "NoticePeriodDays": contract["NoticePeriodDays"],
                        "DaysRemaining": days_until_expiry,
                        "EndDate": contract["EndDate"]
                    })
            
            # Display contract alerts
            if len(expiring_soon) > 0 or len(renewal_alert) > 0:
                st.subheader("Contract Alerts")
                
                alert_col1, alert_col2 = st.columns(2)
                
                with alert_col1:
                    if len(expiring_soon) > 0:
                        st.warning(
                            f"**{len(expiring_soon)} contract(s) expiring soon**\n\n" +
                            "\n".join([f"Contract {c['ContractID']} ({c['Type']}) - {c['DaysRemaining']} days remaining (${c['Value']:,.2f})" 
                                      for c in expiring_soon])
                        )
                
                with alert_col2:
                    if len(renewal_alert) > 0:
                        st.error(
                            f"**{len(renewal_alert)} contract(s) approaching auto-renewal**\n\n" +
                            "\n".join([f"Contract {c['ContractID']} - Notice period ({c['NoticePeriodDays']} days) starts now" 
                                      for c in renewal_alert])
                        )
            
            # Contract timeline
            st.subheader("Contract Timeline")
            
            # Convert date strings to datetime
            timeline_data = []
            
            for _, contract in supplier_contracts.iterrows():
                start_date = datetime.strptime(contract["StartDate"], "%Y-%m-%d")
                end_date = datetime.strptime(contract["EndDate"], "%Y-%m-%d")
                
                timeline_data.append({
                    "ContractID": contract["ContractID"],
                    "Task": contract["ContractType"],
                    "Start": start_date,
                    "Finish": end_date,
                    "Status": contract["Status"],
                    "Value": contract["Value"]
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            
            # Create a Gantt chart
            fig6 = px.timeline(
                timeline_df,
                x_start="Start",
                x_end="Finish",
                y="ContractID",
                color="Status",
                hover_data=["Task", "Value"],
                labels={"ContractID": "Contract", "Task": "Type"},
                title="Contract Timeline",
                color_discrete_map={"Active": "green", "Expired": "gray", "Future": "blue"}
            )
            
            # Add current date line
            # Instead of using vline, let's add a shape for the current date line
            fig6.update_layout(
                shapes=[
                    dict(
                        type='line',
                        yref='paper',
                        x0=current_date.strftime('%Y-%m-%d'),
                        y0=0,
                        x1=current_date.strftime('%Y-%m-%d'),
                        y1=1,
                        line=dict(color='red', width=2, dash='dash')
                    )
                ],
                annotations=[
                    dict(
                        x=current_date.strftime('%Y-%m-%d'),
                        y=1.05,
                        xref='x',
                        yref='paper',
                        text='Today',
                        showarrow=False,
                        font=dict(color='red')
                    )
                ]
            )
            
            fig6.update_yaxes(autorange="reversed")
            
            st.plotly_chart(fig6, use_container_width=True, key="contract_timeline_chart")
            
            # Contract details table
            st.subheader("Contract Details")
            
            # Sort contracts by status and end date
            sorted_contracts = supplier_contracts.sort_values(
                ["Status", "EndDate"],
                ascending=[True, True]
            )
            
            contract_display = sorted_contracts[[
                "ContractID", "ContractType", "StartDate", "EndDate", 
                "Value", "Status", "AutoRenewal", "NoticePeriodDays"
            ]]
            
            st.dataframe(contract_display, hide_index=True)
        else:
            st.warning("No contract data available for this supplier.")
    
    # Relationship Notes Tab (Simulated)
    with tab4:
        st.subheader("Relationship Notes & Activities")
        
        # Simulated relationship notes
        notes = [
            {
                "date": "2023-05-01",
                "type": "Meeting",
                "title": "Quarterly Business Review",
                "content": "Met with supplier's account team to review Q1 performance. Discussed delivery issues with Project XYZ and agreed on corrective actions.",
                "author": "John Smith"
            },
            {
                "date": "2023-03-15",
                "type": "Contract",
                "title": "Contract Amendment Signed",
                "content": "Amendment to add new services to existing MSA. Increased contract value by $50,000.",
                "author": "Jane Doe"
            },
            {
                "date": "2023-02-10",
                "type": "Issue",
                "title": "Delivery Delay",
                "content": "Supplier notified of 2-week delay for Project XYZ deliverables. Impact analysis conducted.",
                "author": "Robert Johnson"
            },
            {
                "date": "2023-01-05",
                "type": "Meeting",
                "title": "Annual Strategic Planning",
                "content": "Annual planning meeting to discuss 2023 roadmap and strategic initiatives. Identified opportunities for cost savings.",
                "author": "John Smith"
            }
        ]
        
        # Display notes in a timeline
        for note in notes:
            with st.expander(f"{note['date']} | {note['type']}: {note['title']}"):
                st.markdown(f"**{note['title']}**")
                st.markdown(note['content'])
                st.markdown(f"*Author: {note['author']}*")
        
        # Add new note form
        st.subheader("Add New Note")
        
        note_col1, note_col2 = st.columns(2)
        
        with note_col1:
            note_type = st.selectbox("Note Type:", ["Meeting", "Contract", "Issue", "Other"])
        
        with note_col2:
            note_title = st.text_input("Title:")
        
        note_content = st.text_area("Content:")
        
        if st.button("Save Note"):
            st.success("Note saved successfully! (This is a simulation)")
    
    # Supplier Segmentation Overview
    st.subheader("Supplier Segmentation Overview")
    
    # Get all supplier data with performance and spend information
    latest_quarter = performance_data["Quarter"].max()
    latest_performance = performance_data[performance_data["Quarter"] == latest_quarter]
    
    # Prepare data for segmentation
    segmentation_data = []
    
    for _, supplier in supplier_data.iterrows():
        # Get performance data
        perf = latest_performance[latest_performance["SupplierID"] == supplier["SupplierID"]]
        performance_score = perf["OverallScore"].iloc[0] if len(perf) > 0 else 5.0  # Default if no data
        
        # Get spend data
        supplier_name = supplier["SupplierName"]
        spend = spend_data[spend_data["Supplier"] == supplier_name]
        total_spend = spend["Amount"].sum() if len(spend) > 0 else 0
        
        # Calculate spend percentile (higher percentile = higher relative spend)
        all_suppliers_spend = spend_data.groupby("Supplier")["Amount"].sum()
        spend_percentile = (all_suppliers_spend <= total_spend).mean() * 100 if total_spend > 0 else 0
        
        # Add to segmentation data
        segmentation_data.append({
            "SupplierID": supplier["SupplierID"],
            "SupplierName": supplier_name,
            "Category": supplier["Category"],
            "PerformanceScore": performance_score,
            "TotalSpend": total_spend,
            "SpendPercentile": spend_percentile,
            "IsSelected": supplier["SupplierID"] == selected_supplier_id
        })
    
    segmentation_df = pd.DataFrame(segmentation_data)
    
    # Create segmentation quadrant chart
    fig7 = px.scatter(
        segmentation_df,
        x="SpendPercentile",
        y="PerformanceScore",
        color="Category",
        size="TotalSpend",
        hover_name="SupplierName",
        title="Supplier Segmentation Matrix",
        labels={
            "SpendPercentile": "Spend (Percentile)",
            "PerformanceScore": "Performance Score (1-10)",
            "Category": "Category"
        },
        size_max=25,
        opacity=0.7
    )
    
    # Apply standardized horizontal legend style at bottom
    # Position legend at bottom horizontally
    fig7.update_layout(
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
    
    # Highlight the selected supplier
    selected_supplier_data = segmentation_df[segmentation_df["IsSelected"]]
    
    if len(selected_supplier_data) > 0:
        x = selected_supplier_data["SpendPercentile"].iloc[0]
        y = selected_supplier_data["PerformanceScore"].iloc[0]
        
        fig7.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers",
            marker=dict(
                size=16,
                color="rgba(0,0,0,0)",
                line=dict(
                    color="black",
                    width=2
                )
            ),
            showlegend=False,
            hoverinfo="skip"
        ))
    
    # Add quadrant lines
    fig7.add_hline(y=7.5, line_width=1, line_dash="dash", line_color="gray")
    fig7.add_vline(x=60, line_width=1, line_dash="dash", line_color="gray")
    
    # Add quadrant annotations
    fig7.add_annotation(x=80, y=8.75, text="Strategic", showarrow=False, font=dict(size=12, color="green"))
    fig7.add_annotation(x=30, y=8.75, text="Potential", showarrow=False, font=dict(size=12, color="blue"))
    fig7.add_annotation(x=80, y=3.75, text="Problematic", showarrow=False, font=dict(size=12, color="red"))
    fig7.add_annotation(x=30, y=3.75, text="Transactional", showarrow=False, font=dict(size=12, color="gray"))
    
    st.plotly_chart(fig7, use_container_width=True)
