import os
import streamlit as st

# config = {
#     'client_id': os.getenv('CLIENT_ID'),
#     'client_secret': os.getenv('CLIENT_SECRET'),
#     'tenant_id': os.getenv('TENANT_ID'),
#     'authority': os.getenv('AUTHORITY'),
#     'scope': ['https://graph.microsoft.com/.default']
# }

config = {
    'client_id': st.secrets["CLIENT_ID"],
    'client_secret': st.secrets["CLIENT_SECRET"],
    'tenant_id': st.secrets["TENANT_ID"],
    'authority': st.secrets["AUTHORITY"],
    'scope': ['https://graph.microsoft.com/.default']
}