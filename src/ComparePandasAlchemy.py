import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from ConfigandImport import Idealfunctions

#Set-up DB Session
engine = create_engine("sqlite:///DataDB_new.db")
Session = sessionmaker(bind=engine)
session = Session()

# Using pandas read_sql with custom SQL query
def load_data_pandas(session, table_name):
    start_time = time.perf_counter()  # Start timer
    df = pd.read_sql(f'SELECT * FROM "{table_name}"', con=session.bind)
    end_time = time.perf_counter()  # End timer
    execution_time = end_time - start_time
    return df, execution_time

# Using SQLAlchemy without SQL Query
def load_df_SQLAlchemy(session, model):
    start_time = time.perf_counter()  # Start timer
    df = pd.read_sql(session.query(model).statement, session.bind)
    end_time = time.perf_counter()  # End timer
    execution_time = end_time - start_time
    return df, execution_time

# Function to compare both
def compare_loading_times(session, table_name, model):
    # Measure time for Pandas
    df_pandas, time_pandas = load_data_pandas(session, table_name)
    print(f"Pandas load time: {time_pandas:.6f} seconds")

    # Measure time for SQLAlchemy
    df_sqlalchemy, time_sqlalchemy = load_df_SQLAlchemy(session, model)
    print(f"SQLAlchemy load time: {time_sqlalchemy:.6f} seconds")

    # Determine which is faster
    if time_pandas < time_sqlalchemy:
        print("Pandas was faster.")
    else:
        print("SQLAlchemy was faster.")

# Execute function
compare_loading_times(session, 'idealfunctions', Idealfunctions)
