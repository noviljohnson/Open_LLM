# import streamlit as st
# from streamlit_option_menu import option_menu
# import requests

# # Backend API URLs
# BASE_API_URL = "http://127.0.0.1:8000"
# START_SESSION_URL = f"{BASE_API_URL}/start-session"
# SEND_MESSAGE_URL = f"{BASE_API_URL}/send-message"
# GET_HISTORY_URL = f"{BASE_API_URL}/get-history"
# END_SESSION_URL = f"{BASE_API_URL}/end-session"

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "active_session_id" not in st.session_state:
#     st.session_state.active_session_id = None

# if "sessions" not in st.session_state:
#     st.session_state.sessions = []

# # Sidebar for session management
# with st.sidebar:
#     st.header("Chat Sessions")

#     # Start a new session
#     if st.button("Start New Session"):
#         user_id = "user_123"  # Replace with actual user ID logic
#         response = requests.post(START_SESSION_URL, params={"user_id": user_id})
#         if response.status_code == 200:
#             session_id = response.json().get("session_id")
#             st.session_state.active_session_id = session_id
#             st.session_state.sessions.append(session_id)
#             st.session_state.messages = []  # Clear messages for the new session
#             st.success(f"New session started: {session_id}")
#         else:
#             st.error("Failed to start a new session.")

#     # Select an active session
#     active_session = st.selectbox(
#         "Select a Session",
#         options=st.session_state.sessions,
#         index=st.session_state.sessions.index(st.session_state.active_session_id) if st.session_state.active_session_id else 0
#     )
#     if active_session != st.session_state.active_session_id:
#         st.session_state.active_session_id = active_session
#         # Load chat history for the selected session
#         response = requests.get(GET_HISTORY_URL, params={"session_id": active_session})
#         if response.status_code == 200:
#             chat_history = response.json().get("messages", [])
#             st.session_state.messages = chat_history
#         else:
#             st.error("Failed to load chat history.")

#     # End the current session
#     if st.button("End Session"):
#         if st.session_state.active_session_id:
#             response = requests.post(END_SESSION_URL, params={"session_id": st.session_state.active_session_id})
#             if response.status_code == 200:
#                 st.session_state.sessions.remove(st.session_state.active_session_id)
#                 st.session_state.active_session_id = None
#                 st.session_state.messages = []
#                 st.success("Session ended successfully.")
#             else:
#                 st.error("Failed to end the session.")
#         else:
#             st.warning("No active session to end.")

# # Main chat interface
# st.title("AI Chat Assistant")

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat input
# if prompt := st.chat_input("Type your message here..."):
#     if not st.session_state.active_session_id:
#         st.warning("Please start or select a session to send a message.")
#     else:
#         # Append user message to session state
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Send message to backend
#         payload = {
#             "session_id": st.session_state.active_session_id,
#             "message": {"role": "user", "content": prompt}
#         }
#         try:
#             with st.spinner("Generating response..."):
#                 response = requests.post(SEND_MESSAGE_URL, json=payload)
#                 if response.status_code == 200:
#                     ai_response = response.json().get("response", {})
#                     st.session_state.messages.append(ai_response)
#                     with st.chat_message("assistant"):
#                         st.markdown(ai_response["content"])
#                 else:
#                     st.error(f"Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")

# =================================================================================

# import streamlit as st
# import requests

# # Backend API URLs  
# BASE_API_URL = "http://127.0.0.1:8001"
# START_SESSION_URL = f"{BASE_API_URL}/start-session"
# SEND_MESSAGE_URL = f"{BASE_API_URL}/send-message"
# GET_HISTORY_URL = f"{BASE_API_URL}/get-history"

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# if "active_session_id" not in st.session_state:
#     st.session_state.active_session_id = None

# if "sessions" not in st.session_state:
#     st.session_state.sessions = {}

# # Sidebar for session management
# with st.sidebar:
#     st.header("Chat Sessions")

#     # New Chat Button
#     if st.button("New Chat"):
#         user_id = "user_123"  # Replace with actual user ID logic
#         response = requests.post(START_SESSION_URL, params={"user_id": user_id})
#         st.markdown(response)
#         if response.status_code == 200:
#             session_id = response.json().get("session_id")
#             st.session_state.active_session_id = session_id
#             st.session_state.sessions[session_id] = []  # Store session in the dictionary
#             st.session_state.messages = []  # Clear messages for the new session
#             st.experimental_rerun()  # Refresh the app to update the UI
#         else:
#             st.error("Failed to start a new session.")

#     # Display all chat sessions in a dropdown
#     session_options = list(st.session_state.sessions.keys())
#     if session_options:
#         selected_session = st.selectbox(
#             "Select a Chat",
#             options=session_options,
#             index=session_options.index(st.session_state.active_session_id) if st.session_state.active_session_id else 0
#         )
#         if selected_session != st.session_state.active_session_id:
#             st.session_state.active_session_id = selected_session
#             # Load chat history for the selected session
#             response = requests.get(GET_HISTORY_URL, params={"session_id": selected_session})
#             if response.status_code == 200:
#                 chat_history = response.json().get("messages", [])
#                 st.session_state.messages = chat_history
#             else:
#                 st.error("Failed to load chat history.")

# # Main chat interface
# st.title("AI Chat Assistant")

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat input
# if prompt := st.chat_input("Type your message here..."):
#     if not st.session_state.active_session_id:
#         st.warning("Please start a new chat to send a message.")
#     else:
#         # Append user message to session state
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Send message to backend
#         payload = {
#             "session_id": st.session_state.active_session_id,
#             "message": {"role": "user", "content": prompt}
#         }
#         try:
#             with st.spinner("Generating response..."):
#                 response = requests.post(SEND_MESSAGE_URL, json=payload)
#                 if response.status_code == 200:
#                     ai_response = response.json().get("response", {})
#                     st.session_state.messages.append(ai_response)
#                     with st.chat_message("assistant"):
#                         st.markdown(ai_response["content"])
#                 else:
#                     st.error(f"Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")


# ============================================================================

import streamlit as st
import requests

# Backend API URLs  
BASE_API_URL = "http://127.0.0.1:8001"
CREATE_USER_URL = f"{BASE_API_URL}/users/"
CREATE_SESSION_URL = f"{BASE_API_URL}/sessions/"
ADD_MESSAGE_URL = f"{BASE_API_URL}/messages/"
GET_USER_SESSIONS_URL = f"{BASE_API_URL}/users/"
GET_CHAT_HISTORY_URL = f"{BASE_API_URL}/sessions/"

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = None

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a user
def create_user(username, email):
    user_data = {
        "username": username,
        "email": email
    }
    response = requests.post(CREATE_USER_URL, json=user_data)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        return None

# Create a new session
def create_session(user_id, session_name):
    session_data = {
        "user_id": user_id,
        "session_name": session_name
    }
    response = requests.post(CREATE_SESSION_URL, json=session_data)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        return None

# Add a message to a session
def add_message(session_id, message, sender):
    message_data = {
        "session_id": session_id,
        "message": message,
        "sender": sender
    }
    response = requests.post(ADD_MESSAGE_URL, json=message_data)
    if response.status_code == 200:
        return True
    else:
        return False

# Get user sessions
def get_user_sessions(user_id):
    response = requests.get(f"{GET_USER_SESSIONS_URL}{user_id}/sessions/")
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Get chat history
def get_chat_history(session_id):
    response = requests.get(f"{GET_CHAT_HISTORY_URL}{session_id}/messages/")
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Sidebar for session management
with st.sidebar:
    st.header("Chat Sessions")

    # Create a new user
    if not st.session_state.username:
        username = st.text_input("Enter your username")
        email = st.text_input("Enter your email")
        if st.button("Create a new user"):
            st.session_state.user_id = create_user(username, email)
            if st.session_state.user_id:
                st.session_state.username = username
            else:
                st.error("Failed to create a new user.")

    # Start a new session
    if st.session_state.username:
        session_name = st.text_input("Enter a session name")
        if st.button("Start a new session"):
            st.session_state.active_session_id = create_session(st.session_state.user_id, session_name)
            if st.session_state.active_session_id:
                st.session_state.messages = []
            else:
                st.error("Failed to start a new session.")

    # Display all chat sessions
    if st.session_state.username:
        sessions = get_user_sessions(st.session_state.user_id)
        if sessions:
            session_options = [session["id"] for session in sessions]
            selected_session = st.selectbox(
                "Select a Chat",
                options=session_options,
                index=session_options.index(st.session_state.active_session_id) if st.session_state.active_session_id else 0
            )
            if selected_session != st.session_state.active_session_id:
                st.session_state.active_session_id = selected_session
                # Load chat history for the selected session
                chat_history = get_chat_history(selected_session)
                if chat_history:
                    st.session_state.messages = [{"role": message["sender"], "content": message["message"]} for message in chat_history]
                else:
                    st.error("Failed to load chat history.")

# Main chat interface
st.title("AI Chat Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        st.write(f"{message['role']}: {message['content']}")

# Chat input
if st.session_state.active_session_id:
    with st.form("message_form"):
        prompt = st.text_area("Type your message here...")
        if st.form_submit_button("Send"):
            add_message(st.session_state.active_session_id, prompt, "user")
            st.session_state.messages.append({"role": "user", "content": prompt})
           




# The following is streamlit frontend code, understand it and modify it according to requirements and below some requirements 
# - check if user exists or not, if exists display the existing chat session on sidebar
# - 
