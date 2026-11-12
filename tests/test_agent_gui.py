"""Desktop smoke test; skip on systems without a usable Tk display."""

import time
import unittest

try:
    import tkinter as tk
except ImportError:
    tk = None


@unittest.skipIf(tk is None, 'Tkinter is not installed')
class AgentGuiTests(unittest.TestCase):
    def test_example_prediction_reset_and_schema(self):
        from ai.agent.gui import AgentWindow

        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f'Tk display/runtime unavailable: {exc}')
        root.withdraw()
        window = AgentWindow(root)
        try:
            window.load_example()
            self.assertIn('fnlwgt', window.editor.get('1.0', 'end'))
            window.send()
            self.assertTrue(window.busy)
            self.assertEqual(str(window.send_button['state']), 'disabled')
            self.wait_for_response(root, window)
            self.assertIn('probabilities', window.transcript.get('1.0', 'end'))
            window.reset()
            self.assertEqual(window.messages, [])
            window.send('/schema')
            self.wait_for_response(root, window)
            self.assertIn('required_features', window.transcript.get('1.0', 'end'))
        finally:
            window.close()

    def wait_for_response(self, root, window):
        deadline = time.monotonic() + 30
        while window.busy and time.monotonic() < deadline:
            root.update()
            time.sleep(0.02)
        self.assertFalse(window.busy, 'Timed out waiting for agent response')


if __name__ == '__main__':
    unittest.main()
