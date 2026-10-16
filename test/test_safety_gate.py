import unittest

from src.agent import run_agent


class DoctorReviewRouteGateTests(unittest.TestCase):
    def test_high_risk_route_holds_every_recommendation(self):
        result = run_agent("I have an allergy and need sunscreen")

        self.assertEqual(result["route"]["route"], "doctor_review")
        self.assertTrue(result["user_response"])
        for item in result["user_response"]:
            self.assertTrue(item["doctor_review"]["requires_doctor_review"])
            self.assertIn("doctor review is required", item["message"])
            self.assertTrue(
                any(
                    reason.startswith("Query routed to doctor review:")
                    for reason in item["doctor_review"]["reasons"]
                )
            )

        for recommendation in result["trace"]["recommendations"]:
            self.assertTrue(
                recommendation["doctor_review"]["requires_doctor_review"]
            )

    def test_child_query_uses_the_request_level_gate(self):
        result = run_agent("My child needs a cleanser")

        self.assertEqual(result["route"]["route"], "doctor_review")
        self.assertTrue(result["user_response"])
        self.assertTrue(
            all(item["doctor_review"]["requires_doctor_review"]
                for item in result["user_response"])
        )

    def test_ordinary_query_keeps_normal_recommendations(self):
        result = run_agent("I need sunscreen for daily use")

        self.assertEqual(result["route"]["route"], "skin_care")
        self.assertTrue(result["user_response"])
        self.assertTrue(
            all(not item["doctor_review"]["requires_doctor_review"]
                for item in result["user_response"])
        )


if __name__ == "__main__":
    unittest.main()
