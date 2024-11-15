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

entry_items_path = 'data/Christmas Raffle.csv'
entry_items_data = pd.read_csv(entry_items_path, skiprows=0)
entries = entry_items_data.iloc[:, 1].tolist()

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
        items = [(item['fields']['ItemName'], item['fields']['Amount'], item['fields']['HasWon']) for item in result['value']]
        graph_data = items
    if graph_result.status_code == 200 and val=="entries":
        result = graph_result.json()
        items = [
            (
                item['fields']['Name'], 
                item['fields']['SoloStoveFirePit'],
                item['fields']['FishingRod_x002f_TackleBoxPackag'],
                item['fields']['AppleAirPodsPro'],
                item['fields']['AppleiWatch'],
                item['fields']['AppleiPadwithStylus'],
                item['fields']['AirFryerOven'],
                item['fields']['SonicareToothbrush'],
                item['fields']['KendraScottBraceletandEarringset'],
                item['fields']['_x0036_5inSmartTV'],
                item['fields']['BoseSoundLinkBluetoothSpeaker'],
                item['fields']['Dronewith4KCamera'],
                item['fields']['DysonSupersonicHairDryer'],
                item['fields']['InsulatedBackpackSoftCooler'],
                item['fields']['KitchenAidStandup5QTMixer'],
                item['fields']['MicrosoftXboxSeriesX1TBConsole'],
                item['fields']['NintendoSwitch_x002d_OLEDModelwi'],
                item['fields']['SonyPlayStation5SlimConsole'],
                item['fields']['TherapeuticDeepTissueMassageGunK'],
                item['fields']['WalkingPadwithIncline'],
                item['fields']['WaterpikAquariusWaterFlosser'],
                item['fields']['HasWon'],
                item['id']
            ) for item in result['value']
        ]
        graph_data = items
    return graph_data

raffle_item_list = get_data('https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/fe49f68c-2b4e-4679-bc9b-6bd3947ebf78/items?expand=fields($select=ItemName, Amount)', "raffle")
raffle_options = [item[0] for item in raffle_item_list if item[2] <= 0]

entry_item_list = get_data('https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/0b898170-c9aa-4ed3-8f37-13e14e3fe47f/items?expand=fields', "entries")
entry_options = [item[0] for item in entry_item_list]

# remove all entries after a win
def delete_entry(user):
    username = user[0]

    for entry in entry_item_list:
        if entry[0] == username:
            item_id = entry[22]
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

def remove_item(item_index):
    # item_index element 6
    # for raffle_item in raffle_item_list:
    #     if raffle_item[1] <= 0:
    #         item_id = raffle_item[0]
            #print(item_id)

    # assert item_id is not None, "No item ID"
    patch_url = f"https://graph.microsoft.com/v1.0/sites/2102e2f9-9d45-46ab-afad-5d8e21a029eb/lists/fe49f68c-2b4e-4679-bc9b-6bd3947ebf78/items/{item_index}"

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

    # if patch_result.ok:
    #     print(f'Successfully updated HasWon field for {raffle_item}')
    # else:
    #     print(f'Failed to update HasWon field {item_id} for {raffle_item}. Status code: {patch_result.status_code}')

# selects winner and does animation
def spinner(raffle_index):
    results = st.empty()
    entered = []

    for item in entry_item_list:
        if item[raffle_index + 1] > 0 and item[21] == False:
            entered.append(item)

    if len(entered) > 0: 
        winner = random.choice(entered)
        time.sleep(3)
        results.markdown(f"<h1 style='text-align: center; font-size: 80px;'>The winner is {winner[0]}!</h1>", unsafe_allow_html=True)
        delete_entry(winner)
        remove_item(raffle_index)
    else:
        time.sleep(3)
        results.write(f"There are no bids on this item.")

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
    st.image("./images/Sigma Christmas Logo.png", use_container_width=True)
    combobox = st.selectbox(
        'Items Being Raffled',
        raffle_options,
        label_visibility='hidden'
    )
    with st.spinner('Selecting a winner...'):
        if st.button("Choose Winner", type='primary'): 
            st.snow()
            spinner(raffle_options.index(combobox)) 