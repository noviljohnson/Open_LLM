
import requests
## testing llm api

# ress =requests.post("http://127.0.0.1:8005/chat", json={"message":"Give me a list of all the planets in our solar system."})
ress =requests.post("http://172.27.109.125:8005/chat", json={"message":"Give me a list of all the planets in our solar system."})
print(ress.json()['response'])



BASE_API_URL = "http://127.0.0.1:8004" 
create_user = f"{BASE_API_URL}/users/"
get_user_sessions = "{BASE_API_URL}/users/{user_id}/sessions/"
create_chat_session = f"{BASE_API_URL}/sessions/"
get_chat_history = "{BASE_API_URL}/users/{session_id}/chat_history/"
query = f"{BASE_API_URL}/query/"
### creating/adding a new user
response = requests.post(create_user,json={"user_name": "ALUser", "user_ip": "10.80.9.14"})
response
user_details = response.json()
user_details
### creating first session
sess_res = requests.post(create_chat_session, json={"user_id": 'aa6aa0e6-3443-49de-83b8-86c3bf2ee3f7', #user_details['user_id'],
                                "session_name": "Intro", 
                                "app_name": "APP3"})
sess_res
list(set([]))
create_chat_session
### get_user_sessions
usr_ses = requests.get(get_user_sessions.format(BASE_API_URL=BASE_API_URL, 
                                                user_id='aa6aa0e6-3443-49de-83b8-86c3bf2ee3f7'))
usr_ses
usr_ses.json()
### get chat history
usr_hist = requests.get(get_chat_history.format(BASE_API_URL=BASE_API_URL, 
                                                session_id='0d40a094-d62d-4c41-9054-09937aa688af'))
usr_hist
usr_hist.json()
"""history_id |  user_id | session_id | app_name |  message | sender | created_at"""
get_chat_history.format(BASE_API_URL=BASE_API_URL, 
                                                session_id='0d40a094-d62d-4c41-9054-09937aa688af')
### Query API
q_res = requests.post(query, json={"session_id":'0d40a094-d62d-4c41-9054-09937aa688af', "user_id":'aa6aa0e6-3443-49de-83b8-86c3bf2ee3f7', "query":"give me the list of all the stars that are named by humans"})
q_res
print(q_res.json()['response'])

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()
ip

import requests

API_URL = "http://127.0.0.1:8004/verify/"
payload = {
    "user_ip": "10.80.9.14"
}
response = requests.post(API_URL, json=payload)
response

#  CREATE TABLE chat_sessions (
#  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#  user_id UUID NOT NULL,
#  session_name VARCHAR(255) NOT NULL,
#  app_name VARCHAR(100) NOT NULL,
#  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
#  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
#  );
# CREATE TABLE chat_history (
#     history_id SERIAL PRIMARY KEY,
#     user_id UUID NOT NULL,
#     session_id UUID NOT NULL,
#     app_name VARCHAR(100) NOT NULL,
#      message TEXT,
#     sender VARCHAR(255),
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
#     CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
#     CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
#     );
## DB connection checking
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
# Database connection URL
DATABASE_URL = "postgresql://postgres:Novil@localhost:5432/chat_assistant"

# Create the engine
engine = create_engine(DATABASE_URL)

engine

def test_connection():
    try:
        # Test the connection
        with engine.connect() as connection:
            # Use the `text()` function to execute raw SQL
            result = connection.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            print(result)
            db_version = result.fetchall()
            print(f"Connection successful! PostgreSQL version: {db_version}")
    except OperationalError as e:
        print(f"Error: Unable to connect to the database.\n{e}")

# Test the connection
if __name__ == "__main__":
    test_connection()
result

