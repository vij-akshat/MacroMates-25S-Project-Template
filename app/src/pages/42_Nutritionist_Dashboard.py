import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Nutritionist Dashboard",
    page_icon="🥗",
    layout="wide"
)

# Title
st.title("🥗 Nutritionist Dashboard")

# Fetch dashboard data
@st.cache_data(ttl=300)
def fetch_dashboard_data():
    try:
        response = requests.get("http://localhost:4000/nutritionist/dashboard")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch dashboard data")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Fetch clients data
@st.cache_data(ttl=300)
def fetch_clients():
    try:
        response = requests.get("http://localhost:4000/nutritionist/clients")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error("Failed to fetch clients data")
            return None
    except Exception as e:
        st.error(f"Error fetching clients: {str(e)}")
        return None

# Main dashboard layout
col1, col2, col3 = st.columns(3)

# Fetch and display dashboard data
dashboard_data = fetch_dashboard_data()
if dashboard_data:
    with col1:
        st.metric("Total Clients", dashboard_data['total_clients'])
    
    with col2:
        st.metric("Average Daily Calories", f"{dashboard_data['meal_statistics']['avg_calories']:.0f}")
    
    with col3:
        st.metric("Active Meal Plans", dashboard_data['meal_statistics']['total_plans'])

# Recent Progress Section
st.subheader("Recent Client Progress")
if dashboard_data and 'recent_progress' in dashboard_data:
    progress_df = pd.DataFrame(dashboard_data['recent_progress'])
    if not progress_df.empty:
        progress_df['progress_date'] = pd.to_datetime(progress_df['progress_date'])
        st.dataframe(progress_df, use_container_width=True)
    else:
        st.info("No recent progress updates available")

# Clients Section
st.subheader("Client Management")
clients_df = fetch_clients()
if clients_df is not None and not clients_df.empty:
    # Display clients table
    st.dataframe(clients_df, use_container_width=True)
    
    # Client selection for detailed view
    selected_client = st.selectbox(
        "Select a client to view detailed progress",
        clients_df['client_name'].tolist()
    )
    
    if selected_client:
        client_id = clients_df[clients_df['client_name'] == selected_client]['client_id'].iloc[0]
        st.markdown(f"[View Detailed Progress](/Client_Progress?client_id={client_id})")

# Nutritional Trends Section
st.subheader("Nutritional Trends")
try:
    trends_response = requests.get("http://localhost:4000/nutritionist/trends")
    if trends_response.status_code == 200:
        trends_df = pd.DataFrame(trends_response.json())
        if not trends_df.empty:
            trends_df['date'] = pd.to_datetime(trends_df['date'])
            
            # Create trend charts
            fig_calories = px.line(trends_df, x='date', y='avg_calories', 
                                 title='Average Daily Calories')
            fig_macros = px.line(trends_df, x='date', 
                               y=['avg_protein', 'avg_carbs', 'avg_fats'],
                               title='Average Macronutrient Intake')
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_calories, use_container_width=True)
            with col2:
                st.plotly_chart(fig_macros, use_container_width=True)
    else:
        st.info("No trend data available")
except Exception as e:
    st.error(f"Error fetching trends: {str(e)}")

# Nutrient Deficiencies Section
st.subheader("Common Nutrient Deficiencies")
try:
    deficiencies_response = requests.get("http://localhost:4000/nutritionist/deficiencies")
    if deficiencies_response.status_code == 200:
        deficiencies_df = pd.DataFrame(deficiencies_response.json())
        if not deficiencies_df.empty:
            fig_deficiencies = px.bar(deficiencies_df, 
                                    x='nutrient_name', 
                                    y='deficiency_count',
                                    title='Most Common Nutrient Deficiencies')
            st.plotly_chart(fig_deficiencies, use_container_width=True)
    else:
        st.info("No deficiency data available")
except Exception as e:
    st.error(f"Error fetching deficiencies: {str(e)}") 