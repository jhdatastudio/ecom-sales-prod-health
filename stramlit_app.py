import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Demo 02: Ecom Health Check", layout="wide")
st.title("🛒 E-Commerce Sales & Product Health Check")

# Load data with cache
@st.cache_data
def load_data():
    df = pd.read_csv("data/online_retail_II.csv", encoding='ISO-8859-1')
    df['Total'] = df['Quantity'] * df['Price']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    return df

df = load_data()

# Prepare cleaned data
@st.cache_data
def clean_data(df):
    df_clean = df[df['Quantity'] > 0].copy()
    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean.dropna()
    df_clean['VolatilePricing'] = df_clean.groupby('Description')['Price'].transform('nunique') > 3
    df_clean['Description'] = df_clean['Description'].str.strip().str.title()
    return df_clean

df_clean = clean_data(df)

# Tabs
with st.sidebar:
    tab = st.radio("Jump to Section:", [
        "Summary Dashboard", "Refund Analysis", "Top Products", "Price Volatility", "Revenue Trends"
    ])

# 1. Summary Dashboard
if tab == "Summary Dashboard":
    st.subheader("📊 Key Metrics Summary")
    refunds = df[df['Quantity'] < 0]
    summary = pd.DataFrame({
        "Metric": [
            "Total Records", "Unique Customers", "Refund Volume (€)", "Refund Rate (%)", "Volatile Price Products (3+ prices)"
        ],
        "Value": [
            f"{len(df):,}",
            f"{df['Customer ID'].nunique():,}",
            f"€{refunds['Total'].sum():,.2f}",
            round(len(refunds) / len(df) * 100, 2),
            df.groupby('Description')['Price'].nunique().gt(3).sum()
        ]
    })
    st.dataframe(summary, use_container_width=True)

    st.subheader("🧼 Data Cleaning Summary")
    initial_rows = len(df)
    refund_rows = (df['Quantity'] < 0).sum()
    duplicate_rows = df.duplicated().sum()
    null_rows = df.isnull().any(axis=1).sum()
    cleaned_rows = len(df_clean)

    st.markdown(f"""
    - **Original Rows**: {initial_rows:,}  
    - **Refund Rows Removed** (`Quantity < 0`): {refund_rows:,}  
    - **Duplicate Rows Removed**: {duplicate_rows:,}  
    - **Rows with Missing Values**: {null_rows:,}  
    - **Rows After Cleaning**: **{cleaned_rows:,}**
    """)

# 2. Refund Analysis
elif tab == "Refund Analysis":
    st.subheader("🔁 Refund-Prone Products")
    refunds = df[df['Quantity'] < 0]
    refund_counts = refunds.groupby('Description')['Quantity'].count().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    refund_counts.plot(kind='barh', ax=ax, title="Top Refund-Prone Products")
    ax.set_xlabel("Refund Records")
    st.pyplot(fig)

# 3. Top Products
elif tab == "Top Products":
    st.subheader("🏆 Top Products by Revenue")
    top_products = df.groupby('Description')['Total'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    top_products.plot(kind='barh', ax=ax, title='Top Products by Revenue (€)')
    ax.set_xlabel("€ Revenue")
    st.pyplot(fig)

# 4. Price Volatility
elif tab == "Price Volatility":
    st.subheader("📈 Price Volatility")
    price_variation = df.groupby('Description')['Price'].nunique()
    volatile = price_variation[price_variation > 3].sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    volatile.plot(kind='bar', ax=ax, title='Products with High Price Variation')
    ax.set_ylabel("Unique Price Points")
    st.pyplot(fig)
    st.dataframe(volatile.reset_index().rename(columns={"Price": "Unique Prices"}))

# 5. Revenue Trends
elif tab == "Revenue Trends":
    st.subheader("📆 Monthly Revenue Trend")
    monthly_sales = df.groupby('YearMonth')['Total'].sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    monthly_sales.plot(kind='bar', ax=ax, title='Monthly Revenue (€)')
    ax.set_ylabel("€ Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.markdown("**Insight:** Strong seasonal peaks in November suggest importance of campaign timing.")
