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

# Convert 'roam_unlimited_usd' to numeric for sorting
df["roam_unlimited_usd"] = df["roam_unlimited_usd"].astype(float)
df["roam_unlimited"] = df["roam_unlimited"].astype(float)

# Rename columns to be more readable
df.columns = [
    "Country",
    "Region",
    "Currency",
    "Roam Unlimited",
    "Roam Unlimited (USD)"
]

df["Roam Unlimited (USD)"] = df["Roam Unlimited (USD)"].round(2)

# Sort by USD column
df = df.sort_values(by="Roam Unlimited (USD)", ascending=True).reset_index(drop=True)

# Display date
st.markdown(f"**Last Updated:** {update_date}")

# Show the table
st.table(df)
