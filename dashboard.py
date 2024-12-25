import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(page_title="Mental Health Dashboard", layout="wide")

# Function to load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('/home/omran-xy/Workspace/Faculty/Data science tools/Final Project/Cleaned.csv')
        return df
    except FileNotFoundError:
        st.error("Error: Could not find the CSV file. Please check the file path.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load the data
df = load_data()

if df is not None:
    # Title and description
    st.title("Mental Health Analytics Dashboard")
    st.markdown("### Analysis of Student/Professional Mental Health Indicators")

    # Sidebar filters
    st.sidebar.header("Filters")
    selected_cities = st.sidebar.multiselect("Select Cities", 
                                             options=df['City'].unique(), 
                                             default=df['City'].unique())
    selected_professions = st.sidebar.multiselect("Select Professions", 
                                                  options=df['Profession'].unique(), 
                                                  default=df['Profession'].unique())

    # Filter the dataframe
    filtered_df = df[df['City'].isin(selected_cities) & df['Profession'].isin(selected_professions)]

    # Create three columns for key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_stress = filtered_df['Financial Stress'].mean()
        st.metric("Average Financial Stress", f"{avg_stress:.2f}")

    with col2:
        avg_satisfaction = filtered_df['Satisfaction'].mean()
        st.metric("Average Satisfaction", f"{avg_satisfaction:.2f}")

    with col3:
        avg_pressure = filtered_df['Pressure'].mean()
        st.metric("Average Pressure", f"{avg_pressure:.2f}")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sleep Duration vs. Stress Levels")
        fig_scatter = px.scatter(filtered_df, 
                                 x='Sleep Duration', 
                                 y='Financial Stress',
                                 color='Profession',
                                 size='Pressure',
                                 hover_data=['City'],
                                 title="Sleep Duration vs. Stress Levels")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("Work Hours Distribution")
        fig_hist = px.histogram(filtered_df, 
                                x='Work/Study Hours',
                                nbins=20,
                                title="Distribution of Work/Study Hours")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Replace heatmap with bar chart
    st.subheader("Average Key Metrics by Profession")
    avg_metrics = filtered_df.groupby('Profession').agg({
        'Financial Stress': 'mean',
        'Pressure': 'mean',
        'Satisfaction': 'mean',
        'Sleep Duration': 'mean',
        'Work/Study Hours': 'mean'
    }).reset_index()

    fig_bar = px.bar(avg_metrics.melt(id_vars='Profession', 
                                      var_name='Metric', 
                                      value_name='Average Value'), 
                     x='Profession', 
                     y='Average Value', 
                     color='Metric',
                     barmode='group',
                     title="Average Key Metrics by Profession")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Mental Health Risk Score
    st.subheader("Mental Health Risk Analysis")

    # Calculate risk score
    filtered_df['Risk Score'] = (
        filtered_df['Financial Stress'] * 0.3 +
        filtered_df['Pressure'] * 0.3 +
        (10 - filtered_df['Satisfaction']) * 0.2 +
        (10 - filtered_df['Sleep Duration']) * 0.2
    )

    fig_risk = px.box(filtered_df, 
                      x='Profession', 
                      y='Risk Score',
                      title="Risk Score Distribution by Profession")
    st.plotly_chart(fig_risk, use_container_width=True)

    # Add detailed statistics table
    st.subheader("Detailed Statistics by Profession")
    profession_stats = filtered_df.groupby('Profession').agg({
        'Financial Stress': 'mean',
        'Pressure': 'mean',
        'Satisfaction': 'mean',
        'Sleep Duration': 'mean',
        'Work/Study Hours': 'mean'
    }).round(2)

    st.dataframe(profession_stats)

    # Add download button for the data
    st.download_button(
        label="Download Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='mental_health_data.csv',
        mime='text/csv',
    )
