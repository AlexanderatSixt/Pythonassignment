from ConfigandImport import Parent
import pandas as pd
import numpy as np
import logging
from FindIdealFunctions import session_scope, load_df

# Logging setup
logging.basicConfig(level=logging.INFO)

# Setup Database and Session Manager
engine, Session = Parent.setup_database()

def calculate_max_deviations(training_df, ideal_df, training_funcs, ideal_funcs):
    """
    Calculate the maximum deviations between training and ideal functions.

    Args:
        training_df (pd.DataFrame): DataFrame containing training function data.
        ideal_df (pd.DataFrame): DataFrame containing ideal function data.
        training_funcs (list): List of training function column names.
        ideal_funcs (list): List of ideal function column names.

    Returns:
        dict: A dictionary where keys are ideal function names and values are the maximum deviations.
    """
    max_devs = {}
    for train_func, ideal_func in zip(training_funcs, ideal_funcs):
        ideal_col = f"{ideal_func} (ideal func)"
        train_col = f"{train_func} (training func)"
        
        if train_col in training_df.columns and ideal_col in ideal_df.columns:
            deviations = np.abs(training_df[train_col] - ideal_df[ideal_col]) * np.sqrt(2)
            max_devs[ideal_func] = deviations.max()
            logging.info(f"Max deviation for {ideal_func} with {train_func}: {max_devs[ideal_func]}")
        else:
            logging.warning(f"Missing columns for {train_col} or {ideal_col}.")
    
    return max_devs

def match_test_to_ideal(test_data_df, ideal_functions_df, max_devs, ideal_funcs, session):
    """
    Match test data to the ideal functions based on deviation thresholds.

    Args:
        test_data_df (pd.DataFrame): DataFrame containing test data.
        ideal_functions_df (pd.DataFrame): DataFrame containing ideal functions.
        max_devs (dict): Dictionary containing the maximum deviations for each ideal function.
        ideal_funcs (list): List of ideal function names.
        session (Session): SQLAlchemy session for database operations.

    Returns:
        pd.DataFrame: DataFrame containing the matching results between test data and ideal functions.
    """
    results = []
    test_data_df['ID'] = range(1, len(test_data_df) + 1)  # Assign an ID to each test point

    for _, test_row in test_data_df.iterrows():
        x_test = test_row['x']
        y_test = test_row['y']
        
        for ideal_func in ideal_funcs:
            ideal_col = f"{ideal_func} (ideal func)"
            if ideal_col in ideal_functions_df.columns:
                ideal_y_value = ideal_functions_df.loc[ideal_functions_df['x'] == x_test, ideal_col].values
                if len(ideal_y_value) > 0:
                    delta_y = abs(y_test - ideal_y_value[0])
                    max_deviation = max_devs.get(ideal_func, float('inf'))
                    within_threshold = delta_y <= max_deviation

                    results.append({
                        "ID": test_row['ID'],
                        "X (test func)": x_test,
                        "Y (test func)": y_test,
                        "Delta Y (test func)": delta_y,
                        "No. of ideal func": ideal_func,
                        "Test Deviation": delta_y,
                        "Max Deviation": max_deviation,
                        "within_threshold": within_threshold
                    })

    results_df = pd.DataFrame(results)
    results_df.to_csv("Test Data vs Ideal Function.csv")
    logging.info("Finished matching test data to ideal functions.")
    
    filtered_results = results_df[results_df["within_threshold"] == True]
    columns_to_export = ["X (test func)", "Y (test func)", "Delta Y (test func)", "No. of ideal func"]
    filtered_results[columns_to_export].to_sql('Table 3', con=session.bind, if_exists='replace', index=False)
    results_df.to_csv("Test Data Evaluation.csv")
    print(filtered_results[columns_to_export])
    logging.info("Exported results to 'Table 3' in the database.")
    
    return results_df

def main():
    """
    Main function to execute the workflow for loading data, calculating deviations, matching test data to ideal functions,
    and visualizing the results.
    """
    with session_scope() as session:
        from ConfigandImport import Trainingdata, Testdata, Idealfunctions
        
        # Load data from the database
        test_data_df = load_df(session, Testdata)
        ideal_functions_df = load_df(session, Idealfunctions)
        training_data_df = load_df(session, Trainingdata)
        
        # Load the best ideal functions from CSV
        best_ideal_df = pd.read_csv("ideal_vs_training.csv")
        training_funcs = best_ideal_df["Training Function"].tolist()
        ideal_funcs = best_ideal_df["Ideal Function"].tolist()
        
        # Calculate maximum deviations
        max_devs = calculate_max_deviations(training_data_df, ideal_functions_df, training_funcs, ideal_funcs)
        
        # Match test data to ideal functions
        results_df = match_test_to_ideal(test_data_df, ideal_functions_df, max_devs, ideal_funcs, session)
        
        # Get rows within the threshold
        within_threshold_df = results_df[results_df['within_threshold'] == True]
        
        # Filter out rows outside the threshold
        outside_df = results_df[~results_df['ID'].isin(within_threshold_df['ID'])]
        outside_threshold_df = outside_df.drop_duplicates(subset="ID", keep='first')
        outside_threshold_df['No. of ideal func'] = "Not matched"
        
        logging.info("Plotting data...")
        from Vizualisationsbokeh import plot_ideal_functions_with_bands_bokeh, plot_ideal_function_counts, create_table3
        
        # Plot visualizations using Bokeh
        plot_ideal_functions_with_bands_bokeh(ideal_functions_df, ideal_funcs, max_devs, within_threshold_df, outside_threshold_df)
        plot_ideal_function_counts(results_df)
        create_table3(results_df)

if __name__ == "__main__":
    main()
