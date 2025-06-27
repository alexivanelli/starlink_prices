import streamlit as st
import pandas as pd
import json

# Wide layout
# st.set_page_config(layout="wide")

# Title
st.title("Starlink Roaming Prices")

# Read the JSON file
with open("prices.json", "r") as f:
    data = json.load(f)

# Extract date and DataFrame
update_date = data.get("date", "Unknown")
df = pd.DataFrame(data["data"])

df = df[df['plan'] == 'Roam - Unlimited'].reset_index(drop=True)

del df['plan']

# Rename columns to be more readable
df.columns = [
    "Country",
    "Region",
    "Currency",
    "Price",
    "Price (USD)"
]

df["Price (USD)"] = df["Price (USD)"].round(2)

# Sort by USD column
df = df.sort_values(by="Price (USD)", ascending=True).reset_index(drop=True)

# Display date
st.markdown(f"**Last Updated:** {update_date}")

# Show the table
st.dataframe(df, use_container_width=True, height=2000)
