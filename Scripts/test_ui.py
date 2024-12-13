

# import streamlit as st
# import requests
# import json

# # Initialize the app
# st.title("Chat with LLM")
# context = ""
# questions = [
#     {"role": "assistant", "content": "You are an expert at answering questions. Please respond in this format: 'Answer: [answer]' for each question. Do not provide explanations or elaborations. Only provide the answer."},
#     {"role": "user", "content": "What is your name?"}
# ]
# answers = []
# new_questions = []

# # Function to send questions and get answers
# def send_questions(questions):
#     url = 'http://localhost:5000/ask'
#     data = {'messages': questions}
#     response = requests.post(url, json=data)
#     response = response.json()['response']
#     return response

# # Function to generate new questions
# def generate_questions(context):
#     url = 'http://localhost:5000/generate'
#     data = {'context': context}
#     response = requests.post(url, json=data)
#     new_questions = response.json()['new_questions']
#     return new_questions

# # Main app
# x = 0
# # while True:
# st.write("Current question:")
# st.write(questions[-1]['content'])
# user_input = st.text_input("Enter your response", key=str(x))
# x += 1
# if st.button("SUBMIT", key=str(x)+str(x)):
#     answers.append(user_input)
#     response = send_questions(questions)
#     if "Answer: " in response:
#         context += user_input + "\n"
#         response = response.replace("Answer: ", "")
#         if len(answers) < 3:
#             questions.append({"role": "assistant", "content": "Next question: "})
#             if len(answers) == 0:
#                 questions.append({"role": "assistant", "content": "What is your age?"})
#             elif len(answers) == 1:
#                 questions.append({"role": "assistant", "content": "Where are you from?"})
#         else:
#             new_questions = generate_questions(context)
#             questions = new_questions
#             context = ""
#             answers = []
#     else:
#         st.write("Invalid response")
#         # continue
# if st.button("REGENERATE", key=str(x)+str(x)+str(x)):
#     new_questions = generate_questions(context)
#     questions = new_questions
#     context = ""
#     answers = []
    






import streamlit as st
from streamlit_option_menu import option_menu
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx


import os, sys
import requests


import json
# import gptQA


st.set_page_config(layout="wide")


# Function to send questions and get answers
def send_questions(questions):
    url = 'http://localhost:5000/ask'
    data = {'messages': questions}
    response = requests.post(url, json=data)
    response = response.json()['response']
    return response

    
def set_page_container_style():
    padding_top = 1.6
    st.markdown(f"""
        <style>
        .block-container{{
            padding-top: {padding_top}rem;    }}
    </style>""",
        unsafe_allow_html=True,
    )

def get_remote_ip() -> str:
    """Get remote ip."""

    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None
    remote_ip = session_info.request.remote_ip
    st.write(remote_ip)
    return remote_ip


agents_flask_url = 'http://10.60.90.31:5001'
# saturn_flask_url = 'http://10.8.30.14:5000/'
saturn_flask_url = 'http://10.60.90.54:5000'
ruleradar_v2_flask = "http://10.60.90.31:5002"



## SESSION STATE 
#########################################
if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever_from_llm" not in st.session_state:
    st.session_state["retriever_from_llm"] = False




set_page_container_style()


with st.sidebar:
    option = option_menu(
        menu_title = None,
        options = ["Pre-Solutioning"],
        orientation="vertical",
        icons=['chat','list-task'],
    )


## 2) CHAT
if option == 'Pre-Solutioning':
    
    with st.sidebar:

        uploadedFiles = st.file_uploader(" ", accept_multiple_files=True) 
        files_uploaded = [file.name for file in uploadedFiles]

    st.session_state.messages.append({"role": "assistant", "content":"Welcome to Workbench"})
    # st.session_state.messages.append({"role": "assistant", "content":""})

    st.markdown("<h3 style='color:#A9A9A9;'>Chat Session</h3>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(""):
        print("=============================\nuser Q ---> ", prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        res = send_questions(prompt)

        
        

        
