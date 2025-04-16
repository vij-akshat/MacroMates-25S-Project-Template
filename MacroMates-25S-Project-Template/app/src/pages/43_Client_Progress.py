import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from modules.nav import SideBarLinks
import os

# Configure the page
st.set_page_config(layout="wide", page_title="Client Progress - MacroMates")

# Display the appropriate sidebar links for the logged in user
SideBarLinks()

st.title("Client Progress Analysis")
st.subheader("Track and analyze client nutrition progress")

# API configuration
API_BASE_URL = "http://host.docker.internal:4000"

# Function to fetch clients
def fetch_clients():
    try:
        url = f"{API_BASE_URL}/c/clients"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch clients: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Function to fetch client progress
def fetch_client_progress(client_id):
    try:
        url = f"{API_BASE_URL}/nutritionist/progress/{client_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch progress: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Function to fetch nutrient deficiencies
def fetch_deficiencies(client_id, threshold=0.7):
    try:
        url = f"{API_BASE_URL}/nutritionist/deficiencies"
        params = {'client_id': client_id, 'threshold': threshold}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch deficiencies: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

# Get client list for dropdown
clients = fetch_clients()
client_options = {f"{client['name']} (ID: {client['id']})": client['id'] for client in clients}

# Client selection
selected_client = st.selectbox("Select Client", options=list(client_options.keys()))
client_id = client_options[selected_client] if selected_client else None

if client_id:
    # Fetch and display progress data
    progress_data = fetch_client_progress(client_id)
    deficiencies = fetch_deficiencies(client_id)
    
    if progress_data:
        # Convert to DataFrame
        df = pd.DataFrame(progress_data)
        
        # Display progress metrics
        st.subheader("Progress Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_progress = df['Progress'].mean() if 'Progress' in df.columns else 0
            st.metric("Average Progress", f"{avg_progress:.1%}")
        
        with col2:
            latest_date = pd.to_datetime(df['Date']).max() if 'Date' in df.columns else "N/A"
            st.metric("Latest Update", str(latest_date))
        
        with col3:
            total_entries = len(df)
            st.metric("Total Entries", total_entries)
        
        # Display progress chart
        if 'Date' in df.columns and 'Progress' in df.columns:
            st.subheader("Progress Over Time")
            fig = px.line(df, x='Date', y='Progress', 
                         title='Client Progress Trend')
            st.plotly_chart(fig, use_container_width=True)
    
    # Display deficiencies
    if deficiencies:
        st.subheader("Nutrient Deficiencies")
        deficiency_df = pd.DataFrame(deficiencies)
        st.dataframe(deficiency_df, use_container_width=True)
        
        # Display deficiency chart
        fig = px.bar(deficiency_df, x='Name', y='Avg_Intake',
                     title='Nutrient Intake vs Recommended Levels')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No significant nutrient deficiencies detected!")
else:
    st.info("Please select a client to view their progress.") 