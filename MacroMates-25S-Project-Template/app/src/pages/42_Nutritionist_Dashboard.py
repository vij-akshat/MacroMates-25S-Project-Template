import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from modules.nav import SideBarLinks
import os

# Configure the page
st.set_page_config(layout="wide", page_title="Nutritionist Dashboard - MacroMates")

# Display the appropriate sidebar links for the logged in user
SideBarLinks()

st.title("Nutritionist Dashboard")
st.subheader("Overview of Client Nutrition Metrics")

# API configuration
API_BASE_URL = "http://host.docker.internal:4000"

# Function to fetch dashboard data
def fetch_dashboard_data():
    try:
        url = f"{API_BASE_URL}/nutritionist/dashboard"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch dashboard data: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Fetch and display dashboard data
dashboard_data = fetch_dashboard_data()

if dashboard_data:
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(dashboard_data)
    
    # Display key metrics
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_intake = df['Avg_Nutrient_Intake'].mean()
        st.metric("Average Nutrient Intake", f"{avg_intake:.2f}")
    
    with col2:
        unique_clients = df['ClientID'].nunique()
        st.metric("Active Clients", unique_clients)
    
    with col3:
        unique_nutrients = df['Name'].nunique()
        st.metric("Tracked Nutrients", unique_nutrients)
    
    # Display nutrient trends
    st.subheader("Nutrient Trends by Category")
    fig = px.bar(df, x='Category', y='Avg_Nutrient_Intake', 
                 color='Name', title='Average Nutrient Intake by Category')
    st.plotly_chart(fig, use_container_width=True)
    
    # Display client-specific metrics
    st.subheader("Client Nutrition Overview")
    client_metrics = df.groupby('ClientID').agg({
        'Avg_Nutrient_Intake': 'mean',
        'Name': 'count'
    }).reset_index()
    client_metrics.columns = ['Client ID', 'Average Intake', 'Nutrients Tracked']
    st.dataframe(client_metrics, use_container_width=True)
else:
    st.warning("No dashboard data available. Please check the API connection.") 