# test_scoring.py

import unittest
from healthcare_api_assessment import score_bp, score_temp, score_age, has_invalid_data

class TestScoringFunctions(unittest.TestCase):

    def test_score_bp(self):
        self.assertEqual(score_bp("150/95"), 3)
        self.assertEqual(score_bp("135/85"), 2)
        self.assertEqual(score_bp("125/75"), 1)
        self.assertEqual(score_bp("110/70"), 0)
        self.assertEqual(score_bp("invalid"), 0)

    def test_score_temp(self):
        self.assertEqual(score_temp(101.2), 2)
        self.assertEqual(score_temp(100.0), 1)
        self.assertEqual(score_temp(98.6), 0)
        self.assertEqual(score_temp("bad"), 0)

    def test_score_age(self):
        self.assertEqual(score_age(70), 2)
        self.assertEqual(score_age(50), 1)
        self.assertEqual(score_age(30), 0)
        self.assertEqual(score_age("text"), 0)

    def test_has_invalid_data(self):
        valid = {"blood_pressure": "120/80", "temperature": 98.6, "age": 45}
        self.assertFalse(has_invalid_data(valid))
        self.assertTrue(has_invalid_data({"blood_pressure": "bad", "temperature": 98.6, "age": 45}))
        self.assertTrue(has_invalid_data({"blood_pressure": "120/80", "temperature": "bad", "age": 45}))
        self.assertTrue(has_invalid_data({"blood_pressure": "120/80", "temperature": 98.6, "age": "bad"}))

if __name__ == "__main__":
    unittest.main()
