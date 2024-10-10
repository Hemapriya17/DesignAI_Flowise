import streamlit as st
import requests
import json

# First API URL
API_URL_1 = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/b83d91c5-7db1-4426-815b-d3b4e48cde31"

# Second API URL (for the Next button)
API_URL_2 = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/f9893e95-2172-4b00-9b45-b14748ad1ae9"

# Function to send request to Flowise API
def query_flowise_api(api_url, payload):
    response = requests.post(api_url, json=payload)
    
    # Check if response is valid and contains JSON
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from the API"}

# Function to convert JSON response to table data
def json_to_table_data(response_data):
    # Parse the JSON string from the 'text' field
    json_str = response_data.get('text', '{}').strip('```json').strip()  # Strip Markdown and extra spaces
    
    # Attempt to load JSON, handling any errors
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError:
        return [], ["Error decoding JSON from 'text' field."]
    
    components_and_functions = json_data.get('components_and_functions', [])
    
    if not components_and_functions:
        return [], ["No data found in the 'components_and_functions' key."]
    
    # Prepare data for the table
    table_data = [[item['specification_category'], item['component'], item['function']] 
                  for item in components_and_functions]
    
    return table_data

# Streamlit app
st.title("System Design AI")

# Initialize session state to store the generated table data
if 'table_data' not in st.session_state:
    st.session_state.table_data = None
    st.session_state.locked = False  # To lock the table after clicking Next

# Text input for user to enter their question
user_input = st.text_input("Generate experimentation plan for...")

# Button to generate response from the first API
if st.button("Generate") and not st.session_state.locked:  # Disable button when table is locked
    if user_input:
        with st.spinner("Genenrating Components and function..."):
            # Send the user input to the first API and get the response
            response = query_flowise_api(API_URL_1, {"question": user_input})
            
            # Debug: Display raw API response
            # st.subheader("Raw API Response:")
            # st.json(response)
            
            # Handle cases where there's an error in the response
            if "error" in response:
                st.error(response["error"])
            else:
                # Convert JSON response to table data
                table_data = json_to_table_data(response)
                
                # Store the generated table data in session state
                st.session_state.table_data = table_data

# Display the generated table if available
if st.session_state.table_data:
    st.subheader("Components and Functions:")
    headers = ['Specification Category', 'Component', 'Function']
    
    # Combine headers with data and display table
    table_data = [headers] + st.session_state.table_data
    st.table(table_data)  # Display as table
    
    # Show the "Next" button only if the table is generated
    if st.button("Next") and not st.session_state.locked:
        # Lock the table to prevent further changes
        st.session_state.locked = True
        
        # Prepare the new "question" from the table data
        question_data = {
            "components_and_functions": [
                {"specification_category": row[0], "component": row[1], "function": row[2]}
                for row in st.session_state.table_data
            ]
        }
        question_json = json.dumps(question_data)  # Convert to JSON format
        
        # st.subheader("Next Step: Sending Data")
        # st.write(f"Sending the following components and functions as a question:\n{question_json}")
        
        # Send the generated data to the second API
        with st.spinner("Genenrating ENgineering Requirements..."):
            response = query_flowise_api(API_URL_2, {"question": question_json})
            
            # Show API response
            st.subheader("Engineering Requirements:")
            st.json(response)
else:
    st.write("Please generate the components and functions first.")
