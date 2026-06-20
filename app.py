#1: Code-Along Start - Basic Streamlit App
#-------------------------------------------------------------------
# import streamlit as st

# # st.title() displays a large heading. st.write() is a general-purpose 
# # function that can display text, dataframes, charts, and more. 
# # We'll explore more display and input components next.
# st.title("Hello, Streamlit!")
# st.write("This is my first Streamlit app.")

# --------------------------------------------------------

#2: Code-Along Start - Display Components
#This is a full code-along lesson. Everyone builds one usable dashboard 
#together using ./data/resale_data.csv.

import streamlit as st

# Sets the page configuration
# You can set the page title and layout here
st.set_page_config(page_title="HDB Resale Dashboard", layout="wide")

st.title("Singapore HDB Resale Dashboard")
st.caption("Code-along: building a usable dashboard from real resale transactions.")

st.header("Dashboard Overview")
st.subheader("What this app will show")
st.markdown("""
- Transaction volume after filtering
- Average resale price
- Median floor area
- Town and flat type trends
""")


# --------------------------------------------------------------------

#3: Load Real Data and show First Output, We now connect the page to the actual data file: ./data/resale_data.csv.
import streamlit as st
import pandas as pd

DATA_PATH = "./data/resale_data.csv"

df = pd.read_csv(DATA_PATH)
# Lesson assumption:
# this dataset has already gone through EDA and basic cleaning.
# Here we focus on dashboard building, not data cleaning.
# We still set the datetime dtype explicitly for reliable filtering and charting.
df["month"] = pd.to_datetime(df["month"])

st.write(f"Rows loaded: {len(df):,} | Columns: {len(df.columns)}")
st.dataframe(df.head(20), width="stretch")

#---------------------------------------------------------------------

# # 4: Add Sidebar Filters and KPIs. Streamlit has a built-in sidebar for inputs. 
# Anything inside st.sidebar appears there. Typically, filters go in the sidebar.

# st.sidebar.header("Filters") - Can delete. 

# 4.1. Get unique values for towns and flat types: We use dropna() to ensure that any missing values are excluded from the unique lists. 
# The sorted() function is used to sort the unique values alphabetically for better user 
# experience in the multi-select widgets.
unique_towns = sorted(df["town"].dropna().unique())
unique_flat_types = sorted(df["flat_type"].dropna().unique())


#4.2. Create multi-selects for towns and flat types
selected_towns = st.sidebar.multiselect("Town", unique_towns, default=[])
selected_flat_types = st.sidebar.multiselect("Flat Type", unique_flat_types, default=[])

# 4.3. Create slider for resale price range. First we get the min and max resale prices from the DataFrame:

min_price = int(df["resale_price"].min())
max_price = int(df["resale_price"].max())

# Then we create the slider widget in the sidebar:
price_range = st.sidebar.slider(
    "Resale Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000,
)

# 4.4. Create date input for month range. First, get the minimum and maximum dates from the "month" column:
date_min = df["month"].min().date()
date_max = df["month"].max().date()

# Then create the date input widget in the sidebar:
date_range = st.sidebar.date_input("Month Range", value=(date_min, date_max))


# 4.4.2 Apply filters. To handle filtering based on the selected sidebar inputs, 
# we will create a new DataFrame called filtered_df that starts as a copy of the original 
# DataFrame df. We will then apply each filter conditionally based on whether the user has made any selections.

filtered_df = df.copy()

if selected_towns:
    filtered_df = filtered_df[filtered_df["town"].isin(selected_towns)]

if selected_flat_types:
    filtered_df = filtered_df[filtered_df["flat_type"].isin(selected_flat_types)]

filtered_df = filtered_df[
    filtered_df["resale_price"].between(price_range[0], price_range[1])
]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[filtered_df["month"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date)
    )]
    
# 4.4.3 Update the table to use filtered_df. Now update the table code from Section 3.2 
# so it uses the filtered DataFrame. Important: move this table block to a position 
# after filtered_df is created in Section 4.2. If you place it earlier, filtered_df is not defined yet and the app will error.
 
st.header("Filtered Results")
st.write(f"Matching rows: {len(filtered_df):,} | Columns: {len(filtered_df.columns)}")
st.dataframe(filtered_df.head(20), width="stretch")

# 4.4.4 KPI row
# The KPI row shows key metrics at a glance. We will use st.metric inside st.columns 
# to create a row of four metrics: total transactions, average price, median price, and median floor area.

st.header("Key Metrics")
# # Create four columns for the metrics and unpack them
# # We can then use each column to place a metric
col1, col2, col3, col4 = st.columns(4)

# Each col provides a .metric() method that takes a label and a value
col1.metric("Transactions", f"{len(filtered_df):,}")
col2.metric("Average Price", f"${filtered_df['resale_price'].mean():,.0f}")
col3.metric("Median Price", f"${filtered_df['resale_price'].median():,.0f}")
col4.metric("Median Floor Area", f"{filtered_df['floor_area_sqm'].median():.1f} sqm")

#----------------------------------------------------------------------------


# Section 5: Add Charts and Data Views. We will add three main visualizations to analyze trends in the filtered data here:
# Average resale price by town (bar chart)
# Transactions by flat type (bar chart)
# Monthly median resale price trend (line chart)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", f"{len(filtered_df):,}")
col2.metric("Average Price", f"${filtered_df['resale_price'].mean():,.0f}")

import plotly.express as px
st.header("Visual Analysis")
col_left, col_right = st.columns(2)

# Tells Streamlit to put the following content in the left column
with col_left:
    st.subheader("Average Resale Price by Town")
    avg_price_by_town = (
        filtered_df.groupby("town", as_index=False)["resale_price"]
        .mean()
        .sort_values("resale_price", ascending=False)
        .head(10) # Top 10 towns only for clarity
    )
    # Create a Plotly bar chart with towns on x-axis and average resale price on y-axis
    fig_town = px.bar(avg_price_by_town, x="town", y="resale_price")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_town, width="stretch")

# Tells Streamlit to put the following content in the right column
with col_right:
    st.subheader("Transactions by Flat Type")
    tx_by_flat = (
        filtered_df.groupby("flat_type", as_index=False)
        .size()
        .rename(columns={"size": "transactions"})
        .sort_values("transactions", ascending=False)
    )
    # Create a Plotly bar chart with flat types on x-axis and transaction counts on y-axis
    fig_flat = px.bar(tx_by_flat, x="flat_type", y="transactions")
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig_flat, width="stretch")
    
#-----------------------------------------------------------------------------
     
# #5.1 Monthly trend. For Monthly Median Resale Price trend, we will create a line chart showing 
# how the median resale price changes over time.

st.subheader("Monthly Median Resale Price")
trend = (
    filtered_df.groupby("month", as_index=False)["resale_price"]
    .median()
    .sort_values("month")
)
# Create a Plotly line chart with month on x-axis and median resale price on y-axis
fig_trend = px.line(trend, x="month", y="resale_price", markers=True)
# Display the Plotly chart in Streamlit
st.plotly_chart(fig_trend, width="stretch")    

# #5.3  Optional: Detailed table + download
# This is an optional section for users who want to inspect more rows and export the filtered 
# results. Unlike the main table in Section 4.3 (always visible for quick feedback), 
# this one is collapsed in an expander to keep the dashboard clean. There is also a download button to export the filtered data as CSV.

with st.expander("View Filtered Transactions"):
    st.dataframe(filtered_df, width="stretch", height=350)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv,
        file_name="filtered_resale_data.csv",
        mime="text/csv",
    )
    
    
# #6: The Rerun Model in Streamlit. In this section, you will observe Streamlit's rerun behavior using your current dashboard. 
# A rerun means the entire script executes again from top to bottom. This is a core concept in Streamlit 
# that affects how you structure your code and manage state.

from datetime import datetime
print(f"🟢 Rerun at: {datetime.now()}")

# Change any sidebar filter and see that the script reruns top-to-bottom.
# Rerun triggers by:Changing widget values (multiselect, slider, date_input, button)

# Because this app reads a large CSV, without caching the file is re-read each rerun. Now refactor to a cached loader:
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data(DATA_PATH)

# Read Lessom.md for deployment
# 8.2 Preparing for Deployment
# Streamlit Community Cloud supports both environment.yml and requirements.txt, but requirements.txt is strongly recommended for deployment because the free tier has a 1GB memory limit, and conda's environment resolution often runs out of memory and fails to deploy.

# Because this app reads a local CSV (./data/resale_data.csv), that file must also be pushed to GitHub.
# If the data file is missing from the repo, deployment succeeds but the app will fail at runtime when it tries to read the file.