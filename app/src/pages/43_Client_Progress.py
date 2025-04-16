import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Client Progress",
    page_icon="📊",
    layout="wide"
)

# Get client_id from URL parameters
client_id = st.experimental_get_query_params().get("client_id", [None])[0]

if not client_id:
    st.error("No client selected. Please select a client from the dashboard.")
    st.stop()

# Title
st.title("📊 Client Progress Tracking")

# Fetch client progress data
@st.cache_data(ttl=300)
def fetch_client_progress(client_id):
    try:
        response = requests.get(f"http://localhost:4000/nutritionist/progress/{client_id}")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error("Failed to fetch client progress data")
            return None
    except Exception as e:
        st.error(f"Error fetching progress data: {str(e)}")
        return None

# Fetch client details
@st.cache_data(ttl=300)
def fetch_client_details(client_id):
    try:
        response = requests.get("http://localhost:4000/nutritionist/clients")
        if response.status_code == 200:
            clients_df = pd.DataFrame(response.json())
            client_details = clients_df[clients_df['client_id'] == int(client_id)].iloc[0]
            return client_details
        else:
            st.error("Failed to fetch client details")
            return None
    except Exception as e:
        st.error(f"Error fetching client details: {str(e)}")
        return None

# Display client information
client_details = fetch_client_details(client_id)
if client_details is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Weight", f"{client_details['current_weight']} kg")
    with col2:
        st.metric("Target Weight", f"{client_details['target_weight']} kg")
    with col3:
        st.metric("Activity Level", client_details['activity_level'])

# Progress Charts
progress_df = fetch_client_progress(client_id)
if progress_df is not None and not progress_df.empty:
    progress_df['progress_date'] = pd.to_datetime(progress_df['progress_date'])
    
    # Weight Progress Chart
    fig_weight = px.line(progress_df, 
                        x='progress_date', 
                        y='weight',
                        title='Weight Progress Over Time')
    st.plotly_chart(fig_weight, use_container_width=True)
    
    # Body Composition Charts
    col1, col2 = st.columns(2)
    with col1:
        fig_body_fat = px.line(progress_df, 
                              x='progress_date', 
                              y='body_fat_percentage',
                              title='Body Fat Percentage')
        st.plotly_chart(fig_body_fat, use_container_width=True)
    
    with col2:
        fig_muscle = px.line(progress_df, 
                            x='progress_date', 
                            y='muscle_mass',
                            title='Muscle Mass')
        st.plotly_chart(fig_muscle, use_container_width=True)
    
    # Progress Notes
    st.subheader("Progress Notes")
    progress_df['progress_date'] = progress_df['progress_date'].dt.strftime('%Y-%m-%d')
    st.dataframe(progress_df[['progress_date', 'notes']], 
                use_container_width=True,
                hide_index=True)
else:
    st.info("No progress data available for this client")

# Add new progress entry
st.subheader("Add New Progress Entry")
with st.form("progress_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    with col2:
        body_fat = st.number_input("Body Fat Percentage", min_value=0.0, max_value=100.0, step=0.1)
    with col3:
        muscle_mass = st.number_input("Muscle Mass (kg)", min_value=0.0, step=0.1)
    
    water_percentage = st.number_input("Water Percentage", min_value=0.0, max_value=100.0, step=0.1)
    notes = st.text_area("Notes")
    
    if st.form_submit_button("Save Progress"):
        # Here you would typically make a POST request to save the new progress entry
        st.success("Progress entry saved successfully!")
        # Refresh the page to show new data
        st.experimental_rerun() 