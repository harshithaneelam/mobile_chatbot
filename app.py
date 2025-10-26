from flask import Flask, request, jsonify
import sys
import os

# Add the 'mobilebot' folder to the system path so Flask can find the necessary modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'mobilebot')))

# Import the 'get_response' function from your existing 'autogen_module' in the agents folder
from agents.autogen_module import get_response

# Initialize the Flask application
app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint for Streamlit to send user queries."""
    # Get the incoming JSON data from Streamlit
    data = request.get_json()
    user_query = data.get("query", "")  # Extract the user query from the data

    # If no query is provided, return an error response
    if not user_query.strip():
        return jsonify({"response": "Please provide a question."}), 400

    try:
        # Call your existing backend logic to generate a response for the user's query
        answer = get_response(user_query)
        # Return the response as a JSON object to Streamlit
        return jsonify({"response": answer})
    except Exception as e:
        # If there’s an error, log it and send an error response
        print(f"❌ Flask error: {e}")
        return jsonify({"response": "⚠️ Error processing your request."}), 500


if __name__ == "__main__":
    # Run the Flask app in debug mode (for development purposes)
    app.run(debug=True)
