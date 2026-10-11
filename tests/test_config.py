import unittest
from process_dashboard.config import format_bytes, CPU_ALERT, MEMORY_ALERT_BYTES

class ConfigTests(unittest.TestCase):
    def test_format_bytes_zero(self):
        self.assertEqual(format_bytes(0), "0 B")
    def test_format_bytes_kilobyte(self):
        self.assertEqual(format_bytes(1024), "1.0 KB")
    def test_thresholds_are_positive(self):
        self.assertGreater(CPU_ALERT, 0)
        self.assertGreater(MEMORY_ALERT_BYTES, 0)

if __name__ == "__main__":
    unittest.main()
