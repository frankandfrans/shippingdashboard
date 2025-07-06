import pandas as pd
import requests
import xml.etree.ElementTree as ET
import streamlit as st
import matplotlib.pyplot as plt

# Set your USPS Web Tools User ID here
USPS_USER_ID = "52148930"

# USPS Tracking API request function
def get_usps_status(tracking_number):
    url = "https://secure.shippingapis.com/ShippingAPI.dll"
    api = "TrackV2"
    xml = f"""<TrackRequest USERID="{USPS_USER_ID}"><TrackID ID="{tracking_number}"></TrackID></TrackRequest>"""
    params = {"API": api, "XML": xml}

    try:
        response = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(response.content)
        status = root.find('.//TrackSummary').text

        if "Delivered" in status:
            return "Delivered"
        elif "Exception" in status or "Failure" in status:
            return "Exception"
        else:
            return "In Progress"
    except Exception as e:
        return "Error"

# Streamlit Web App
st.title("📦 USPS Shipping Dashboard")

uploaded_file = st.file_uploader("Upload your shipment CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    tracking_numbers = df['TRACKING NO']

    st.write("Fetching delivery statuses, please wait...")

    statuses = []
    for tn in tracking_numbers:
        status = get_usps_status(tn)
        statuses.append(status)

    df['DELIVERY STATUS'] = statuses

    status_colors = {"Delivered": "green", "In Progress": "yellow", "Exception": "red", "Error": "gray"}
    df['STATUS COLOR'] = df['DELIVERY STATUS'].map(status_colors)

    st.success("Statuses fetched successfully!")

    # Display data
    st.dataframe(df[['ORDER ID', 'TRACKING NO', 'SHIPPING FULL NAME', 'DELIVERY STATUS']])

    # Chart visualization
    status_counts = df['DELIVERY STATUS'].value_counts()
    fig, ax = plt.subplots()
    ax.bar(status_counts.index, status_counts.values, color=[status_colors[status] for status in status_counts.index])
    ax.set_title('Shipment Status Overview')
    ax.set_ylabel('Number of Shipments')
    st.pyplot(fig)

    # Option to download the results
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Dashboard CSV", data=csv, file_name='shipping_dashboard.csv', mime='text/csv')
