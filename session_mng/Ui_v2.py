import streamlit as st
from streamlit_option_menu import option_menu
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

import requests

from PIL import Image
import base64
import io

API_URL = "http://127.0.0.1:5000/generate"

st.set_page_config(layout="wide")

def display_logo_and_title(title):
    primary_color = '#027dc3'
    header = st.container()
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
    with header:
        col1, col3 = st.columns([30,6.5])
        with col1:
            st.markdown(f'<h1 style="color:{primary_color};">{title}</h1>', unsafe_allow_html=True)

    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.5rem;
            background-color: white;
            z-index: 999;
            color: #027dc3;
        }
    </style>
        """,
        unsafe_allow_html=True
    )

def set_page_container_style():
    padding_top = 1.6
    st.markdown(f"""
        <style>
        .block-container{{
            padding-top: {padding_top}rem;    }}
    </style>""",
        unsafe_allow_html=True,
    )

def retrieve_sessions(list_sessions, app_name=""):
    if list_sessions == {}:
        return []
    sessions = []
    for sess in list_sessions:
        sessions.append(sess["session_name"]) if sess["app_name"] == app_name else None
    return sessions

def create_chatName(sessions):
    chat_name = int(sessions[-1][-1])+1
    return chat_name

set_page_container_style()

# API URLs
BASE_API_URL = "http://127.0.0.1:8004" 
create_user = f"{BASE_API_URL}/users/"
get_user_sessions = "{BASE_API_URL}/users/{user_id}/sessions/"
create_chat_session = f"{BASE_API_URL}/sessions/"
query = f"{BASE_API_URL}/query/"

# Function to get the IP address of the user
def get_ip_address():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        st.error(f"Failed to get IP address: {str(e)}")

# Function to send IP address to backend for verification
def send_ip_address_to_backend(ip_address):
    try:
        API_URL = "http://127.0.0.1:8004/verify/"
        payload = {
            "user_ip": ip_address
        }
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            return response.json()#.get("verified", False)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {"verified": False}
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        

# Get the IP address of the user
if "user_ip" not in st.session_state:
    st.session_state['user_ip'] = get_ip_address()

if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = {
        "App1":{}, "App2":{}, "App3":{}, "App4":{}
    }



if "verified" not in st.session_state:
# Send IP address to backend for verification
    
    st.session_state["verified"] = send_ip_address_to_backend(st.session_state['user_ip'])
    
if st.session_state["verified"].get("verified", False):
    st.session_state['user_name'] = st.session_state["verified"].get("user_name", "Empty_User")
    st.session_state['user_id'] = st.session_state["verified"].get("user_id", "Empty_id")

    try:
        usr_ses = requests.get(get_user_sessions.format(BASE_API_URL=BASE_API_URL, 
                                            user_id=st.session_state['user_id']))
        if usr_ses.status_code == 200:
            st.session_state['chat_sessions'] = usr_ses.json()
        else:
            st.session_state['chat_sessions'] = {}
            st.markdown("Select an app and create a session")

    except Exception as e:
        print(e)
    # Rest of the code
    with st.sidebar:
        app_options = ["App1", "App2", "App3", "App4"]
        app_selected = st.selectbox("Select App", app_options)

        if app_selected == "App1":
            sessions = list(set(["New Chat"]+retrieve_sessions(usr_ses.json(), app_selected)))
            chat_selected = st.selectbox("Select Chat", sessions)
            
            if chat_selected == "New Chat":
                sess_res = requests.post(create_chat_session, 
                                         json={"user_id": st.session_state['user_id'],
                                               "session_name": create_chatName(sessions),
                                               "app_name": app_selected})
            else:
                st.session_state['Chat_history'][app_selected][chat_selected] = True # update this 
 

    # Rest of the code
else:
    if "user_name" not in st.session_state:
        user_name = st.text_input("Please enter User name: ")
        if st.button("Submit"):
            st.session_state['user_name'] = user_name
            response = requests.post(create_user,json={"user_name": st.session_state['user_name'], "user_ip": st.session_state['user_ip']})
            if response.status_code == 200:
                st.session_state["verified"] = response.json()
                st.session_state["verified"]["verified"] = True
            else:
                print(f"Error: {response.status_code} - {response.text}")



if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "images" not in st.session_state:
    st.session_state.images = ''

models_dict = {"App1":"model1", 
               'App2':"model2", 
               "App3":"model3",
               "App4":"model4"}

display_logo_and_title("Chat Assistant")  

st.markdown("<h3 style='color:#A9A9A9;'>Chat Session</h3>", unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(""):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"): 
        message_placeholder = st.empty()
        full_response = ""
        filename = ''
        page_id = "-"
        using_Internet = False
        empty_response = False

    payload = {
            "chat_history": st.session_state.chat_history,
            "prompt": prompt,
            "model": models_dict[app_selected]
        }

    try:
        with st.spinner("Generating response..."):
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json().get("response", "")

                st.session_state.chat_history.append({
                    "user": prompt,
                    "response": result
                })

                st.session_state.messages.append({"role": "assistant", "content": result})

                st.rerun()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
