import streamlit as st
import pandas as pd
import json

# Wide layout
st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    with open("prices.json", "r") as f:
        raw = json.load(f)
    df = pd.DataFrame(raw["data"])
    date = raw.get("date", "Unknown")
    return df, date


df, update_date = load_data()

# Title
st.title("📡 Starlink Prices Explorer")
st.markdown("""
### 🌐 Starlink Price Comparison

Compare **Starlink subscription prices** across different countries.

- 💵 **All prices are shown in USD**
- ⚠️ _This site is **not affiliated with Starlink**_
- 🔄 Data is **updated daily**
""")
st.markdown(f"🗓️ Last updated: **{update_date}**")

# Load data



# Plan grouping logic
def get_plan_group(plan_name):
    name = plan_name.lower()
    if 'roam' in name:
        return "🌍 Roam"
    elif 'residential' in name:
        return "🏠 Residential"
    elif 'priority' in name:
        return "🚀 Priority"
    return "❓ Other"


# Add group columns
df['plan_category'] = df['plan'].map(lambda x: x.split('-')[0].strip())
df['plan_group'] = df['plan_category'].map(get_plan_group)

# Visual category buttons
visual_groups = ["🌍 Roam", "🏠 Residential", "🚀 Priority"]

if "selected_group" not in st.session_state:
    st.session_state.selected_group = visual_groups[0]

st.subheader("Choose a Plan Category")

cols = st.columns(len(visual_groups))
for i, group in enumerate(visual_groups):
    if cols[i].button(group, use_container_width=True):
        st.session_state.selected_group = group

group = st.session_state.selected_group
st.markdown(f"### Showing plans for: {group}")


# Display logic
if group == "🚀 Priority":
    plan_categories = df.loc[df['plan_group'] == group, 'plan_category'].unique()
    selected_plan_category = st.radio("Select a specific plan category", sorted(plan_categories), key="priority_radio")
    df_to_show = df[df['plan_category'] == selected_plan_category][['region', 'country', 'plan', 'price_usd']]
    df_to_show = df_to_show.sort_values(by='price_usd', ascending=True)
    df_to_show = df_to_show.set_index('region')
    price_columns = ['price_usd']

else:
    filtered_df = df[df['plan_group'] == group]
    df_to_show = pd.pivot_table(
        filtered_df,
        values='price_usd',
        index=['country', 'region'],
        columns=['plan'],
        aggfunc='first'
    ).reset_index()

    price_columns = [c for c in df_to_show.columns if c not in ['country', 'region']]
    price_columns_sorted = sorted(price_columns, key=lambda col: df_to_show[col].notna().sum(), reverse=True)
    df_to_show = df_to_show[['region', 'country'] + price_columns_sorted]

    if group == "🏠 Residential":
        df_to_show = df_to_show.sort_values(by='Residential', ascending=True)
    if group == "🌍 Roam":
        df_to_show = df_to_show.sort_values(by='Roam - Unlimited', ascending=True)

    df_to_show = df_to_show.set_index('region')

# Display table
st.dataframe(df_to_show,
             column_config={
                 p: st.column_config.NumberColumn(p, format='$%.2f') for p in price_columns
             },
             use_container_width=True, height=3000)
