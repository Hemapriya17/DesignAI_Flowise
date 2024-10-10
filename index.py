import streamlit as st
import requests
import json
import re

# API URLs
Component_Function = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/b83d91c5-7db1-4426-815b-d3b4e48cde31"
Engineering_Requirements = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/f9893e95-2172-4b00-9b45-b14748ad1ae9"
Component_Diagram = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/3e98e228-996a-4205-8c75-3cf34774b088"
Function_Diagram = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/9297a1fe-c925-4c00-9217-608d891b81ef"
FMEA = "https://hemapriyadharshini-flowise.hf.space/api/v1/prediction/fe1c2f99-b3a6-4b2f-9145-c6e07c686483"

# Function to query Flowise API
def query_flowise_api(api_url, payload):
    response = requests.post(api_url, json=payload)
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from the API"}

# Function to convert JSON response to table data for components and functions
def json_to_table_data(response_data):
    json_str = response_data.get('text', '{}').strip('```json').strip()  # Strip Markdown and extra spaces
    
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError:
        return [], ["Error decoding JSON from 'text' field."]
    
    components_and_functions = json_data.get('components_and_functions', [])
    
    if not components_and_functions:
        return [], ["No data found in the 'components_and_functions' key."]
    
    table_data = [[item['specification_category'], item['component'], item['function']] 
                  for item in components_and_functions]
    
    return table_data

# Function to convert JSON response to table data for Engineering Requirements
def json_to_engineering_req_table(response_data):
    text = response_data.get('text', '')
    json_match = re.search(r'```json\n([\s\S]*?)\n```', text)
    
    if not json_match:
        return [["No JSON data found in the response."]]
    
    json_str = json_match.group(1)
    
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError:
        return [["Error decoding JSON from 'text' field."]]
    
    table_data = [[item.get('id', ''), item.get('user_need', ''), 
                   item.get('tech_id', ''), item.get('description', '')] 
                  for item in json_data]
    
    return table_data if table_data else [["No data found in the JSON."]]

# Function to convert FMEA response to table data
def json_to_fmea_table(response_data):
    json_str = response_data.get('text', '').strip('```json').strip()
    
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError:
        return [], ["Error decoding JSON from 'text' field."]
    
    fmea_entries = json_data.get('fmea', [])
    
    if not fmea_entries:
        return [], ["No data found in the 'fmea' key."]
    
    table_data = [
        [
            entry.get('id', ''),
            entry.get('name_of_related_function', ''),
            entry.get('name_of_requirement', ''),
            entry.get('potential_failure_mode', ''),
            entry.get('effects_of_failure', ''),
            entry.get('severity', ''),
            entry.get('cause_of_failure', ''),
            entry.get('occurance', ''),
            entry.get('design_controls', ''),
            entry.get('detection', ''),
            entry.get('rpn', ''),
            entry.get('recommended_actions', '')
        ]
        for entry in fmea_entries
    ]
    
    return table_data

# Function to query the Mermaid API for component diagram
def query_mermaid_api(user_input):
    response = requests.post(Component_Diagram, json={"question": user_input})
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from mermaid API"}

# Function to query the function diagram API
def query_function_diagram_api(user_input):
    response = requests.post(Function_Diagram, json={"question": user_input})
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from function diagram API"}

# Function to query the FMEA API
def query_fmea_api(user_input):
    response = requests.post(FMEA, json={"question": user_input})
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid response from FMEA API"}

# Streamlit app
st.title("System Design AI")

# Initialize session state to store generated table data
if 'table_data' not in st.session_state:
    st.session_state.table_data = None
    st.session_state.eng_req_data = None
    st.session_state.locked = False  # To lock the table after clicking Next
    st.session_state.component_diagram = None
    st.session_state.function_diagram = None
    st.session_state.fmea_data = None

# Text input for user to enter their question
user_input = st.text_input("Generate experimentation plan for...")

# Button to generate response from the first API
if st.button("Generate") and not st.session_state.locked:  # Disable button when table is locked
    if user_input:
        with st.spinner("Generating Components and Functions..."):
            response = query_flowise_api(Component_Function, {"question": user_input})
            if "error" in response:
                st.error(response["error"])
            else:
                table_data = json_to_table_data(response)
                st.session_state.table_data = table_data

# Display the generated table if available
if st.session_state.table_data:
    st.subheader("Components and Functions:")
    headers = ['Specification Category', 'Component', 'Function']
    table_data = [headers] + st.session_state.table_data
    st.table(table_data)

    # Show the "Next" button only if the table is generated
    if st.button("Next") and not st.session_state.locked:
        st.session_state.locked = True
        question_data = {
            "components_and_functions": [
                {"specification_category": row[0], "component": row[1], "function": row[2]}
                for row in st.session_state.table_data
            ]
        }
        question_json = json.dumps(question_data)
        
        with st.spinner("Generating Engineering Requirements..."):
            response = query_flowise_api(Engineering_Requirements, {"question": question_json})
            eng_req_table_data = json_to_engineering_req_table(response)
            st.session_state.eng_req_data = eng_req_table_data

# Display the Engineering Requirements table if available
if st.session_state.eng_req_data:
    st.subheader("Engineering Requirements:")
    headers = ['User Req ID', 'User Need', 'Technical Req ID', 'Description']
    eng_req_table = [headers] + st.session_state.eng_req_data
    st.table(eng_req_table)
    
    # Add another "Next" button for the component diagram API call
    if st.button("Next for Component Diagram"):
        with st.spinner("Generating Component Diagram..."):
            response = query_mermaid_api(user_input)
            if "error" in response:
                st.error(response["error"])
            else:
                st.session_state.component_diagram = response

# Display the component diagram if available
if st.session_state.component_diagram:
    st.subheader("Component Diagram:")
    st.json(st.session_state.component_diagram)
    
    # Add a "Next" button to generate the function diagram
    if st.button("Next for Function Diagram"):
        with st.spinner("Generating Function Diagram..."):
            response = query_function_diagram_api(user_input)
            if "error" in response:
                st.error(response["error"])
            else:
                st.session_state.function_diagram = response

# Display the function diagram if available
if st.session_state.function_diagram:
    st.subheader("Function Diagram:")
    st.json(st.session_state.function_diagram)
    
    # Add the "Next" button to generate the FMEA
    if st.button("Next for FMEA"):
        # Prepare the question from the generated components and functions
        components_and_functions_data = {
            "components_and_functions": [
                {"specification_category": row[0], "component": row[1], "function": row[2]}
                for row in st.session_state.table_data
            ]
        }
        fmea_question = json.dumps(components_and_functions_data)
        
        with st.spinner("Generating FMEA..."):
            response = query_fmea_api(fmea_question)
            fmea_table_data = json_to_fmea_table(response)
            st.session_state.fmea_data = fmea_table_data

# Display the FMEA data in table format
if st.session_state.fmea_data:
    st.subheader("FMEA Data:")
    fmea_headers = [
        'ID', 
        'Name of Related Function', 
        'Name of Requirement', 
        'Potential Failure Mode', 
        'Effects of Failure', 
        'Severity', 
        'Cause of Failure', 
        'Occurance',
        'Design Controls', 
        'Detection', 
        'RPN', 
        'Recommended Actions'
    ]
    fmea_table = [fmea_headers] + st.session_state.fmea_data
    st.table(fmea_table)

