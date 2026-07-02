import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
import os
# ==========================================================
# PAGE CONFIGURATION
# ==========================================================


st.set_page_config(
    page_title="Shopper Spectrum",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* Main App */
.main{
    background-color:#0E1117;
}

/* Padding */
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:#161B22;
}

/* KPI Cards */
div[data-testid="metric-container"]{
    background:#1B1F24;
    border:1px solid #2F3742;
    border-radius:16px;
    padding:18px;
    box-shadow:0px 3px 10px rgba(0,0,0,.25);
}

/* Buttons */
.stButton>button{
    width:100%;
    border-radius:12px;
    height:3em;
    font-weight:bold;
}

/* Charts */
.js-plotly-plot{
    border-radius:15px;
}

/* Hide Streamlit Footer */
footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    # Correct paths for your project
    sales_df = pd.read_csv("data/cleaned_online_retail.csv")
    rfm_df = pd.read_csv("data/rfm_customer_segments.csv")
    if os.path.exists("data/product_similarity_matrix.csv"):
        similarity_df = pd.read_csv("data/product_similarity_matrix.csv")
    else:
        similarity_df = None

    sales_df["InvoiceDate"] = pd.to_datetime(sales_df["InvoiceDate"])

    sales_df["TotalPrice"] = (
        sales_df["Quantity"] *
        sales_df["UnitPrice"]
    )

    sales_df["Month"] = (
        sales_df["InvoiceDate"]
        .dt.to_period("M")
        .astype(str)
    )

    sales_df["Year"] = sales_df["InvoiceDate"].dt.year

    return sales_df, rfm_df, similarity_df


sales_df, rfm_df, similarity_df = load_data()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🛒 Shopper Spectrum")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive Dashboard",
        "📈 Sales Analytics",
        "🌍 Country Analysis",
        "👥 RFM Analysis",
        "🎯 Customer Segmentation",
        "🤖 Product Recommendation",
        "💡 Business Insights"
    ]
)

st.sidebar.markdown("---")

st.sidebar.subheader("Dashboard Filters")

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(sales_df["Country"].unique().tolist())
)

year = st.sidebar.selectbox(
    "Year",
    ["All"] + sorted(sales_df["Year"].unique().tolist())
)

filtered_df = sales_df.copy()

if country != "All":
    filtered_df = filtered_df[
        filtered_df["Country"] == country
    ]

if year != "All":
    filtered_df = filtered_df[
        filtered_df["Year"] == year
    ]

st.sidebar.markdown("---")

st.sidebar.success("Business Analyst Portfolio Project")

# ==========================================================
# EXECUTIVE DASHBOARD
# ==========================================================

if page == "🏠 Executive Dashboard":

    st.title("🛒 Shopper Spectrum")
    st.caption("Executive Dashboard")

    # ------------------------------------------------------
    # KPI CALCULATIONS
    # ------------------------------------------------------

    total_revenue = filtered_df["TotalPrice"].sum()

    total_orders = filtered_df["InvoiceNo"].nunique()

    total_customers = filtered_df["CustomerID"].nunique()

    total_products = filtered_df["Description"].nunique()

    avg_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "💰 Revenue",
        f"₹ {total_revenue:,.0f}"
    )

    c2.metric(
        "📦 Orders",
        f"{total_orders:,}"
    )

    c3.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )

    c4.metric(
        "🛍 Products",
        f"{total_products:,}"
    )

    c5.metric(
        "💵 Avg Order",
        f"₹ {avg_order_value:,.0f}"
    )

    st.markdown("---")

    # ------------------------------------------------------
    # MONTHLY REVENUE
    # ------------------------------------------------------

    monthly_sales = (
        filtered_df
        .groupby("Month", as_index=False)["TotalPrice"]
        .sum()
    )

    fig = px.line(
        monthly_sales,
        x="Month",
        y="TotalPrice",
        title="Monthly Revenue Trend",
        markers=True,
        template="plotly_dark"
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------------
    # TOP CHARTS
    # ------------------------------------------------------

    left, right = st.columns(2)

    with left:

        top_products = (
            filtered_df
            .groupby("Description", as_index=False)["Quantity"]
            .sum()
            .sort_values(
                "Quantity",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_products,
            x="Quantity",
            y="Description",
            orientation="h",
            title="Top 10 Selling Products",
            color="Quantity",
            template="plotly_dark"
        )

        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        top_countries = (
            filtered_df
            .groupby("Country", as_index=False)["TotalPrice"]
            .sum()
            .sort_values(
                "TotalPrice",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_countries,
            x="Country",
            y="TotalPrice",
            color="TotalPrice",
            title="Top Countries by Revenue",
            template="plotly_dark"
        )

        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    # ------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ------------------------------------------------------

    st.subheader("📌 Executive Summary")

    st.info(f"""
**Total Revenue:** ₹ {total_revenue:,.0f}

**Orders Processed:** {total_orders:,}

**Unique Customers:** {total_customers:,}

**Products Sold:** {total_products:,}

**Average Order Value:** ₹ {avg_order_value:,.0f}
""")
    
# ==========================================================
# SALES ANALYTICS
# ==========================================================

elif page == "📈 Sales Analytics":

    st.title("📈 Sales Analytics")
    st.caption("Detailed Sales Performance Analysis")

    # ------------------------------------------------------
    # Create Date Features
    # ------------------------------------------------------

    analytics_df = filtered_df.copy()

    analytics_df["Weekday"] = analytics_df["InvoiceDate"].dt.day_name()

    analytics_df["Hour"] = analytics_df["InvoiceDate"].dt.hour

    # ------------------------------------------------------
    # Monthly Revenue
    # ------------------------------------------------------

    monthly_sales = (
        analytics_df
        .groupby("Month", as_index=False)["TotalPrice"]
        .sum()
    )

    fig = px.line(
        monthly_sales,
        x="Month",
        y="TotalPrice",
        markers=True,
        title="Monthly Revenue Trend",
        template="plotly_dark"
    )

    fig.update_layout(height=420)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Monthly Orders
    # ------------------------------------------------------

    monthly_orders = (
        analytics_df
        .groupby("Month")["InvoiceNo"]
        .nunique()
        .reset_index(name="Orders")
    )

    fig = px.bar(
        monthly_orders,
        x="Month",
        y="Orders",
        color="Orders",
        title="Monthly Orders",
        template="plotly_dark"
    )

    fig.update_layout(height=420)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Average Order Value
    # ------------------------------------------------------

    monthly_avg = (
        analytics_df
        .groupby("Month")
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique")
        )
        .reset_index()
    )

    monthly_avg["AverageOrder"] = (
        monthly_avg["Revenue"] /
        monthly_avg["Orders"]
    )

    fig = px.line(
        monthly_avg,
        x="Month",
        y="AverageOrder",
        markers=True,
        title="Average Order Value",
        template="plotly_dark"
    )

    fig.update_layout(height=420)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    left, right = st.columns(2)

    # ------------------------------------------------------
    # Weekday Sales
    # ------------------------------------------------------

    with left:

        weekday_sales = (
            analytics_df
            .groupby("Weekday")["TotalPrice"]
            .sum()
            .reindex([
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ])
            .reset_index()
        )

        fig = px.bar(
            weekday_sales,
            x="Weekday",
            y="TotalPrice",
            color="TotalPrice",
            title="Revenue by Weekday",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------------------
    # Hourly Sales
    # ------------------------------------------------------

    with right:

        hourly_sales = (
            analytics_df
            .groupby("Hour")["TotalPrice"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            hourly_sales,
            x="Hour",
            y="TotalPrice",
            markers=True,
            title="Revenue by Hour",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================================
# COUNTRY ANALYSIS
# ==========================================================

elif page == "🌍 Country Analysis":

    st.title("🌍 Country Analysis")
    st.caption("Country-wise Sales Performance")

    country_df = (
        filtered_df
        .groupby("Country")
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique")
        )
        .reset_index()
    )

    country_df["AverageOrderValue"] = (
        country_df["Revenue"] /
        country_df["Orders"]
    )

    # ------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🌍 Countries",
        country_df["Country"].nunique()
    )

    c2.metric(
        "💰 Total Revenue",
        f"₹ {country_df['Revenue'].sum():,.0f}"
    )

    c3.metric(
        "👥 Customers",
        country_df["Customers"].sum()
    )

    st.markdown("---")

    # ------------------------------------------------------
    # World Map
    # ------------------------------------------------------

    fig = px.choropleth(
        country_df,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        hover_name="Country",
        color_continuous_scale="Blues",
        title="Revenue by Country"
    )

    fig.update_layout(height=550)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------------
    # Two Charts
    # ------------------------------------------------------

    left, right = st.columns(2)

    with left:

        top_country = (
            country_df
            .sort_values(
                "Revenue",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_country,
            x="Revenue",
            y="Country",
            orientation="h",
            color="Revenue",
            title="Top 10 Countries by Revenue",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.bar(
            top_country,
            x="Country",
            y="Orders",
            color="Orders",
            title="Orders by Country",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    # ------------------------------------------------------
    # Average Order Value
    # ------------------------------------------------------

    fig = px.bar(
        top_country,
        x="Country",
        y="AverageOrderValue",
        color="AverageOrderValue",
        title="Average Order Value by Country",
        template="plotly_dark"
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# RFM ANALYSIS
# ==========================================================

elif page == "👥 RFM Analysis":

    st.title("👥 RFM Customer Analysis")
    st.caption("Customer Segmentation using RFM Model")

    # ------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------

    total_customers = rfm_df["CustomerID"].nunique()
    avg_recency = rfm_df["Recency"].mean()
    avg_frequency = rfm_df["Frequency"].mean()
    avg_monetary = rfm_df["Monetary"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Customers", f"{total_customers:,}")
    c2.metric("📅 Avg Recency", f"{avg_recency:.1f}")
    c3.metric("🛒 Avg Frequency", f"{avg_frequency:.1f}")
    c4.metric("💰 Avg Monetary", f"₹ {avg_monetary:,.0f}")

    st.markdown("---")

    # ------------------------------------------------------
    # Customer Segment Distribution
    # ------------------------------------------------------

    segment_counts = (
        rfm_df["CustomerSegment"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = ["CustomerSegment", "Customers"]

    fig = px.bar(
        segment_counts,
        x="CustomerSegment",
        y="Customers",
        color="Customers",
        title="Customer Segment Distribution",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Recency vs Monetary
    # ------------------------------------------------------

    fig = px.scatter(
        rfm_df,
        x="Recency",
        y="Monetary",
        color="CustomerSegment",
        hover_data=["CustomerID"],
        title="Recency vs Monetary",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Bubble Chart
    # ------------------------------------------------------

    fig = px.scatter(
        rfm_df,
        x="Frequency",
        y="Monetary",
        size="Monetary",
        color="CustomerSegment",
        hover_data=["CustomerID"],
        title="Frequency vs Monetary",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Box Plot
    # ------------------------------------------------------

    fig = px.box(
        rfm_df,
        x="CustomerSegment",
        y="Monetary",
        color="CustomerSegment",
        title="Monetary Distribution by Segment",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Segment Summary
    # ------------------------------------------------------

    st.subheader("📋 Segment Summary")

    segment_summary = (
        rfm_df
        .groupby("CustomerSegment")
        .agg(
            Customers=("CustomerID", "count"),
            AvgRecency=("Recency", "mean"),
            AvgFrequency=("Frequency", "mean"),
            AvgMonetary=("Monetary", "mean")
        )
        .round(2)
    )

    st.dataframe(
        segment_summary,
        use_container_width=True
    )

# ==========================================================
# CUSTOMER SEGMENTATION
# ==========================================================

elif page == "🎯 Customer Segmentation":

    st.title("🎯 Customer Segmentation")
    st.caption("Cluster-based Customer Analysis")

    # ------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------

    total_clusters = rfm_df["Cluster"].nunique()
    total_customers = rfm_df["CustomerID"].nunique()
    avg_frequency = rfm_df["Frequency"].mean()
    avg_monetary = rfm_df["Monetary"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📊 Clusters", total_clusters)
    c2.metric("👥 Customers", total_customers)
    c3.metric("🛒 Avg Frequency", f"{avg_frequency:.1f}")
    c4.metric("💰 Avg Monetary", f"₹ {avg_monetary:,.0f}")

    st.markdown("---")

    # ------------------------------------------------------
    # Cluster Distribution
    # ------------------------------------------------------

    cluster_counts = (
        rfm_df["Cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_counts.columns = ["Cluster", "Customers"]

    fig = px.pie(
        cluster_counts,
        names="Cluster",
        values="Customers",
        hole=0.45,
        title="Customer Distribution by Cluster"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Frequency vs Monetary
    # ------------------------------------------------------

    fig = px.scatter(
        rfm_df,
        x="Frequency",
        y="Monetary",
        color="Cluster",
        size="Monetary",
        hover_data=["CustomerID"],
        title="Frequency vs Monetary by Cluster",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Cluster Revenue
    # ------------------------------------------------------

    cluster_summary = (
        rfm_df
        .groupby("Cluster")
        .agg(
            Customers=("CustomerID","count"),
            AvgRecency=("Recency","mean"),
            AvgFrequency=("Frequency","mean"),
            AvgMonetary=("Monetary","mean")
        )
        .reset_index()
    )

    fig = px.bar(
        cluster_summary,
        x="Cluster",
        y="AvgMonetary",
        color="AvgMonetary",
        title="Average Monetary Value by Cluster",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Cluster Comparison
    # ------------------------------------------------------

    fig = px.bar(
        cluster_summary,
        x="Cluster",
        y="AvgFrequency",
        color="AvgFrequency",
        title="Average Purchase Frequency",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------
    # Cluster Summary Table
    # ------------------------------------------------------

    st.subheader("📋 Cluster Summary")

    st.dataframe(
        cluster_summary.round(2),
        use_container_width=True
    )

# ==========================================================
# PRODUCT RECOMMENDATION ENGINE
# ==========================================================

if page == "🤖 Product Recommendation":
    

    st.title("🤖 Product Recommendation")
    st.write("Page Loaded Successfully")

    # Product names
    product_list = similarity_df.columns.tolist()

    selected_product = st.selectbox(
        "Choose a Product",
        product_list
    )

    if st.button("Recommend Products"):

        # Get column position
        product_index = similarity_df.columns.get_loc(selected_product)

        # Get similarity values from that row
        similarity_scores = similarity_df.iloc[product_index]

        recommendations = pd.DataFrame({
            "Recommended Product": similarity_df.columns,
            "Similarity Score": similarity_scores.values
        })

        # Remove selected product
        recommendations["Similarity Score"] = pd.to_numeric(
        recommendations["Similarity Score"],
        errors="coerce"
)
        # Top 5 recommendations
        recommendations = (
            recommendations
            .sort_values(
                "Similarity Score",
                ascending=False
            )
            .head(5)
        )

        st.success("Top 5 Recommended Products")

        st.dataframe(
            recommendations,
            use_container_width=True
        )

        fig = px.bar(
            recommendations,
            x="Similarity Score",
            y="Recommended Product",
            orientation="h",
            color="Similarity Score",
            title="Top Similar Products",
            template="plotly_dark"
        )

        fig.update_layout(height=450)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    st.info("""
### 💡 How it Works

This recommendation engine uses a **Cosine Similarity Matrix**.

For every selected product, it finds the products with the highest similarity score.

### Business Applications

- Cross Selling
- Product Bundling
- Personalized Recommendations
- Improve Customer Experience
""")
    
# ==========================================================
# BUSINESS INSIGHTS
# ==========================================================

elif page == "💡 Business Insights":

    st.title("💡 Business Insights")
    st.caption("Executive Summary & Business Recommendations")

    # ------------------------------------------------------
    # Calculate Insights
    # ------------------------------------------------------

    total_revenue = filtered_df["TotalPrice"].sum()

    top_country = (
        filtered_df.groupby("Country")["TotalPrice"]
        .sum()
        .idxmax()
    )

    top_product = (
        filtered_df.groupby("Description")["Quantity"]
        .sum()
        .idxmax()
    )

    top_customer_segment = (
        rfm_df["CustomerSegment"]
        .value_counts()
        .idxmax()
    )

    repeat_customers = (
        (rfm_df["Frequency"] > 1).sum()
    )

    customer_retention = (
        repeat_customers /
        len(rfm_df)
    ) * 100

    # ------------------------------------------------------
    # KPI Cards
    # ------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "💰 Total Revenue",
            f"₹ {total_revenue:,.0f}"
        )

    with c2:
        st.metric(
            "🔁 Repeat Customer Rate",
            f"{customer_retention:.1f}%"
        )

    st.markdown("---")

    # ------------------------------------------------------
    # Key Findings
    # ------------------------------------------------------

    st.subheader("📌 Key Business Findings")

    st.success(f"""
### 1️⃣ Revenue

The business generated **₹ {total_revenue:,.0f}** in total sales.

---

### 2️⃣ Best Performing Country

**{top_country}** generated the highest revenue.

---

### 3️⃣ Best Selling Product

**{top_product}** sold the highest quantity.

---

### 4️⃣ Largest Customer Segment

**{top_customer_segment}** represents the largest customer group.

---

### 5️⃣ Customer Retention

Approximately **{customer_retention:.1f}%** of customers made repeat purchases.
""")

    st.markdown("---")

    # ------------------------------------------------------
    # Business Recommendations
    # ------------------------------------------------------

    st.subheader("🚀 Business Recommendations")

    st.info("""
### Recommendation 1
Increase marketing spend in the highest-performing countries to maximize revenue.

---

### Recommendation 2
Create bundle offers using the best-selling products.

---

### Recommendation 3
Develop loyalty programs to convert Regular Customers into High-Value Customers.

---

### Recommendation 4
Target At-Risk Customers with personalized discounts and email campaigns.

---

### Recommendation 5
Use the Product Recommendation Engine to improve cross-selling opportunities.
""")

    st.markdown("---")

    # ------------------------------------------------------
    # Project Summary
    # ------------------------------------------------------

    st.subheader("📋 Project Summary")

    st.write("""
This dashboard provides an end-to-end Retail Business Intelligence solution including:

- Executive Dashboard
- Sales Analytics
- Country Analysis
- RFM Customer Segmentation
- Customer Cluster Analysis
- Product Recommendation Engine
- Business Insights & Recommendations

The project demonstrates practical Business Analyst skills in Python, Pandas, Plotly, Streamlit, Data Visualization, Customer Analytics, and Recommendation Systems.
""")