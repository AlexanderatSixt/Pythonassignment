from bokeh.plotting import figure, show, output_file, reset_output
from bokeh.models import ColumnDataSource, Band

def plot_training_vs_ideal_bokeh(training_df, ideal_df, best_ideal_df):
    """
    Plots the training functions against their best corresponding ideal functions using Bokeh.

    Args:
    - training_df (pd.DataFrame): DataFrame containing the training data with columns 'x', 'y1', 'y2', 'y3', 'y4'.
    - ideal_df (pd.DataFrame): DataFrame containing the ideal functions with 'x' and multiple 'y' columns.
    - best_ideal_df (pd.DataFrame): DataFrame mapping training functions to their best ideal functions.
    """
    reset_output()  # Clear any previous output configurations
    output_file("Visualisations/Training_vs_Ideal_Functions.html")  # Specify output file for the plot

    # Create a Bokeh figure
    p = figure(title="Training Functions vs. Best Matching Ideal Functions", 
               x_axis_label='X', y_axis_label='Y', width=800, height=600)
    
    # Define color palettes for training and ideal functions
    training_colors = ["green", "blue", "orange", "red"]
    ideal_colors = ["red", "orange", "blue", "green"]

    # Plot each training function and its corresponding best ideal function
    for index, row in best_ideal_df.iterrows():
        training_func = row["Training Function"]
        ideal_func = row["Ideal Function"]
        training_col = f"{training_func} (training func)"
        ideal_col = f"{ideal_func} (ideal func)"

        # Assign colors based on function number
        training_color = training_colors[int(training_func[-1]) - 1]
        ideal_color = ideal_colors[int(training_func[-1]) - 1]

        # Plot the training function with a solid line
        p.line(training_df["x"], training_df[training_col], 
               legend_label=training_func, color=training_color, line_width=2)

        # Plot the corresponding ideal function with a dashed line
        if ideal_col in ideal_df.columns:
            p.line(ideal_df["x"], ideal_df[ideal_col], 
                   legend_label=ideal_col, color=ideal_color, line_dash="dotted", line_width=4)

    # Customize the plot ranges and legend
    p.x_range.start = -20
    p.x_range.end = 20
    p.y_range.start = -40
    p.y_range.end = 40
    p.legend.location = "top_center"
    p.legend.orientation = "horizontal"
    p.legend.label_text_font_size = "8pt"

    # Show the plot
    show(p)


from bokeh.models import ColumnDataSource, HoverTool, Band
from bokeh.plotting import figure, show, output_file, reset_output

def plot_ideal_functions_with_bands_bokeh(ideal_functions_df, ideal_functions, max_devs, within_threshold_df, outside_threshold_df):
    """
    Plots ideal functions with deviation bands and test data points using Bokeh.

    Args:
    - ideal_functions_df (pd.DataFrame): DataFrame containing the ideal functions with 'x' and multiple 'y' columns.
    - ideal_functions (list): List of ideal function column names.
    - max_devs (dict): Dictionary containing maximum deviation for each ideal function.
    - within_threshold_df (pd.DataFrame): DataFrame of test points within the deviation threshold.
    - outside_threshold_df (pd.DataFrame): DataFrame of test points outside the deviation threshold.
    """
    reset_output()  # Clear previous output configurations
    output_file("Ideal_Functions_vs_Test_Data.html")  # Specify output file for the plot

    # Create a Bokeh figure
    p = figure(title='Ideal Functions incl. Threshold vs. Test Data', 
               x_axis_label='X', y_axis_label='Y', width=800, height=600)

    # Define colors for the ideal functions
    color_list = ["purple", "red", "blue", "orange"]

    # Plot each ideal function with its corresponding max deviation band
    for i, ideal_func in enumerate(ideal_functions):
        ideal_func_column = f"{ideal_func} (ideal func)"
        max_dev = max_devs.get(ideal_func, 0)
        color = color_list[i % len(color_list)]

        if ideal_func_column in ideal_functions_df.columns:
            ideal_functions_dict = {
                'x': ideal_functions_df['x'].values,
                'y': ideal_functions_df[ideal_func_column].values,
                'lower': (ideal_functions_df[ideal_func_column] - max_dev).values,
                'upper': (ideal_functions_df[ideal_func_column] + max_dev).values,
                "funclabel": [f'{ideal_func_column} ideal func with threshold'] * len(ideal_functions_df)
            }
            source = ColumnDataSource(data=ideal_functions_dict)

            # Plot the ideal function line
            line = p.line('x', 'y', source=source, 
                          legend_label=f'Ideal {ideal_func}', line_width=2, color=color)

            # Add the max deviation band
            band = Band(base='x', lower='lower', upper='upper', source=source,
                        level='underlay', fill_color=color, fill_alpha=0.2)
            p.add_layout(band)

            # Add a hover tool for this line
            hover_tool_func = HoverTool(
                tooltips=[("Function", "@funclabel")],
                renderers=[line], mode='mouse'  # Hover appears only on the line
            )
            p.add_tools(hover_tool_func)

    # Create ColumnDataSource for within-threshold test data points
    within_source = ColumnDataSource(data={
        'x': within_threshold_df['X (test func)'],
        'y': within_threshold_df['Y (test func)'],
        'ID': within_threshold_df['ID'],
        'IdealFunction': within_threshold_df['No. of ideal func']
    })

    # Create ColumnDataSource for outside-threshold test data points
    outside_source = ColumnDataSource(data={
        'x': outside_threshold_df['X (test func)'],
        'y': outside_threshold_df['Y (test func)'],
        'ID': outside_threshold_df['ID'],
        'IdealFunction': outside_threshold_df['No. of ideal func']
    })

    # Plot test data points: within-threshold in green and outside-threshold in red
    p.scatter(x='x', y='y', source=within_source, color='green', marker='circle', size=8, legend_label='Within Threshold')
    p.scatter(x='x', y='y', source=outside_source, color='red', marker='x', size=8, legend_label='Outside Threshold')

    # Add hover tools for test data points
    hover_tool_within = HoverTool(tooltips=[('ID', '@ID'), ('Ideal Function', '@IdealFunction')],
                                  renderers=[p.renderers[-2]], mode='mouse')
    hover_tool_outside = HoverTool(tooltips=[('ID', '@ID'), ('Ideal Function', '@IdealFunction')],
                                   renderers=[p.renderers[-1]], mode='mouse')
    p.add_tools(hover_tool_within, hover_tool_outside)

    # Customize and show the plot
    p.add_layout(p.legend[0], 'right')
    p.legend.title = "Legend"
    show(p)


import matplotlib.pyplot as plt

def plot_ideal_function_counts(results_df):
    """
    Plots a bar graph showing the count of test points within threshold for each ideal function.

    Args:
    - results_df (pd.DataFrame): DataFrame containing results with 'No. of ideal func' and 'within_threshold' columns.
    """
    # Filter DataFrame for rows where within_threshold is True
    filtered_data = results_df[results_df['within_threshold']]

    # Count occurrences of each ideal function
    ideal_function_counts = filtered_data['No. of ideal func'].value_counts()

    # Plot the counts
    plt.figure(figsize=(10, 6))
    ideal_function_counts.plot(kind='bar', color='skyblue', edgecolor='black')

    # Add titles and labels
    plt.title('Test Points within Threshold per Ideal Function', fontsize=14)
    plt.xlabel('Ideal Function', fontsize=12)
    plt.ylabel('Within Threshold Count', fontsize=12)
    
    # Show the grid and the plot
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, DataTable, TableColumn
from bokeh.layouts import layout

def create_table3(results_df):
    """
    Creates and displays a Bokeh DataTable from the given results DataFrame.

    Args:
    - results_df (pd.DataFrame): DataFrame containing results with 'within_threshold' and relevant columns for display.
    """
    df_for_table = results_df[results_df['within_threshold'] == True][["X (test func)", "Y (test func)", "Delta Y (test func)", "No. of ideal func"]]

    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df_for_table)

    # Define the columns for the Bokeh DataTable
    columns = [
        TableColumn(field="X (test func)", title="X (test func)"),
        TableColumn(field="Y (test func)", title="Y (test func)"),
        TableColumn(field="Delta Y (test func)", title="Delta Y (test func)"),
        TableColumn(field="No. of ideal func", title="No. of ideal func"),
    ]

    # Create the Bokeh DataTable
    data_table = DataTable(source=source, columns=columns, width=800, height=350)

    # Output the result to an HTML file
    output_file("table3_bokeh.html")

    # Show the DataTable
    layout_table = layout([[data_table]])
    show(layout_table)
