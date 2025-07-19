

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
# 5. Sidebar Filters (Hierarchical)
# -----------------------------
st.sidebar.title("🔍 Filter Options")

# Step 1: Select Route
route_options = [""] + sorted(df['Bus_Route_Name'].dropna().unique().tolist())
selected_route = st.sidebar.selectbox("Select Bus Route", route_options, index=0)

if selected_route:
    filtered_route_df = df[df['Bus_Route_Name'] == selected_route]

    # Step 2: Select Bus Type
    bus_type_options = [""] + sorted(filtered_route_df['Bus_Type'].dropna().unique().tolist())
    selected_bus_type = st.sidebar.selectbox("Select Bus Type", bus_type_options, index=0)

    if selected_bus_type:
        filtered_type_df = filtered_route_df[filtered_route_df['Bus_Type'] == selected_bus_type]

        # Step 3: Select Bus Name
        bus_name_options = [""] + sorted(filtered_type_df['Bus_Name'].dropna().unique().tolist())
        selected_bus_name = st.sidebar.selectbox("Select Bus Name", bus_name_options, index=0)

        # Step 4: Star Rating filter
        min_rating = float(df['Star_Rating'].min())
        max_rating = float(df['Star_Rating'].max())
        rating_range = st.sidebar.slider("Star Rating", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))

        # Step 5: Price filter
        min_price = float(df['Price'].min())
        max_price = float(df['Price'].max())
        price_range = st.sidebar.slider("Price Range (₹)", min_value=min_price, max_value=max_price, value=(min_price, max_price))

        # -----------------------------
        # 6. Apply Filters
        # -----------------------------
        final_df = filtered_type_df[
            (filtered_type_df['Bus_Name'] == selected_bus_name) &
            (filtered_type_df['Star_Rating'].between(rating_range[0], rating_range[1])) &
            (filtered_type_df['Price'].between(price_range[0], price_range[1]))
        ] if selected_bus_name else pd.DataFrame()

        # Format Price column back to ₹
        if not final_df.empty:
            final_df['Price'] = final_df['Price'].apply(lambda x: f"₹ {int(x):,}")

        # -----------------------------
        # 7. Display Filtered Data
        # -----------------------------
        st.title("🚌 Redbus - Available Buses")
        st.markdown(f"Total Results: **{len(final_df)}**")

        if not final_df.empty:
            st.markdown(final_df.to_html(index=False, escape=False), unsafe_allow_html=True)
        else:
            st.warning("No matching buses found with the selected filters.")

    else:
        st.info("Please select a Bus Type.")
else:
    st.info("Please select a Bus Route.")

# -----------------------------
# 8. Bottom Scrolling Footer (Right to Left)
# -----------------------------
st.markdown("""
<br>
<div class="marquee-container">
    <div class="marquee-text">📞 For any help contact toll free: 88888 00008 | Thank you for choosing RedBus! ❤️🚌</div>
</div>
""", unsafe_allow_html=True)

