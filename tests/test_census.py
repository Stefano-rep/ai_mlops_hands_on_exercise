"""Verify notebook parity and edge cases without relying on the real dataset."""

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.backend.data import NUMERIC, correlations, distribution, filtered
from src.backend.main import education, records


class CensusAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({col: [1, 2, 3, 4] for col in NUMERIC})
        self.frame['fnlwgt'] = [1, 1, 1, 7]
        self.frame['income'] = ['<=50K', '>50K', '<=50K', '>50K']
        self.frame['sex'] = ['Female', 'Male', 'Female', 'Male']
        self.frame['education'] = ['A', 'B', 'C', 'D']

    def test_weighted_histogram(self):
        result = distribution(self.frame, 'age', 2, True)
        np.testing.assert_allclose(result['values'], [20, 80])
        self.assertAlmostEqual(sum(result['values']), 100)
        self.assertEqual(result['summary']['count'], 4)

    def test_categorical_and_education(self):
        result = distribution(self.frame, 'income', 20, False)
        self.assertEqual(sum(result['values']), 4)
        self.assertEqual(education(self.frame)['values'], [25, 25, 25, 25])

    def test_pearson_matches_pandas_and_nulls_constant(self):
        result = correlations(self.frame, 'pearson')
        np.testing.assert_allclose(result['values'], self.frame[NUMERIC].corr().values)
        self.frame['age'] = 1
        self.assertTrue(all(value is None for value in correlations(self.frame, 'pearson')['values'][0]))

    def test_cramers_binary_exclusion(self):
        result = correlations(self.frame, 'cramers_v')
        index = result['columns'].index('income')
        self.assertTrue(all(value is None for value in result['values'][index]))
        index = result['columns'].index('education')
        self.assertAlmostEqual(result['values'][index][index], 1)

    def test_filter_pagination_and_empty(self):
        with patch('src.backend.data.dataset', return_value=self.frame):
            result = filtered(search='female', income='<=50K')
            self.assertEqual(len(result), 2)
            self.assertTrue(filtered(search='[').empty)  # Literal, not regex.
        page = records(self.frame, page=2, page_size=3)
        self.assertEqual(len(page['rows']), 1)
        self.assertEqual(page['total'], 4)
        empty = self.frame.iloc[:0]
        self.assertEqual(distribution(empty, 'age', 20, False)['values'], [])
        self.assertTrue(all(v is None for row in correlations(empty, 'pearson')['values'] for v in row))


if __name__ == '__main__':
    unittest.main()
