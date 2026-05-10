import unittest
from unittest.mock import patch

from app import assessment


class AssessmentTests(unittest.TestCase):
    def tearDown(self) -> None:
        assessment.clear_sessions()

    def test_math_assessment_flow(self):
        with patch("app.assessment.pick_assessment_question", return_value="Assessment question math: What is 9 + 6? Answer: 15"):
            text = assessment.start_assessment("s1", "please start math assessment")
        self.assertIn("assessment question", text.lower())
        self.assertTrue(assessment.has_pending_assessment("s1"))

        result, passed = assessment.grade_assessment_answer("s1", "15")
        self.assertTrue(passed)
        self.assertIn("correct", result.lower())

    def test_english_assessment_grading(self):
        assessment.set_assessment_state_for_test(
            "s2",
            assessment.AssessmentState(
            question="Assessment question english: Write one sentence using the word 'because'.",
            expected_answer=None,
            ),
        )
        result, passed = assessment.grade_assessment_answer("s2", "I study hard because I love math.")
        self.assertTrue(passed)
        self.assertIn("passed", result.lower())


if __name__ == "__main__":
    unittest.main()
