import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Turbo256
from bokeh.models import ColumnDataSource, Legend
from FindIdealFunctions import load_df, session_scope
from ConfigandImport import Idealfunctions, Testdata, Parent

# Setup Database and Session Manager
engine, Session = Parent.setup_database()

# Seaborn Plotting Function
def plotallidealfunctions_seaborn(idealfunctions_df, test_df):
    '''This function will be used to plot the data using Seaborn
    Input Args:
    idealfunctions_df: data frame containing data points of ideal functions
    test_df: data frame containing test data points'''
    plt.figure(figsize=(18, 8))
    plt.ylim(-40, 40)

    # Create a color palette
    palette = sns.color_palette("tab10", len(idealfunctions_df.columns) - 1)

    # Plot ideal functions
    ideal_func_columns = [col for col in idealfunctions_df.columns if col != "x"]
    for i, col in enumerate(ideal_func_columns):
        plt.plot(idealfunctions_df['x'], idealfunctions_df[col], label=f'Ideal {col}',
                 color=palette[i], linestyle='--', linewidth=0.5)

    # Plot test data
    plt.scatter(test_df['x'], test_df['y'], marker='o', color='black', label="Testdata")

    plt.title('All Ideal Functions - Seaborn')
    plt.xlabel('X')
    plt.ylabel('Y')

    # Create a legend below the plot with multiple columns
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), shadow=True, ncol=5)

    # Show the plot
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# Bokeh Plotting Function
output_file("bokeh_plot_with_legend.html")

def plotallidealfunctions_bokeh(idealfunctions_df, test_df):
    '''This function will be used to plot the data using Bokeh
    Input Args:
    idealfunctions_df: data frame containing data points of ideal functions
    test_df: data frame containing test data points'''
    p = figure(title="All Ideal Functions - Bokeh", x_axis_label='X', y_axis_label='Y',
               width=1200, height=900, tools="pan,wheel_zoom,box_zoom,reset,save")

    # Set y-axis range
    p.y_range.start = -40
    p.y_range.end = 40

    # Use Turbo256 palette
    num_cols = len(idealfunctions_df.columns) - 1
    palette = Turbo256[:num_cols]

    # Plot ideal functions
    ideal_func_columns = [col for col in idealfunctions_df.columns if col != "x"]
    legend_items = []

    for i, col in enumerate(ideal_func_columns):
        #print(f"Plotting {col}...")

        # Create a data source for Bokeh
        source = ColumnDataSource(data={'x': idealfunctions_df['x'], 'y': idealfunctions_df[col]})

        # Plot each ideal function with legend_label
        line = p.line('x', 'y', source=source, legend_label=f'Ideal {col}', color=palette[i], line_dash="dashed", line_width=0.5)
        legend_items.append((f'Ideal {col}', [line]))

    # Plot test data
    p.scatter(test_df['x'], test_df['y'], marker='x', color='black', size=8, legend_label="Test Data")

    # Customize grid lines
    p.grid.grid_line_alpha = 0.3

    # Hide the built-in legend
    p.legend.visible = False

    # Create a separate legend and add it to the plot, positioned to the right
    legend = Legend(items=legend_items)
    p.add_layout(legend, 'right')  # 'right' places it to the right of the plot
    
    # Customize the legend
    legend.label_text_font_size = "8pt"
    legend = Legend(items=legend_items)
    legend.ncols=5
    legend.spacing = 5
    legend.padding = 5
    legend.glyph_width = 15
    legend.glyph_height = 15
    legend.ncols = 1  # Arrange in a single column for the right-side layout

    show(p)  # Show the plot with the legend


def main():
    """Connect to DB to provide input data for the plots"""
    with session_scope() as session:  # Corrected session_scope usage
        # Load data from the database
        idealfunctions_df = load_df(session, Idealfunctions)
        test_df = load_df(session, Testdata)
        
        # Measure time for Bokeh plot
        start_time = time.perf_counter()
        plotallidealfunctions_bokeh(idealfunctions_df, test_df)
        print(f"Bokeh plot execution time: {time.perf_counter()- start_time:.6f} seconds")

        # Measure time for Seaborn plot
        start_time = time.perf_counter()
        plotallidealfunctions_seaborn(idealfunctions_df, test_df)
        print(f"Seaborn plot execution time: {time.perf_counter() - start_time:.6f} seconds")


if __name__ == "__main__":
    main()
