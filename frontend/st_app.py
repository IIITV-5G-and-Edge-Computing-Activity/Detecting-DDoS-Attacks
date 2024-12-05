import streamlit as st
import requests
import json
import re

# backend URL 
backend_url = "http://localhost:5000"  

# Function to validate IP address format
def validate_ip(ip):
    # Regular expression to match a valid IPv4 address (four octets between 0-255)
    pattern = r"^([0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(pattern, ip):
        # Check if each octet is in the range 0-255
        octets = ip.split(".")
        for octet in octets:
            if int(octet) < 0 or int(octet) > 255:
                return False
        return True
    return False

# Function to upload the file and train the models
def upload_file():
    st.subheader("Step 1: Upload Your CSV File")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        with st.spinner("Training models, please wait..."):
            files = {"file": uploaded_file}
            response = requests.post(f"{backend_url}/upload", files=files)
            if response.status_code == 200:
                st.success("Models trained and saved successfully!")
            else:
                st.error(f"Error: {response.json().get('error')}")

# Function to make predictions with custom inputs
def predict_with_custom_input():
    st.subheader("Step 2: Enter Custom Data for Prediction")

    # Input fields for custom data
    src_ip = st.text_input("Source IP Address (e.g., 192.168.1.25)", "192.168.1.25")
    dst_ip = st.text_input("Destination IP Address (e.g., 192.168.1.120)", "192.168.1.120")
    protocol = st.selectbox("Protocol", ["TCP", "UDP", "ICMP"])

    # Model selection dropdown
    model_name = st.selectbox("Select Model for Prediction", ["random_forest", "knn", "naive_bayes"])

    # Validate IP addresses
    if not validate_ip(src_ip):
        st.error("Invalid Source IP Address format. Please enter a valid IP (e.g., 192.168.1.25).")
        return

    if not validate_ip(dst_ip):
        st.error("Invalid Destination IP Address format. Please enter a valid IP (e.g., 192.168.1.120).")
        return

    # Collect data for prediction
    prediction_data = [{
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": protocol
    }]

    # Show the input data for prediction
    st.write("Input Data for Prediction:")
    st.json(prediction_data)

    # Submit button for prediction
    if st.button("Get Prediction"):
        with st.spinner("Getting prediction..."):
            response = requests.post(
                f"{backend_url}/predict", 
                data=json.dumps(prediction_data),
                headers={"Content-Type": "application/json"},
                params={"model": model_name}
            )
            
            if response.status_code == 200:
                predictions = response.json().get("predictions")
                result = "DDoS Attack Detected" if predictions[0] == 1 else "No DDoS Attack"
                st.success(f"Prediction Result: {result}")
            else:
                st.error(f"Error: {response.json().get('error')}")

# Streamlit app layout
st.title("DDoS Prediction System")
st.sidebar.header("Upload Data and Make Predictions")

# Add interactivity through sidebar buttons
sidebar_buttons = st.sidebar.selectbox("Choose an Action", ["Upload and Train Model", "Make Prediction"])

if sidebar_buttons == "Upload and Train Model":
    upload_file()

elif sidebar_buttons == "Make Prediction":
    predict_with_custom_input()
