"""Offline graph/tool integration and input validation tests."""

import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from langchain_core.messages import HumanMessage, ToolMessage

from ai.agent.graph import build_agent
from ai.agent.tools import input_schema, load_model, predict_income


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((Path(__file__).resolve().parents[1] / 'ai/agent/example_record.json').read_text())

    def test_mock_graph_calls_actual_mlp(self):
        result = build_agent('mock').invoke({'messages': [HumanMessage(content=json.dumps(self.record))]})
        tool_messages = [message for message in result['messages'] if isinstance(message, ToolMessage)]
        self.assertEqual(len(tool_messages), 1)
        output = json.loads(tool_messages[0].content)
        model = load_model()
        frame = pd.DataFrame([self.record], columns=model.feature_names_in_)
        self.assertEqual(output['prediction'], int(model.predict(frame)[0]))
        np.testing.assert_allclose(list(output['probabilities'].values()), model.predict_proba(frame)[0])
        self.assertIn(output['income'], result['messages'][-1].content)

    def test_schema_and_missing_fields(self):
        self.assertNotIn('income', input_schema.invoke({})['required_features'])
        self.assertIn('missing_features', predict_income.invoke({'record': {}}))
        result = build_agent().invoke({'messages': [HumanMessage(content='/schema')]})
        self.assertIn('required_features', result['messages'][-1].content)

    def test_invalid_numeric_and_category(self):
        for name, value in [('age', 'thirty'), ('age', float('inf')), ('sex_Male', 3), ('workclass', 'unknown')]:
            self.assertIn('error', predict_income.invoke({'record': {**self.record, name: value}}))

    def test_mock_invalid_json_and_placeholder_key(self):
        result = build_agent().invoke({'messages': [HumanMessage(content='hello')]})
        self.assertIn('JSON', result['messages'][-1].content)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-fake-key-replace-me'}):
            with self.assertRaisesRegex(ValueError, 'real OPENAI_API_KEY'):
                build_agent('openai')


if __name__ == '__main__':
    unittest.main()
