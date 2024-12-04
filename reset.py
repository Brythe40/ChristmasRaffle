# reset the HasWon columns in both raffle lists
from raffle_spinner import get_auth
import requests
import json
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
def patch(patch_url):
    data = {
        'fields': {
            'HasWon': 0
        }
    }

    token_result = get_auth()
    headers = {
        'Authorization': token_result['access_token'],
        'Content-Type': 'application/json'
    }

    patch_result = requests.patch(patch_url, headers=headers, data=json.dumps(data))

def reset():
    item_IDs = [5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24, 27, 29, 30, 31, 32, 33, 34, 35]
    for item in item_IDs: 
        patch(f"https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/fe49f68c-2b4e-4679-bc9b-6bd3947ebf78/items/{item}")
    # patch(f"https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/0b898170-c9aa-4ed3-8f37-13e14e3fe47f/items?expand=fields")