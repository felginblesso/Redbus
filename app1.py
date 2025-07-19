

# Import necessary libraries
import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine

# -----------------------------
# 1. Setup Database Connection
# -----------------------------
host = "localhost"
user = "root"
password = "password"
database = "redbus_db"

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# -----------------------------
# 2. Load Data
# -----------------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM redbus_data"
    df = pd.read_sql(query, engine)
    return df

df = load_data()

# Convert Price to float
df['Price'] = df['Price'].str.replace('₹', '', regex=False).str.replace(',', '', regex=False).astype(float)

# -----------------------------
# 3. Page Styling (Background, Marquee)
# -----------------------------
st.markdown("""
    <style>
    /* Background image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1526932849424-e0bbf1709d8b");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Scrolling marquee container */
    .marquee-container {
        width: 100%;
        overflow: hidden;
        background-color: #d60000;
        border-radius: 8px;
        box-shadow: 2px 2px 10px gray;
    }

    /* Actual scrolling text */
    .marquee-text {
        display: inline-block;
        white-space: nowrap;
        padding: 10px 0;
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        animation: scroll-left 15s linear infinite;
    }

    @keyframes scroll-left {
        0% {
            transform: translateX(100%);
        }
        100% {
            transform: translateX(-100%);
        }
    }

    /* Stylish Table */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background-color: #f44336;
        color: white;
        padding: 10px;
    }
    td {
        padding: 8px;
        background-color: #fff5f5;
    }
    tr:nth-child(even) {
        background-color: #ffe6e6;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 4. Top Scrolling Message (Right to Left)
# -----------------------------
st.markdown("""
<div class="marquee-container">
    <div class="marquee-text">🚍 Welcome to RedBus! Have a great journey! 😊🚌</div>
</div><br>
""", unsafe_allow_html=True)


# -----------------------------
# 3. Sidebar Filters
# -----------------------------
df_all = pd.read_sql("SELECT DISTINCT Bus_Route_Name, Bus_Type, Bus_Name FROM redbus_data", engine)

st.sidebar.title("🔍 Filter Options")

# Route filter
route_options = [""] + sorted(df_all['Bus_Route_Name'].dropna().unique().tolist())
selected_route = st.sidebar.selectbox("Select Bus Route", route_options, index=0)

# Bus Type filter
bus_type_options = [""]
if selected_route:
    bus_type_options += sorted(df_all[df_all['Bus_Route_Name'] == selected_route]['Bus_Type'].dropna().unique().tolist())
selected_bus_type = st.sidebar.selectbox("Select Bus Type", bus_type_options, index=0)

# Bus Name filter
bus_name_options = [""]
if selected_bus_type:
    bus_name_options += sorted(df_all[(df_all['Bus_Route_Name'] == selected_route) & (df_all['Bus_Type'] == selected_bus_type)]['Bus_Name'].dropna().unique().tolist())
selected_bus_name = st.sidebar.selectbox("Select Bus Name", bus_name_options, index=0)

# Star Rating range (query full range)
stars_range_df = pd.read_sql("SELECT MIN(Star_Rating) as min_r, MAX(Star_Rating) as max_r FROM redbus_data", engine)
min_rating = float(stars_range_df['min_r'][0])
max_rating = float(stars_range_df['max_r'][0])
rating_range = st.sidebar.slider("Star Rating", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))

# Price range (query full range)
price_range_df = pd.read_sql("SELECT MIN(REPLACE(REPLACE(Price, '₹', ''), ',', '') + 0) as min_p, MAX(REPLACE(REPLACE(Price, '₹', ''), ',', '') + 0) as max_p FROM redbus_data", engine)
min_price = float(price_range_df['min_p'][0])
max_price = float(price_range_df['max_p'][0])
price_range = st.sidebar.slider("Price Range (₹)", min_value=min_price, max_value=max_price, value=(min_price, max_price))

# -----------------------------
# 4. Build and Run SQL Query with Filters
# -----------------------------
query = "SELECT * FROM redbus_data WHERE 1=1"
params = ()

if selected_route:
    query += " AND Bus_Route_Name = %s"
    params += (selected_route,)
if selected_bus_type:
    query += " AND Bus_Type = %s"
    params += (selected_bus_type,)
if selected_bus_name:
    query += " AND Bus_Name = %s"
    params += (selected_bus_name,)
query += " AND Star_Rating BETWEEN %s AND %s"
params += (rating_range[0], rating_range[1])
query += " AND REPLACE(REPLACE(Price, '₹', ''), ',', '') + 0 BETWEEN %s AND %s"
params += (price_range[0], price_range[1])

final_df = pd.DataFrame()

# Only run the query if at least one filter is selected (not empty/default)
if selected_route or selected_bus_type or selected_bus_name or rating_range != (min_rating, max_rating) or price_range != (min_price, max_price):
    with engine.connect() as conn:
        final_df = pd.read_sql(query, conn, params=params)

# -----------------------------
# 5. Format and Display Data
# -----------------------------
if not final_df.empty:
    final_df['Price'] = final_df['Price'].apply(lambda x: f"₹ {int(str(x).replace('₹','').replace(',','')):,}")

st.title("🚌 Redbus - Available Buses")

if not final_df.empty:
    st.markdown(f"Total Results: **{len(final_df)}**")
    st.markdown(final_df.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.warning("Please apply filters to see available buses.")

# -----------------------------
# 8. Bottom Scrolling Footer (Right to Left)
# -----------------------------
st.markdown("""
<br>
<div class="marquee-container">
    <div class="marquee-text">📞 For any help contact toll free: 88888 00008 | Thank you for choosing RedBus! ❤️🚌</div>
</div>
""", unsafe_allow_html=True)

