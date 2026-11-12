"""Check partition isolation and training-only preprocessing."""

import unittest

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ai.ml.training.train import build_pipeline, split_data


class TrainingTests(unittest.TestCase):
    def test_stratified_disjoint_splits(self):
        features = pd.DataFrame({'age': range(100), 'workclass': ['Private'] * 100})
        target = pd.Series([0, 0, 0, 1] * 25)
        train, validation, test, y_train, y_validation, y_test = split_data(features, target)
        self.assertEqual([len(train), len(validation), len(test)], [60, 20, 20])
        self.assertFalse(set(train.index) & set(validation.index))
        self.assertFalse(set(train.index) & set(test.index))
        self.assertFalse(set(validation.index) & set(test.index))
        self.assertEqual(len(set(train.index) | set(validation.index) | set(test.index)), 100)
        for labels in [y_train, y_validation, y_test]:
            self.assertAlmostEqual(labels.mean(), 0.25, delta=0.02)

    def test_preprocessing_ignores_held_out_values(self):
        features = pd.DataFrame({'age': [20., 30., np.nan, 40.], 'workclass': ['A', 'B', 'A', 'B']})
        pipeline = build_pipeline(features, LogisticRegression())
        pipeline.fit(features, [0, 1, 0, 1])
        preprocessing = pipeline.named_steps['preprocessing']
        numeric = preprocessing.named_transformers_['numeric']
        self.assertEqual(numeric.named_steps['imputer'].statistics_[0], 30.)
        original_mean = numeric.named_steps['scaler'].mean_.copy()
        predictions = pipeline.predict(pd.DataFrame({'age': [1000.], 'workclass': ['Unseen']}))
        self.assertEqual(len(predictions), 1)
        np.testing.assert_array_equal(numeric.named_steps['scaler'].mean_, original_mean)


if __name__ == '__main__':
    unittest.main()
