import sys
import os
import unittest

# Add the 'src' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pandas as pd
import numpy as np
from EvaluateTestData import calculate_max_deviations  # Adjust according to your actual import path

class TestCalculateMaxDeviations(unittest.TestCase):
    
    def setUp(self):
        # Sample data for testing
        self.training_df = pd.DataFrame({
            'y1 (training func)': [1.0, 2.0, 3.0],
            'y2 (training func)': [2.0, 3.0, 4.0]
        })
        self.ideal_df = pd.DataFrame({
            'y1 (ideal func)': [1.1, 2.1, 3.1],
            'y2 (ideal func)': [2.2, 3.2, 4.2]
        })
        self.training_funcs = ['y1', 'y2']
        self.ideal_funcs = ['y1', 'y2']
    
    def test_max_deviation_calculation(self):
        # Corrected: Convert lists to NumPy arrays for subtraction
        expected_deviations = {
            'y1': np.max(np.abs(np.array([1.0, 2.0, 3.0]) - np.array([1.1, 2.1, 3.1])) * np.sqrt(2)),
            'y2': np.max(np.abs(np.array([2.0, 3.0, 4.0]) - np.array([2.2, 3.2, 4.2])) * np.sqrt(2))
        }
        
        # Call the function
        max_devs = calculate_max_deviations(self.training_df, self.ideal_df, self.training_funcs, self.ideal_funcs)
        
        # Assert results
        self.assertEqual(max_devs['y1'], expected_deviations['y1'])
        self.assertEqual(max_devs['y2'], expected_deviations['y2'])

if __name__ == '__main__':
    unittest.main()