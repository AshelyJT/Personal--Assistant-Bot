import unittest

from backend.app import app


class ChatEndpointTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post_chat(self, message):
        return self.client.post("/chat", json={"message": message})

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Interactive Resume Assistant", response.data)

    def test_chat_returns_structured_answer(self):
        response = self.post_chat("What are your technical skills?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", payload)
        self.assertIn("intent", payload)
        self.assertIn("confidence", payload)
        self.assertIn("suggestions", payload)
        self.assertEqual(payload["intent"], "skills")

    def test_project_question_returns_project_intent(self):
        response = self.post_chat("Tell me about Campus VibeMarket")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("Campus VibeMarket", payload["response"])
        self.assertNotIn("Stack:", payload["response"])
        self.assertNotIn("Role:", payload["response"])

    def test_skills_response_is_conversational(self):
        response = self.post_chat("What are your technical skills?")
        payload = response.get_json()

        self.assertIn("My strongest language", payload["response"])
        self.assertNotIn("Languages:", payload["response"])

    def test_empty_message_is_rejected(self):
        response = self.post_chat("")
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("Please enter a message", payload["response"])


if __name__ == "__main__":
    unittest.main()
