import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import os
from utils.data_manager import load_data, validate_data, detect_column_types
from utils.visualizations import create_spend_chart, create_supplier_chart
from utils.mock_data import get_mock_spend_data, get_mock_supplier_data, get_mock_contract_data, get_mock_performance_data
from utils.template_generator import get_template_download_button
from utils.llm_manager import render_llm_config_sidebar, analyze_text_with_llm
from pages import category_intelligence, supplier_risk, supplier_relationship, market_engagement

# Set page config
st.set_page_config(
    page_title="Arcadis Procure Insights",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default menu elements and add custom styling - CSS included directly
st.markdown("""
<style>
/* Enhanced navigation experience */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Improved tab navigation styling */
div.stTabs button[role="tab"] {
    background-color: rgba(30, 30, 30, 0.7) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 1rem 1.5rem !important;
    margin-right: 4px !important;
    gap: 0.5rem !important;
    transition: all 0.2s ease-in-out !important;
    border-top: 3px solid transparent !important;
    font-weight: 500 !important;
}

div.stTabs button[role="tab"][aria-selected="true"] {
    background-color: rgba(40, 40, 40, 0.8) !important;
    border-top: 3px solid #FF6B35 !important;
    font-weight: 600 !important;
}

div.stTabs button[role="tab"]:hover {
    background-color: rgba(40, 40, 40, 0.9) !important;
    transform: translateY(-2px);
}

/* Hide hamburger menu */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* Improve card styling with shadows and hover effects */
div[data-testid="stExpander"] {
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

div[data-testid="stExpander"]:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

/* Improve button styling */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
}

/* Enhanced card-style metrics with animation */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1c1c1c, #252525);
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    border-left: 3px solid #FF6B35;
    transition: all 0.3s ease;
    margin-bottom: 10px;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

[data-testid="stMetric"] > div {
    padding: 5px 0;
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: rgba(255, 255, 255, 0.85) !important;
    letter-spacing: 0.02em;
}

[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    color: #FF6B35 !important;
    font-size: 1.6rem !important;
}

/* Card-style containers for key elements */
div.element-container div.stDataFrame,
div.element-container div.stPlotlyChart {
    background: rgba(30, 30, 30, 0.6);
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    border-bottom: 3px solid rgba(255, 107, 53, 0.7);
    transition: all 0.3s ease;
}

div.element-container div.stDataFrame:hover,
div.element-container div.stPlotlyChart:hover {
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15);
}

/* Improved spacing and alignment throughout */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 95% !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0.5rem !important;
}

/* Improved spacing between sections */
.element-container {
    margin-bottom: 1.2rem !important;
}

/* Chart wrapper styling */
div[data-testid="stPlotlyChart"] > div {
    border-radius: 8px;
    overflow: hidden;
}

/* Improved text readability */
p, li {
    line-height: 1.6 !important;
    font-size: 1rem !important;
    color: rgba(255, 255, 255, 0.85) !important;
}

/* Headings styling */
h1, h2, h3, h4 {
    margin-bottom: 1rem !important;
    padding-bottom: 0.5rem !important;
    letter-spacing: 0.02em !important;
}

h1 {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
}

h2 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    border-bottom: 1px solid rgba(255, 107, 53, 0.3) !important;
}

h3 {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #FF8C61 !important;
}

/* Form elements styling */
div[data-testid="stFileUploader"] {
    border: 1px dashed rgba(255, 107, 53, 0.5) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    background: rgba(30, 30, 30, 0.4) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #FF6B35 !important;
    background: rgba(30, 30, 30, 0.6) !important;
}

/* Animation for section transitions */
.element-container {
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
}

h1, h2, h3, h4 {
    letter-spacing: -0.01em;
}

/* Improve sidebar */
section[data-testid="stSidebar"] {
    background-color: #181818;
    border-right: 1px solid #2D2D2D;
}

/* Custom scrollbar for dark theme */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #1E1E1E;
}

::-webkit-scrollbar-thumb {
    background: #3D3D3D;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4D4D4D;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "spend_data" not in st.session_state:
    st.session_state.spend_data = get_mock_spend_data()
if "supplier_data" not in st.session_state:
    st.session_state.supplier_data = get_mock_supplier_data()
if "contract_data" not in st.session_state:
    st.session_state.contract_data = get_mock_contract_data()
if "performance_data" not in st.session_state:
    st.session_state.performance_data = get_mock_performance_data()

# Custom logo and header in sidebar
st.sidebar.markdown("""
<h1 style='text-align: center'>
    <span style='color: #e65100'>
        Arcadis Procure Insights
    </span>
</h1>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Download Templates Section in Sidebar
with st.sidebar.expander("📑 Data Templates"):
    st.markdown("### Download Data Templates")
    st.markdown("Get all the templates you need to populate the procurement tool:")
    
    # Single button to download all templates at once
    get_template_download_button()  # Will use the new function to create a bundle

# Data Management Section in Sidebar
with st.sidebar.expander("📊 Smart Data Upload"):
    st.markdown("### Intelligent File Detection")
    st.markdown("Upload multiple files and let the system detect and map each file to the appropriate section:")
    
    # Smart multiple file uploader
    uploaded_files = st.file_uploader(
        "Upload your procurement data files:",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        data_type_map = {
            "Spend Data": "spend_data",
            "Supplier Master Data": "supplier_data",
            "Contract Data": "contract_data",
            "Performance Data": "performance_data"
        }
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            # Try to automatically detect the data type based on file content
            is_processed = False
            
            # Create placeholder for status messages
            status_placeholder = st.empty()
            status_placeholder.info(f"🔍 Analyzing {uploaded_file.name}...")
            
            # Simple file detection based on filename patterns
            filename = uploaded_file.name.lower()
            detected_type = None
            
            # Detect file type based on filename
            if "supplier_master" in filename or "supplier_data" in filename:
                detected_type = "Supplier Master Data"
                state_var = "supplier_data"
            elif "contract" in filename:
                detected_type = "Contract Data"
                state_var = "contract_data"
            elif "performance" in filename:
                detected_type = "Performance Data"
                state_var = "performance_data"
            elif "spend" in filename:
                detected_type = "Spend Data"
                state_var = "spend_data"
            
            if detected_type:
                # Load the file using the standard loader
                data = load_data(uploaded_file, 'csv' if filename.endswith('.csv') else 'excel')
                if data is not None:
                    # Store the data in session state
                    st.session_state[state_var] = data
                    
                    # Detect column types for dynamic UI
                    detect_column_types(data)
                    
                    # Store column types for dynamic UI generation
                    if hasattr(data, 'attrs') and 'column_types' in data.attrs:
                        column_type_key = f"{state_var}_column_types"
                        st.session_state[column_type_key] = data.attrs['column_types']
                    
                    if hasattr(data, 'attrs') and 'unique_values' in data.attrs:
                        unique_values_key = f"{state_var}_unique_values"
                        st.session_state[unique_values_key] = data.attrs['unique_values']
                    
                    # Show success message
                    status_placeholder.success(f"✅ {uploaded_file.name}: Loaded as {detected_type} successfully!")
                    is_processed = True
            
            # If no valid data type was found
            if not is_processed:
                status_placeholder.error(f"❌ {uploaded_file.name}: Could not determine data type. Please ensure the file contains the required columns for at least one of the supported data types.")

    # Data Refresh Option
    if st.button("Reset to Demo Data"):
        st.session_state.spend_data = get_mock_spend_data()
        st.session_state.supplier_data = get_mock_supplier_data()
        st.session_state.contract_data = get_mock_contract_data()
        st.session_state.performance_data = get_mock_performance_data()
        st.success("✅ Reset to demonstration data")
        st.rerun()

# Add LLM Configuration Section
render_llm_config_sidebar()

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Welcome", 
    "Category Intelligence", 
    "Supplier Risk Analysis", 
    "Supplier Relationship Management", 
    "Market Engagement"
])

# Welcome Tab Content
with tab1:
    # Enhanced welcome header with professional styling
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(30,30,30,0.8) 0%, rgba(40,40,40,0.8) 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 25px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); border-left: 4px solid #FF6B35;">
        <h1 style="margin: 0; color: white; font-size: 32px; font-weight: 600;">
            Welcome to <span style="color: #FF6B35;">Procure</span>Insights
        </h1>
        <p style="color: rgba(255,255,255,0.8); margin-top: 8px; font-size: 16px;">
            Transform your procurement data into actionable business intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    ## Transforming Procurement into Strategic Value
    
    Arcadis Procure Insights empowers your procurement team to move beyond tactical buying to strategic value creation. Our analytics 
    platform reveals the stories hidden within your procurement data, guiding you from insight to informed action.
    
    ### Your Procurement Strategy Journey:
    """)
    
    # Create a more elegant and visually appealing welcome page with clear value proposition
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
        <div style="text-align: center; max-width: 800px;">
            <p style="font-size: 1.2rem; color: #FF6B35; margin-bottom: 2rem;">
                Transform your procurement data into strategic business value
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create stylish cards for the four key value propositions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">📊 Visualize</h3>
            <p style="font-weight: bold;">See the full picture of your spending</p>
            <p>Uncover spending patterns and supplier dependencies that would otherwise remain hidden.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">💡 Discover</h3>
            <p style="font-weight: bold;">Identify untapped opportunities</p>
            <p>Find savings potential, risk factors, and innovation sources across your supply base.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">🔍 Analyze</h3>
            <p style="font-weight: bold;">Understand the 'why' behind the numbers</p>
            <p>Connect spending patterns to business outcomes and market conditions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #FF6B35;">
            <h3 style="color: #FF6B35;">🚀 Act</h3>
            <p style="font-weight: bold;">Transform insights into results</p>
            <p>Implement data-driven strategies that deliver measurable procurement value.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create elegant module cards with visual separators
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #FFFFFF; margin-bottom: 1.5rem;">Procurement Intelligence Modules</h2>
        <p style="color: #BBBBBB; margin-bottom: 2rem;">Comprehensive analytics to transform your procurement function</p>
    </div>
    """, unsafe_allow_html=True)
    
    mod_col1, mod_col2 = st.columns(2)
    
    with mod_col1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">📊 Category Intelligence</h3>
            <p>Turn spend data into cost-saving opportunities and category strategies that align with business objectives.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Spend pattern analysis</li>
                <li>Supplier concentration insights</li>
                <li>Category strategy recommendations</li>
            </ul>
        </div>
        
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🤝 Supplier Relationship Management</h3>
            <p>Create value-driven partnerships with your most critical suppliers through data-driven relationship management.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Performance tracking dashboards</li>
                <li>Relationship health assessments</li>
                <li>Value improvement opportunities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with mod_col2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🔍 Supplier Risk Analysis</h3>
            <p>Anticipate and mitigate supply chain disruptions before they impact your business operations.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Multi-factor risk assessment</li>
                <li>Risk mitigation recommendations</li>
                <li>Early warning indicators</li>
            </ul>
        </div>
        
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-top: 4px solid #FF6B35;">
            <h3 style="color: #FFFFFF;">🌐 Market Engagement</h3>
            <p>Align sourcing decisions with market trends and identify emerging opportunities.</p>
            <ul style="margin-top: 0.8rem;">
                <li>Market dynamics analysis</li>
                <li>Potential supplier identification</li>
                <li>Price trend forecasting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section with a prominent call-to-action
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; background-color: #1E1E1E; padding: 2rem; border-radius: 10px;">
        <h2 style="color: #FFFFFF; margin-bottom: 1.5rem;">Getting Started</h2>
        <div style="display: flex; justify-content: center;">
            <ol style="max-width: 600px; text-align: left;">
                <li style="margin-bottom: 0.8rem;">Upload your procurement data using the <b>Data Management</b> panel in the sidebar</li>
                <li style="margin-bottom: 0.8rem;">Or explore using our pre-loaded demonstration data</li>
                <li style="margin-bottom: 0.8rem;">Configure AI-powered insight generation in the sidebar (optional)</li>
                <li style="margin-bottom: 0.8rem;">Navigate through the tabs to discover actionable procurement insights</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Category Intelligence Tab
with tab2:
    category_intelligence.show(st.session_state)

# Supplier Risk Analysis Tab
with tab3:
    supplier_risk.show(st.session_state)

# Supplier Relationship Management Tab
with tab4:
    supplier_relationship.show(st.session_state)

# Market Engagement Tab
with tab5:
    market_engagement.show(st.session_state)
