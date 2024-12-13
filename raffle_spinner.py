# randomizer for christmas party raffle
import random
import streamlit as st
import pandas as pd
import time
import msal
import requests
import json
from dotenv import load_dotenv
from config import config
from streamlit_lottie import st_lottie 

if 'winner_name' not in st.session_state:
    st.session_state.winner_name = None

# load data
load_dotenv()
@st.cache_data(ttl=3600)
def get_auth():
    client = msal.ConfidentialClientApplication(config['client_id'], authority=config['authority'], client_credential=config['client_secret'])
    token_result = client.acquire_token_silent(config['scope'], account=None)
    if token_result:
        access_token = f"Bearer {token_result['access_token']}"
        print('Access token was loaded from cache')
    else:
        token_result = client.acquire_token_for_client(scopes=config['scope'])
        access_token = f"Bearer {token_result['access_token']}"
        print('New access token was acquired from Azure AD')
    return token_result


# get data from graph by url 
def get_data(url, val):
    token_result = get_auth()
    headers = {
        'Authorization': token_result['access_token']
    }
    graph_data = []
    graph_result = requests.get(url, headers=headers)
    print(f'Status code: {graph_result.status_code}')
    if graph_result.status_code == 200 and val=="raffle":
        result = graph_result.json()
        items = [
            (
                item['fields']['ItemName'], 
                item['fields']['Amount'],
                item['fields'].get('HasWon', 0),
                item['fields'].get('SeqID', 0),
                item['id']
            ) for item in result['value']]
        graph_data = items
    if graph_result.status_code == 200 and val=="entries":
        result = graph_result.json()
        items = [
            (
                item['fields']['Name'], 
                # group 1
                item['fields']['WaterpikAquariusWaterFlosser'],
                item['fields']['SonicareToothbrush'],
                item['fields']['TherapeuticDeepTissueMassageGunK'],
                item['fields']['BoseSoundLinkBluetoothSpeaker'],
                item['fields']['KendraScottBraceletandEarringset'],
                item['fields']['AirFryerOven'],
                item['fields']['EverywhereCrossbodyBagLululemonG'],
                item['fields']['MichaelKorsPurse'],
                item['fields']['InsulatedBackpackSoftCooler'],
                # group 2
                item['fields']['Dronewith4KCamera'],
                item['fields']['AppleAirPodsPro'],
                item['fields']['WalkingPadwithIncline'],
                item['fields']['AppleiPadwithStylus'],
                item['fields']['SoloStoveFirePit'],
                item['fields']['AppleiWatch'],
                item['fields']['NintendoSwitch_x002d_OLEDModelwi'],
                item['fields']['KitchenAidStandup5QTMixer'],
                item['fields']['KamadoKettleJoeGrill'],
                # group 3
                item['fields']['RTICSigmaIceChest'],
                item['fields']['FishingRod_x002f_TackleBoxPackag'],
                item['fields']['DysonSupersonicHairDryer'],
                item['fields']['MicrosoftXboxSeriesX1TBConsole'],
                item['fields']['SonyPlayStation5SlimConsole'],
                item['fields']['PearceBespokeCustomSuitJacket'],
                item['fields']['_x0036_5inSmartTV'],
                item['fields']['BeckyFosCanvasGraphic'],
                item['fields']['DateNightPackage'],
            
                item['fields']['MYSTERYITEM'],
                item['fields']['HasWon'],
                item['id']
            ) for item in result['value']
        ]
        graph_data = items
    return graph_data

raffle_item_list = get_data('https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/fe49f68c-2b4e-4679-bc9b-6bd3947ebf78/items?expand=fields($select=ItemName, Amount, HasWon, SeqID)', "raffle")
raffle_options = sorted(
    [{"name": item[0], "seqID":item[3], "id": item[4]} for item in raffle_item_list if item[2] <= 0],
    key=lambda x: x["seqID"]
    )

entry_item_list = get_data('https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/0b898170-c9aa-4ed3-8f37-13e14e3fe47f/items?expand=fields', "entries")
entry_options = [item[0] for item in entry_item_list]

# remove all entries after a win
def delete_entry(username):
    # username = user[0]

    for entry in entry_item_list:
        print(f"Entry: {entry[0]}, Winner: {username}")
        if entry[0] == username:
            item_id = entry[len(entry) - 1]
            print(item_id)

    assert item_id is not None, "No item ID"
    patch_url = f"https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/0b898170-c9aa-4ed3-8f37-13e14e3fe47f/items/{item_id}"

    data = {
        'fields': {
            'HasWon': 1
        }
    }

    token_result = get_auth()
    headers = {
        'Authorization': token_result['access_token'],
        'Content-Type': 'application/json'
    }

    patch_result = requests.patch(patch_url, headers=headers, data=json.dumps(data))

    if patch_result.ok:
        print(f'Successfully updated HasWon field for {username}')
    else:
        print(f'Failed to update HasWon field {item_id} for {username}. Status code: {patch_result.status_code}')

def remove_item(item):
    patch_url = f"https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/fe49f68c-2b4e-4679-bc9b-6bd3947ebf78/items/{item}"

    data = {
        'fields': {
            'HasWon': 1
        }
    }

    token_result = get_auth()
    headers = {
        'Authorization': token_result['access_token'],
        'Content-Type': 'application/json'
    }

    patch_result = requests.patch(patch_url, headers=headers, data=json.dumps(data))

# selects winner and does animation
def spinner(raffle_index):
    results = st.empty()
    entered = []

    for item in entry_item_list:
        if item[raffle_index + 1] > 0 and item[len(item) - 2] == 0:
            entered.append(item)

    if len(entered) > 0: 
        winner = random.choice(entered)
        # suspense meter
        time.sleep(3)
        results.markdown(f"<h1 style='text-align: center; font-size: 80px;'>The winner is {winner[0]}!</h1>", unsafe_allow_html=True)
        # delete_entry(winner)
        return winner
    else:
        time.sleep(3)
        results.write(f"There are no bids on this item.")
        return None

def confirm(winner, item):
    delete_entry(winner)
    remove_item(item)
    winner_name = ""

# page setup
col1, col2, col3 = st.columns([1, 50, 1])
anim_url = requests.get(
    "https://lottie.host/b93f7c66-4f7a-4fb5-997c-bbbb128b2d01/RwphoDTqQW.json"
)
url_json = dict()
if anim_url.status_code == 200:
    url_json = anim_url.json()
else:
    st.write("Failed to GET animation.")



with col2:    
    st.image("./images/Sigma Christmas Logo.png")
    st.markdown(
        """
        <style>
        .st-br {
            white-space: pre-wrap;
        }
        div[data-baseweb="select"] > div {
            font-size: 60px;
            min-height: 100px;
            height: auto;
            font-weight: bold;
            overflow-wrap: normal !important;
            text-wrap-mode: wrap !important;
            white-space: normal;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    combobox = st.selectbox(
        'Items Being Raffled',
        options=raffle_options,
        format_func=lambda item: item['name'],
        label_visibility='hidden'
    )
    
    with st.spinner('Selecting a winner...'):
        if st.button("Choose Winner", type='primary'): 
            st.snow()
            winner = spinner(raffle_options.index(combobox)) 
            st.session_state.winner_name = winner[0]
            # remove_item(combobox['id'])
    if st.button("Confirm", type="secondary"):
        if st.session_state.winner_name:
            confirm(st.session_state.winner_name, combobox['id'])
        else:
            st.warning("No winner selected.")