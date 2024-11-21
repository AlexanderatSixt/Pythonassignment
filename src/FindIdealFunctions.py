from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
import logging
from contextlib import contextmanager
from ConfigandImport import Trainingdata, Idealfunctions, Parent
from Vizualisationsbokeh import plot_training_vs_ideal_bokeh

# Set up logging for the script
logging.basicConfig(level=logging.INFO)

# Database setup using Parent class
engine, Session = Parent.setup_database()

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of database operations.
    
    Yields:
        session (Session): A session object that is committed if operations succeed,
        or rolled back if an exception occurs.
    """
    session = Session()  # Create a new session
    try:
        yield session  # Make the session available within the context
        session.commit()  # Commit the transaction on success
    except:
        session.rollback()  # Rollback the transaction if an exception occurs
        raise  # Re-raise the exception to ensure it's handled further up
    finally:
        session.close()  # Ensure session is always closed to release resources

def load_df(session, model):
    """
    Load data from a SQLAlchemy model into a Pandas DataFrame.

    Args:
        session (Session): Active SQLAlchemy session to interact with the database.
        model (Base): SQLAlchemy model class representing the table to load.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the specified table.
    """
    return pd.read_sql(session.query(model).statement, session.bind)

def get_min_sse(training_df, ideal_df):
    """
    Calculate the minimum Sum of Squared Errors (SSE) between each training function and all ideal functions.

    Args:
        training_df (pd.DataFrame): DataFrame containing the training functions (y1 to y4).
        ideal_df (pd.DataFrame): DataFrame containing all the ideal functions.

    Returns:
        dict: A dictionary with the minimum SSE and corresponding ideal function for each training function.
    """
    min_sse = {f"y{j}": {"ideal_func": None, "min_sse": float("inf")} for j in range(1, 5)}
    
    training_array = training_df.iloc[:, 1:5].values  # Extract values for y1 to y4 (training functions)
    ideal_array = ideal_df.iloc[:, 1:].values  # Extract values for all ideal functions
    
    num_training_funcs = training_array.shape[1]  # Number of training functions
    num_ideal_funcs = ideal_array.shape[1]  # Number of ideal functions
    
    for j in range(num_training_funcs):  # Iterate over all training functions (y1 to y4)
        for i in range(num_ideal_funcs):  # Iterate over all ideal functions
            sse = np.sum((training_array[:, j] - ideal_array[:, i]) ** 2)  # Calculate SSE
            if sse < min_sse[f"y{j+1}"]["min_sse"]:
                min_sse[f"y{j+1}"] = {"ideal_func": f"y{i+1}", "min_sse": sse}  # Update min SSE if a lower value is found

    return min_sse

def create_results_df(min_sse):
    """
    Create a DataFrame from the minimum SSE results.

    Args:
        min_sse (dict): Dictionary containing the minimum SSE and corresponding ideal function for each training function.

    Returns:
        pd.DataFrame: DataFrame summarizing the best ideal functions for each training function and their SSE values.
    """
    return pd.DataFrame([
        {"Training Function": func, "Ideal Function": result["ideal_func"], "SSE": result["min_sse"]}
        for func, result in min_sse.items()
    ])

def main():
    """
    Main function to manage the workflow of loading data, calculating minimum SSE, and plotting the results.
    """
    with session_scope() as session:  # Ensure transactional scope for database operations
        # Load data from the database
        training_df = load_df(session, Trainingdata)
        ideal_df = load_df(session, Idealfunctions)
        
        # Calculate the minimum SSE between training and ideal functions
        min_sse = get_min_sse(training_df, ideal_df)
        
        # Create a DataFrame of the results and save it to a CSV file
        best_ideal_df = create_results_df(min_sse)
        best_ideal_df.to_csv("ideal_vs_training.csv", index=False)
        
        # Visualize the results using Bokeh
        plot_training_vs_ideal_bokeh(training_df, ideal_df, best_ideal_df)

if __name__ == "__main__":
    main()
