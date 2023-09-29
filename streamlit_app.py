import io, os, time, ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openai

from streamlit_option_menu import option_menu
import streamlit as st
from google.cloud import bigquery


from Insight import insight
from Insight_df_summary import insight_df_summary
from Home import home
from Upload_CSV import Upload
from Google_Cloud_Storage import google_cloud_storage
from Azure_database import azure_database
from Databricks_CSV import csv_databricks


endpoint = 'https://allbirds.openai.azure.com/'
region = 'eastus'
key = 'd67d19908eba4902af4903c270547bba'
openai.api_key = key
openai.api_base = endpoint
openai.api_type = 'azure'
openai.api_version = "2023-03-15-preview"

# st.set_page_config(layout="wide")
# hide_streamlit_style = """ <style> #MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)


number_of_tables = 0
flag = False
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'affine2-dae2df9a2d7e.json'
client = bigquery.Client()
st.markdown("""
<div style='text-align: center;'>
<h2 style='font-size: 50px; font-family: Arial, sans-serif;
                   letter-spacing: 2px; text-decoration: none;'>
<a href='https://affine.ai/' target='_blank' rel='noopener noreferrer'
               style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      text-shadow: none; text-decoration: none;'>
                      Affine QUIN
</a>
</h2>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    choose = option_menu("", ["Home", "Upload csv file","Databricks CSV", "Google Cloud Storage", 'Azure SQL Database'],
                         icons=['house', 'filetype-csv', 'bar-chart-steps',
                                'cloud-arrow-down', 'database-down'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#fa2a54"},
    }

    )


if choose == "Home":
    home()

elif choose == "Upload csv file":
    Upload()

elif choose == "Databricks CSV":
    csv_databricks()

elif choose == "Google Cloud Storage":
    google_cloud_storage()

elif choose == "Azure SQL Database":
    azure_database()

else:
    st.write('yet not written')
