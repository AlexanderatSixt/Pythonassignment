import sys
import os
import unittest

# Add the 'src' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pandas as pd
import numpy as np
from FindIdealFunctions import get_min_sse

class TestMinSSE(unittest.TestCase):
    
    def setUp(self):
        # Simple mock training data
        self.training_df = pd.DataFrame({
            'x': [1.0, 2.0, 3.0],
            'y1': [1.0, 2.0, 3.0],
            'y2': [1.5, 2.5, 3.5]
        })
        
        # Simple mock ideal function data (just a couple of ideal functions)
        self.ideal_df = pd.DataFrame({
            'x': [1.0, 2.0, 3.0],
            'y1': [1.0, 2.0, 3.0],  # Perfect match for y1
            'y2': [1.1, 2.1, 3.1],  # Slight difference from y2
            'y3': [1.5, 2.5, 3.5]   # Perfect match for y2
        })

    
    def test_get_min_sse(self):
        # Call the function to test
        result = get_min_sse(self.training_df, self.ideal_df)
        
        # Calculate expected SSE
        expected_result = {
            'y1': {'ideal_func': 'y1', 'min_sse': 0.0},  # y1 matches y1 perfectly, so SSE = 0
            'y2': {'ideal_func': 'y3', 'min_sse': 0.0}   # y2 matches y3 perfectly, so SSE = 0
        }
        
        # Assert if calculated SSE matches expected SSE for each training function
        self.assertEqual(result['y1']['ideal_func'], expected_result['y1']['ideal_func'])
        self.assertEqual(result['y1']['min_sse'], expected_result['y1']['min_sse'])
        
        self.assertEqual(result['y2']['ideal_func'], expected_result['y2']['ideal_func'])
        self.assertEqual(result['y2']['min_sse'], expected_result['y2']['min_sse'])


if __name__ == '__main__':
    unittest.main()