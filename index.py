import streamlit as st
import requests
import json

# Flowise API URL
API_URL = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/b83d91c5-7db1-4426-815b-d3b4e48cde31"

# Function to send request to Flowise API
def query_flowise_api(user_input):
    payload = {"question": user_input}
    response = requests.post(API_URL, json=payload)
    
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

# Text input for user to enter their question
user_input = st.text_input("Generate experimentation plan for...")

# Button to generate response
if st.button("Generate"):
    if user_input:
        with st.spinner("Processing..."):
            # Send the user input to the Flowise API and get the response
            response = query_flowise_api(user_input)
            
            # Debug: Display raw API response
            st.subheader("Raw API Response:")
            st.json(response)
            
            # Handle cases where there's an error in the response
            if "error" in response:
                st.error(response["error"])
            else:
                # Convert JSON response to table data
                table_data = json_to_table_data(response)
                
                # Display the result as a table
                if table_data:
                    st.subheader("Formatted Table:")
                    headers = ['Specification Category', 'Component', 'Function']
                    
                    # Ensure headers and data are lists
                    table_data = [headers] + table_data  # Combine headers with data
                    st.table(table_data)  # Display as table
                else:
                    st.write("No components and functions found.")
    else:
        st.write("Please enter a question.")
