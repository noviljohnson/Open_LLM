
### # requirement
# for the backend the requirement is 
# - the user will give user name and email 
# - the user will see the older/existing sessions 
# - the user will select an existing session or will create a new session
# - there will 4 other apps will available in the UI, user can select an APP and every session is associated with the app name
# - if user creates a new session, user can choose an app or the default will be 4th app("Open_LLMs")
# So, in the backend code i need
# - an API to retrieve all the sessions for an existing user
# - an to call another API running at another port with the user input (could be a query)
# - so every message the user types, it should go to the corresponding app with session info and chat history

###########################################################################################################1001NJ


from uuid import UUID
import uuid
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import requests
import shutil
import json
import os
import boto3

from typing import List

### for direct llms
from configparser import ConfigParser
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock
from llama_index.core.llms import ChatMessage
import os


# Step 1: Load AWS configuration
config_object = ConfigParser()
config_object.read(r"E:\Ollama_models\scripts\hf_config.config")
aws_info = config_object["AWS"]

s3 = boto3.client('s3', aws_access_key_id=aws_info['aws_access_key_id'],aws_secret_access_key=aws_info['aws_secret_access_key'])



"""
This is a FastAPI application that provides endpoints for user management and chat sessions.
"""

# Database Configuration
DATABASE_URL = "postgresql://postgres:Novil@localhost/chat_assistant"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """
    User Model
    This is a database model for a user.

    Attributes:
        user_id (UUID): The unique identifier for the user.
        user_ip (str): The IP address of the user.
        user_name (str): The username of the user.
        chat_sessions (List[ChatSession]): The chat sessions associated with the user.
        chat_histories (List[ChatHistory]): The chat histories associated with the user.

    Relationships:
        chat_sessions (List[ChatSession]): The chat sessions associated with the user.
        chat_histories (List[ChatHistory]): The chat histories associated with the user.
    """
    __tablename__ = "users"
    user_id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_ip = Column(String, unique=True, nullable=False)
    user_name = Column(String, nullable=False)
    chat_sessions = relationship("ChatSession", back_populates="user")
    chat_histories = relationship("ChatHistory", back_populates="user")
    # email = Column(String, unique=True, nullable=False)
    

class ChatSession(Base):
    """
    Database model for a chat session.

    Attributes:
        id (UUID): The unique identifier for the chat session.
        user_id (UUID): The ID of the user who created the chat session.
        session_name (str): The name of the chat session.
        app_name (str): The name of the application associated with the chat session.
        created_at (datetime): The timestamp when the chat session was created.
        chat_histories (list): A list of chat histories associated with this chat session.
        user (User): The user who created this chat session.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "session_name": "Chat Session 1",
            "app_name": "My App",
            "created_at": "2022-01-01 12:00:00",
            "chat_histories": [...],
            "user": {...}
        }
    """
    __tablename__ = "chat_sessions"
    session_id = Column(PostgresUUID(as_uuid=True), primary_key=True,default=uuid.uuid4, index=True)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    session_name = Column(String, nullable=False)
    app_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat_histories = relationship("ChatHistory", back_populates="session")
    user = relationship("User", back_populates="chat_sessions")


class ChatHistory(Base):
    """
    Database model for a chat history.

    Attributes:
        id (int): The unique identifier for the chat history.
        session_id (UUID): The ID of the chat session associated with this chat history.
        message (str): The message in this chat history.
        sender (str): The sender of this chat history.
        created_at (datetime): The timestamp when this chat history was created.
        session (ChatSession): The chat session associated with this chat history.
        user (User): The user associated with this chat history.

    Example:
        {
            "id": 1,
            "session_id": "123e4567-e89b-12d3-a456-426614174000",
            "message": "Hello",
            "sender": "John Doe",
            "created_at": "2022-01-01 12:00:00",
            "session": {...},
            "user": {...}
        }
    """
    __tablename__ = "chat_history"
    history_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(PostgresUUID(as_uuid=True), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    app_name = Column(String, nullable=False)
    message = Column(Text)
    sender = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="chat_histories")
    user = relationship("User", back_populates="chat_histories")


Base.metadata.create_all(bind=engine)


app = FastAPI()

class UserCheck(BaseModel):
    """
    This is a Pydantic model for verifying/checking an existing user details.

    Attributes:
        user_ip (str): The IP address of the user.
    """
    user_ip: str

class UserCreate(BaseModel):
    """
    This is a Pydantic model for creating a new user.

    Attributes:
        user_ip (str): The IP address of the user.
        user_name (str): The name of the user.
    """
    user_ip: str
    user_name: str

    # def __init__(self, user_ip: str, user_name: str):
    #     """
    #     Initialize the UserCreate model.

    #     Args:
    #         user_ip (str): The IP address of the user.
    #         user_name (str): The name of the user.
    #     """
    #     self.user_ip = user_ip
    #     self.user_name = user_name


class ChatSessionCreate(BaseModel):
    """
    This is a Pydantic model for creating a new chat session.
    
    Attributes:
        user_id (UUID): The ID of the user who created the chat session.
        session_name (str): The name of the chat session.
        app_name (str): The name of the app associated with this chat session.
    """
    user_id: UUID
    session_name: str
    app_name: str

    # def __init__(self, user_id: UUID, session_name: str, app_name: str):
    #     """
    #     Initialize the ChatSessionCreate model.
        
    #     Args:
    #         user_id (int): The ID of the user who created the chat session.
    #         session_name (str): The name of the chat session.
    #         app_name (str): The name of the app associated with this chat session.
    #     """
    #     self.user_id = user_id
    #     self.session_name = session_name
    #     self.app_name = app_name


class ChatMessageCreate(BaseModel):
    """
    This is a Pydantic model for creating a new chat message.
    
    Attributes:
        session_id (int): The ID of the chat session associated with this chat message.
        message (str): The message in this chat message.
        sender (str): The sender of this chat message.
    """
    session_id: UUID
    message: str
    sender: str

    # def __init__(self, session_id: UUID, message: str, sender: str):
    #     """
    #     Initialize the ChatMessageCreate model.
        
    #     Args:
    #         session_id (int): The ID of the chat session associated with this chat message.
    #         message (str): The message in this chat message.
    #         sender (str): The sender of this chat message.
    #     """
    #     self.session_id = session_id
    #     self.message = message
    #     self.sender = sender

class QueryRequest(BaseModel):
    """
    This is a Pydantic model for querying.
    
    Attributes:
        user_id (int): The ID of the user who sent the query.
        session_id (int): The ID of the chat session associated with this query.
        query (str): The query sent by the user.
    """
    user_id: UUID
    session_id: UUID
    query: str
    app_name: str
    model_name: str = "Claude 3"

    # def __init__(self, user_id: int, session_id: UUID, query: str):
    #     """
    #     Initialize the QueryRequest model.
        
    #     Args:
    #         user_id (int): The ID of the user who sent the query.
    #         session_id (int): The ID of the chat session associated with this query.
    #         query (str): The query sent by the user.
    #     """
    #     self.user_id = user_id
    #     self.session_id = session_id
    #     self.query = query

class UserData(BaseModel):
    """
    This is a Pydantic model for uploading files for DocuMentors.
    
    Attributes:
        user_id (uuid): The ID of the chat session associated with this chat message.
        files: List of files that user uploaded
    """
    user_id: UUID
    # files: List[UploadFile] = File(...)


def get_db():
    """
    Get a database session.
    
    Yields:
        db (SessionLocal): A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return "HI, Welcome!"

@app.post("/verify/", response_model=dict)
def user_verify(user: UserCheck, db=Depends(get_db)):
    """
    Check/verify if user exists.
    Args:
        user_ip (UserCheck): The user to verify.
    Returns:
        dict: A dictionary containing the ID and username of the existing user.
    
    To make an API call:
    * Method: POST
    * URL: /verify/
    * Data: {"user_ip": "ipaddr"}
    * Sample API call: requests.post("http://localhost:8000/verify/", json={"user_ip": "10.8.90.14"})
    """
    user_check =db.query(User).filter(User.user_ip == user.user_ip).first()
    # passing table stucture with table name
    # passing query: filter query, user_ip from table vs user ip from api call
    if not user_check:
        raise HTTPException(status_code=404, detail="User Not Found")
    return {"user_id": user_check.user_id, "user_ip": user_check.user_ip, "user_name": user_check.user_name, "verified":True}

@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db=Depends(get_db)):
    """
    Create a new user.
    
    Args:
        user (UserCreate): The user to create.
        db (SessionLocal): A database session.
    
    Returns:
        dict: A dictionary containing the ID and username of the created user.
    
    To make an API call:
    * Method: POST
    * URL: /users/
    * Data: {"username": "username", "user_ip": "10.80.9.14"}
    * Sample API call: requests.post("http://localhost:8000/users/", json={"user_name": "username", "user_ip": "10.8.90.14"})
    """
    new_user = User(user_ip=user.user_ip, user_name=user.user_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.user_id, "user_ip": new_user.user_ip, "user_name": new_user.user_name}


@app.get("/users/{user_id}/sessions/", response_model=list)
def get_user_sessions(user_id: UUID, db=Depends(get_db)):
    """
    Get all chat sessions for a user.
    
    Args:
        user_id (int): The ID of the user.
        db (SessionLocal): A database session.
    
    Returns:
        list: A list of dictionaries containing the ID, session name, and app name of each chat session.
    
    To make an API call:
    * Method: GET
    * URL: /users/{user_id}/sessions/
    * Params: user_id (int)
    * Sample API call: requests.get("http://localhost:8000/users/1/sessions/")
    """
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this user")
    return [{"session_id": s.session_id, "session_name": s.session_name, "app_name": s.app_name} for s in sessions]


@app.get("/users/{session_id}/chat_history/", response_model=list)
def get_chat_history(session_id: UUID, db=Depends(get_db)):
    """
    Get all chat history for a user for a session.
    
    Args:
        session_id (UUID): The ID of the user.
    
    Returns:
        list: A list of dictionaries containing the ID, session name, and app name of each chat session.
    
    To make an API call:
    * Method: GET
    * URL: /users/{user_id}/sessions/
    * Params: session_id (int)
    * Sample API call: requests.get("http://localhost:8000/users/1/chat_history/")
    """
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    if not history:
        raise HTTPException(status_code=404, detail=f"No chat history found for this this session : {session_id}")
    return [{"session_id": s.session_id, "app_name": s.app_name, "message":s.message, "sender":s.sender, "timestamp":s.created_at} for s in history]


@app.post("/sessions/", response_model=dict)
def create_chat_session(session: ChatSessionCreate, db=Depends(get_db)):
    """
    Create a new chat session.
    
    Args:
        session (ChatSessionCreate): The chat session to create.
        db (SessionLocal): A database session.
    
    Returns:
        dict: A dictionary containing the ID and session name of the created chat session.
    
    To make an API call:
    * Method: POST
    * URL: /sessions/
    * Data: {"user_id": 1, "session_name": "session_name", "app_name": "app_name"}
    * Sample API call: requests.post("http://localhost:8000/sessions/", json={"user_id": 'b6b0a764-daff-422a-be6c-abb34bc53dc0', "session_name": "session_name", "app_name": "app_name"})
    """
    print("create chat session")
    user = db.query(User).filter(User.user_id == session.user_id).first()
    if not user:
        print("user  ", user)
        raise HTTPException(status_code=404, detail="User not found")
    new_session = ChatSession(user_id=user.user_id, session_name=session.session_name, app_name=session.app_name)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.session_id, "session_name": new_session.session_name, "app_name": new_session.app_name}


@app.post("/messages/", response_model=dict)
def add_message_to_session(message: ChatMessageCreate, db=Depends(get_db)):
    """
    Add a message to a chat session.
    
    Args:
        message (ChatMessageCreate): The message to add.
        db (SessionLocal): A database session.
    
    Returns:
        dict: A dictionary containing the ID of the added message.
    
    To make an API call:
    * Method: POST
    * URL: /messages/
    * Data: {"session_id": 1, "message": "message", "sender": "sender"}
    * Sample API call: requests.post("http://localhost:8000/messages/", json={"session_id": 1, "message": "message", "sender": "sender"})
    """
    session = db.query(ChatSession).filter(ChatSession.id == message.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    user = db.query(User).filter(User.user_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_message = ChatHistory(session_id=message.session_id, user_id=user.user_id, app_name=session.app_name, message=message.message, sender=message.sender)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    # Call API of another app with user input
    app_url = get_app_url(session.app_name)
    if app_url:
        send_message_to_app(app_url, message.message, session.id)
    return {"id": new_message.id}


@app.post("/query/", response_model=dict)
def query(request: QueryRequest, db=Depends(get_db)):
    """
    Send a query to the LLM.
    
    Args:
        request (QueryRequest): The query to send.
        db (SessionLocal): A database session.
    
    Returns:
        dict: A dictionary containing the response from the LLM.
    
    To make an API call:
    * Method: POST
    * URL: /query/
    * Data: {"user_id": 1, "session_id": 1, "query": "query"}
    * Sample API call: requests.post("http://localhost:8000/query/", json={"user_id": 1, "session_id": 1, "query": "query", "app_name":"APP"})
    * if the user selects Direct LLMs then the payload will be : json={"user_id": 1, "session_id": 1, "query": "query", "app_name":"APP", "model_name":"LLM name"}
    """
    user = db.query(User).filter(User.user_id  == request.user_id).first()
    if not user:
        print(user)
        raise HTTPException(status_code=404, detail="User not found")
    
    session = db.query(ChatSession).filter(ChatSession.session_id == request.session_id).first()
    if not session:
        print(session)
        raise HTTPException(status_code=404, detail="Chat session not found")
    

    try:
        if session.app_name in ["FailWise","RuleRadar"]: 
            app_url = get_app_url(session.app_name)
            response = requests.post(app_url, json={"message": str(request.query)})
            response.raise_for_status()
            response_data = response.json() 
        elif request.app_name == "DocuMentor":
            pass
        elif session.app_name == "Direct LLMs":
            response_data = {"response":llm_response(str(request.query), request.model_name)}

        new_message = ChatHistory(session_id=request.session_id, 
                                  user_id=user.user_id, 
                                  app_name=session.app_name, 
                                  message=request.query, 
                                  sender="user")
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        new_message = ChatHistory(session_id=request.session_id, 
                                  user_id=user.user_id, 
                                  app_name=session.app_name, 
                                  message=response_data["response"], 
                                  sender="assistant")
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return {"response": response_data["response"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to send query to LLM")

@app.post("/uploadfile/", response_model=dict)
async def create_upload_file( user_data: UserData, files: List[UploadFile] = File(...), db=Depends(get_db)):
    user = db.query(User).filter(User.user_id  == user_data.user_id).first()
    if not user:
        print(user)
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # create a session id for a user session for file storage in AWS s3
        session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')

        # create a temporary folder to store the uploaded files
        temp_dir = os.path.join(os.getcwd(),'temp-'+user_data.user_id)

        for file in files:
            file_path = os.path.join(temp_dir, file.name)
            # with open(file_path, 'wb') as f:
            #     f.write(file.getvalue())
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # s3_filename = os.path.basename(file_path)
            s3_key = f"{user.user_ip}/{session_id}/{file.name}"
            s3.upload_file(file_path, aws_info["bucket_name"], s3_key)
            

        ## Clean up the temporary directory
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir,ignore_errors=True)

        return {
            "s3_filepath": f"{user.user_ip}/{session_id}"
        }

    except Exception as e:
        return JSONResponse(content={
            "error": str(e)
        }, status_code=500)



def get_app_url(app_name):
    """
    Get the URL of an app based on the app name.
    
    Args:
        app_name (str): The name of the app.
    
    Returns:
        str: The URL of the app.
    """
    apps = {
        "FailWise": 'http://10.60.90.31:5001',
        "RuleRadar": 'http://10.60.90.31:5001',
        "APP2": "http://localhost:8082",
        "APP3": "http://172.27.109.125:8005/chat",#"http://127.0.0.1:8003/chat",
        "Open_LLMs": "http://localhost:8084"
    }
    
    # saturn_flask_url = 'http://10.8.30.14:5000/'
    saturn_flask_url = 'http://10.60.90.54:5000'
    ruleradar_v2_flask = "http://10.60.90.31:5002"
    return apps.get(app_name)


def send_message_to_app(app_url, message, session_id):
    """
    Send a message to an app.
    
    Args:
        app_url (str): The URL of the app.
        message (str): The message to send.
        session_id (int): The ID of the chat session.
    """
    url = f"{app_url}/message"
    data = {"message": message, "session_id": session_id}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to send message to app")



########## Direct LLM from AWS Bedrock



# Step 2: Initialize Bedrock LLM and embedding model
bedrock_models_list = {"Claude 3":"anthropic.claude-3-sonnet-20240229-v1:0",
            "Llama 3 8B Instruct": "meta.llama3-8b-instruct-v1:0"
 }

System_prompt_for_BedrockModels ="""You are a Genarative ai assistant, please respond to the user queries based on following instructions 
                - Do not Give too much information for Direct and short questions
                - Give Structured point wise answers for Questions that require lengthy explanations
                - Always give responses in Markdown format so that the structure will be maintained in the UI
                - DO NOT return any other tokens (like <SYS>, <END> etc...)
                """


# Generate LLM response
def llm_response(message, model_id="Claude 3", models_list=bedrock_models_list):

    llm = Bedrock(
    model=models_list[model_id],
    region_name="us-east-1",
    aws_access_key_id=aws_info["aws_access_key_id"],
    aws_secret_access_key=aws_info["aws_secret_access_key"]
    )

    messages = [
        ChatMessage(
            role="system", 
            content= System_prompt_for_BedrockModels
        ),
        ChatMessage(
            role="user", content=message
        ),
    ]
    response = llm.chat(messages)
    return response.message.content.strip()  # Correctly formatted title










#### Embedding model initialization # use if required
# embedding_model = BedrockEmbedding(
#     model_name="amazon.titan-embed-text-v2:0",
#     region_name="us-east-1",
#     aws_access_key_id=aws_info["aws_access_key_id"],
#     aws_secret_access_key=aws_info["aws_secret_access_key"]
# )












### Considerations 
# """
# Error Handling: While you're handling some errors, you might want to consider adding more comprehensive error handling to ensure that your application remains robust and reliable.

# Database Connections: You're creating a new database connection for each request. This can be inefficient and may lead to connection leaks. Consider using a connection pool to manage your database connections.

# Security: Your application seems to be using plain HTTP. Consider using HTTPS to encrypt your data in transit.

# Input Validation: Your application is using Pydantic models to validate input. However, you might want to consider adding additional validation to ensure that the input is valid and consistent with your application's requirements.

# API Documentation: Your application could benefit from API documentation. Consider using a library like Swagger or OpenAPI to generate API documentation automatically.

# Testing: Your application lacks tests. Consider adding unit tests and integration tests to ensure that your application is working as expected.

# Performance: Your application's performance might be impacted by the number of database queries it's making. Consider using caching or optimizing your database queries to improve performance.

# Session Management: Your application is managing sessions, but it's not clear how sessions are being closed. Consider adding session closure logic to ensure that sessions are properly cleaned up.

# LLM Query: Your application is sending a query to an LLM, but it's not clear how the LLM is being managed. Consider adding logic to manage the LLM and ensure that it's available when needed.

# Code Organization: Your application's code is a bit monolithic. Consider breaking it up into smaller modules or packages to improve maintainability and reusability.
# """



# ### code-specific suggestions:
# """
# In the get_user_sessions endpoint, consider adding pagination to handle cases where a user has many sessions.
# In the create_chat_session endpoint, consider validating the app name to ensure that it's one of the allowed apps.
# In the add_message_to_session endpoint, consider adding a check to ensure that the session exists before adding a message to it.
# In the query endpoint, consider adding a check to ensure that the session exists before sending a query to the LLM.
# """

# logging
# authentication
# Exception
# Sage integration
# Attachiments handling - Documentor
# Direct llms (AWS llm access)
