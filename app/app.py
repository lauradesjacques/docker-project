import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Database connection setup
def connect_to_db(server, database):
    connection_url = URL.create(
        "mssql+pyodbc",
        host=server,
        database=database,
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "trusted_connection": "yes"
        }
    )
    engine = create_engine(connection_url)
    return engine

# Query data from the database
def load_data(engine, table_name):
    query = f"SELECT * FROM {table_name}"
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

# Main Streamlit app
def main():
    st.title("E-Commerce Data Dashboard")
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Sales Analysis", "Inventory Analysis"]
    )

    # Connect to the database
    server = "LAPTOP-AAS7RBMP"
    database = "EcomerceDB"
    engine = connect_to_db(server, database)

    if page == "Overview":
        st.header("Overview")
        # Load data from database
        customers = load_data(engine, "CustomerDimension")
        products = load_data(engine, "ProductDimension")
        sales = load_data(engine, "SalesFact")

        st.write(f"📊 **Total Customers:** {len(customers)}")
        st.write(f"📦 **Total Products:** {len(products)}")
        st.write(f"💰 **Total Sales Transactions:** {len(sales)}")

    elif page == "Sales Analysis":
        st.header("Sales Analysis")
        sales = load_data(engine, "SalesFact")
        products = load_data(engine, "ProductDimension")
        dates = load_data(engine, "DateDimension")

        # Merge for richer insights
        sales = sales.merge(dates, left_on="DateID", right_on="DateID")
        sales = sales.merge(products, left_on="ProductID", right_on="ProductID")

        # Sales over time
        sales_over_time = sales.groupby("FullDate")["NetAmount"].sum().reset_index()
        fig = px.line(
            sales_over_time,
            x="FullDate",
            y="NetAmount",
            title="Sales Over Time",
            labels={"FullDate": "Date", "NetAmount": "Total Sales (€)"}
        )
        st.plotly_chart(fig)

        # Top 10 Products by Sales
        top_products = sales.groupby("ProductName")["NetAmount"].sum().nlargest(10).reset_index()
        fig = px.bar(
            top_products,
            x="ProductName",
            y="NetAmount",
            title="Top 10 Products by Sales",
            labels={"ProductName": "Product", "NetAmount": "Total Sales (€)"}
        )
        st.plotly_chart(fig)

    elif page == "Inventory Analysis":
        st.header("Inventory Analysis")
        inventory = load_data(engine, "InventoryFact")
        products = load_data(engine, "ProductDimension")

        # Merge inventory with products
        inventory = inventory.merge(products, left_on="ProductID", right_on="ProductID")

        # Stock On Hand by Product
        stock_on_hand = inventory.groupby("ProductName")["StockOnHand"].sum().reset_index()
        fig = px.bar(
            stock_on_hand,
            x="ProductName",
            y="StockOnHand",
            title="Stock On Hand by Product",
            labels={"ProductName": "Product", "StockOnHand": "Stock On Hand"}
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()