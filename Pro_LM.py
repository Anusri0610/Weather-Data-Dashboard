import streamlit as st
import pandas as pd
import plotly

import plotly.express as px
import requests
from ydata_profiling import ProfileReport
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Weather Dashboard",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://your-help-url.com',
        'Report a bug': "https://your-bug-report-url.com",
        'About': "# Mobile-friendly Weather Dashboard"
    }
)
st.title("🌤️ Weather Data Dashboard 🌤️")

# API Configuration
apiKey = "c4955b467b19f41bfcdb6f8ef53d837e"

# Input widgets
latitude = st.text_input("Enter latitude:")
longitude = st.text_input("Enter longitude:")

if latitude and longitude:
    try:
        # Validate coordinates
        lat = float(latitude)
        lon = float(longitude)
        
        completeURL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apiKey}"
        response = requests.get(completeURL)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)
            
            # Convert list/dict values to strings
            df = df.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            
            # Display vertical data table
            st.write("## Current Weather Data")
            vertical_df = df.T.reset_index()
            vertical_df.columns = ["Attribute", "Value"]
            st.dataframe(
                vertical_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Attribute": st.column_config.Column(width="large"),
                    "Value": st.column_config.Column(width="large")
                }
            )
            
            # Visualization fix - only show numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                col = st.selectbox("Select a metric to visualize", numeric_cols)
                
                # Handle single-row data visualization
                if len(df) == 1:
                    st.write(f"### Current {col} Value")
                    st.metric(label=col, value=df[col].iloc[0])
                else:
                    fig = px.bar(df, x=df.index, y=col, title=f"{col} Values")
                    st.plotly_chart(fig)
            else:
                st.warning("No numeric columns available for visualization")
            
            # Generate and display report inline
            with st.spinner("Generating detailed analysis..."):
                profile = ProfileReport(df, explorative=True, minimal=True)
                st.write("## Comprehensive Analysis")
                
                # Generate HTML report and display
                html_report = profile.to_html()
                #html(html_report, height=1000, scrolling=True)
                html(html_report, height=800, scrolling=True, width=1200)


        else:
            st.error(f"🌩️ API Error: {response.status_code} - {response.text}")
            
    except ValueError:
        st.warning("⚠️ Please enter valid numerical coordinates")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.info("📍 Please enter both latitude and longitude to fetch weather data")
