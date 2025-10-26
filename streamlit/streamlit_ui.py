import sys
import os
# Adding parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import requests
from pymongo import MongoClient
from config.settings import (
    COSMOS_CONNECTION_STRING,  # Cosmos DB connection string
    COSMOS_DATABASE_NAME,      # Database name
    COSMOS_COLLECTION_NAME     # Collection name
)

# Setup Streamlit page configuration
st.set_page_config(page_title="📱 Mobile Store Chatbot", layout="wide")
# Connect to Cosmos DB
mongo_client = MongoClient(COSMOS_CONNECTION_STRING)
db = mongo_client[COSMOS_DATABASE_NAME]
chat_collection = db[COSMOS_COLLECTION_NAME]

# Display main title and description on the page
st.title("Mobile Store Chatbot")
st.write("Ask a question about mobiles, accessories, offers, or services!")

# Sidebar for chat history
st.sidebar.header("Chat History")
if st.sidebar.button("Clear Chat History"):
    # Clear chat history from Cosmos DB when button is clicked
    chat_collection.delete_many({})
    st.sidebar.success("Chat history cleared!")

# Fetch the latest 20 messages from Cosmos DB and display them
history = list(chat_collection.find().sort("_id", -1).limit(20))
if history:
    for msg in reversed(history):
        # Display the most recent chat message in the sidebar
        st.sidebar.write(f"- {msg.get('content', '')[:50]}{'...' if len(msg.get('content', '')) > 50 else ''}")
else:
    st.sidebar.write("No chat history yet.")

# Handle user input through a form
if "input" not in st.session_state:
    st.session_state["input"] = ""

with st.form("query_form", clear_on_submit=True):
    user_query = st.text_input("Your question:", key="input")  # Text input field for user query
    submit = st.form_submit_button("Ask")  # Button to submit the query

if submit and user_query.strip():
    with st.spinner("Thinking..."):
        try:
            # Send the user query to the Flask API (backend)
            response = requests.post(
                "http://localhost:5000/chat",  # Flask API endpoint
                json={"query": user_query}  # Sending user query as JSON
            )
            if response.status_code == 200:
                # Parse the response from Flask and display the bot's answer
                answer = response.json().get("response", "⚠️ No response.")
            else:
                answer = "⚠️ Server error. Please try again."
        except Exception as e:
            # Handle any errors in connecting to Flask API
            answer = f"❌ Error connecting to backend: {e}"

    # Display user query and bot's response
    st.markdown(f"**You:** {user_query}")
    st.markdown(f"**Bot:** {answer}")

    # Store the user query in Cosmos DB for chat history
    chat_collection.insert_one({"role": "user", "content": user_query})
