import os
import streamlit as st

config = {
    'client_id': st.secrets["CLIENT_ID"],
    'client_secret': st.secrets["CLIENT_SECRET"],
    'tenant_id': st.secrets["TENANT_ID"],
    'authority': st.secrets["AUTHORITY"],
    'scope': ['https://graph.microsoft.com/.default']
}