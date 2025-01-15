import pandas as pd
from sqlalchemy import create_engine, inspect
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
    try:
        with engine.connect() as connection:
            print("Connected to SQL Server database!")
        return engine
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

# ETL Pipeline
def etl_pipeline(df):
    df.fillna({
        'CustomerEmail': 'unknown email',
        'CustomerPhone': '0000000000',
        'SupplierContact': 'Not Provided',
        'ProductPrice': '0.0',
        'CustomerName': 'Unknown',
        'CustomerAddress': 'Unknown',
        'CustomerSegment': 'Uncategorized',
        'ShipperName': 'Unknown',
        'ShippingMethod': 'Unknown',
        'ProductSubCategory': 'Uncategorized',
        'SupplierLocation': 'Unknown',
    }, inplace=True)

    # Data type conversions
    df['ProductPrice'] = pd.to_numeric(df['ProductPrice'], errors='coerce').fillna(0.0).astype(float)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['CustomerPhone'] = df['CustomerPhone'].astype(str)
    df['QuantitySold'] = df['QuantitySold'].astype(int)
    df['TotalAmount'] = df['TotalAmount'].astype(float)
    df['DiscountAmount'] = df['DiscountAmount'].astype(float)
    df['NetAmount'] = df['NetAmount'].astype(float)
    df['StockReceived'] = df['StockReceived'].astype(int)
    df['StockSold'] = df['StockSold'].astype(int)
    df['StockOnHand'] = df['StockOnHand'].astype(int)

    # Standardize text data
    df['CustomerEmail'] = df['CustomerEmail'].str.lower()
    df['CustomerSegment'] = df['CustomerSegment'].str.capitalize()

    # Extract additional features if needed
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    return df

# Load data into dimensions and fact tables
def load_data_to_database(df, engine):
    # Load DateDimension
    date_dimension_df = df[['Date']].drop_duplicates().reset_index(drop=True)
    date_dimension_df['DateID'] = date_dimension_df.index + 1
    date_dimension_df['Year'] = date_dimension_df['Date'].dt.year
    date_dimension_df['Month'] = date_dimension_df['Date'].dt.month
    date_dimension_df['Day'] = date_dimension_df['Date'].dt.day
    date_dimension_df['Quarter'] = date_dimension_df['Date'].dt.quarter
    date_dimension_df.rename(columns={'Date': 'FullDate'}, inplace=True)
    date_dimension_df.to_sql('DateDimension', con=engine, if_exists='append', index=False)

    # Load ProductDimension
    product_dimension_df = df[['ProductName', 'ProductCategory', 'ProductSubCategory', 'ProductPrice']].drop_duplicates().reset_index(drop=True)
    product_dimension_df['ProductID'] = product_dimension_df.index + 1
    product_dimension_df = product_dimension_df.drop_duplicates(subset=['ProductName'])
    product_dimension_df.to_sql('ProductDimension', con=engine, if_exists='append', index=False)

    # Load CustomerDimension
    customer_dimension_df = df[['CustomerName', 'CustomerEmail', 'CustomerSegment']].drop_duplicates().reset_index(drop=True)
    customer_dimension_df['CustomerID'] = customer_dimension_df.index + 1
    customer_dimension_df = customer_dimension_df.drop_duplicates(subset=['CustomerName'])
    customer_dimension_df.to_sql('CustomerDimension', con=engine, if_exists='append', index=False)

    # Load SupplierDimension
    supplier_dimension_df = df[['SupplierName', 'SupplierLocation', 'SupplierContact']].drop_duplicates().reset_index(drop=True)
    supplier_dimension_df['SupplierID'] = supplier_dimension_df.index + 1
    supplier_dimension_df = supplier_dimension_df.drop_duplicates(subset=['SupplierName'])
    supplier_dimension_df.to_sql('SupplierDimension', con=engine, if_exists='append', index=False)

    # Load ShipperDimension
    shipper_dimension_df = df[['ShipperName', 'ShippingMethod']].drop_duplicates().reset_index(drop=True)
    shipper_dimension_df['ShipperID'] = shipper_dimension_df.index + 1
    shipper_dimension_df = shipper_dimension_df.drop_duplicates(subset=['ShipperName'])
    shipper_dimension_df.to_sql('ShipperDimension', con=engine, if_exists='append', index=False)

    # Load SalesFact
    sales_fact_df = df[['Date', 'ProductName', 'CustomerName', 'SupplierName', 'ShipperName', 'QuantitySold', 'TotalAmount', 'DiscountAmount', 'NetAmount']].copy()
    sales_fact_df.to_sql('SalesFact', con=engine, if_exists='append', index=False)

    # Load InventoryFact
    inventory_fact_df = df[['Date', 'ProductName', 'SupplierName', 'StockReceived', 'StockSold', 'StockOnHand']].copy()
    inventory_fact_df.to_sql('InventoryFact', con=engine, if_exists='append', index=False)

    print("All tables loaded successfully.")

# Main function
if __name__ == "__main__":
    server = 'LAPTOP-AAS7RBMP'
    database = 'EcomerceDB'
    engine = connect_to_db(server, database)

    if engine:
        data = pd.read_csv("./Data/ecommerce-data-67331b7de6f07116971040.csv")
        transformed_data = etl_pipeline(data)
        load_data_to_database(transformed_data, engine)
