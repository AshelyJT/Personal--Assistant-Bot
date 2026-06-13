import re
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
        self.assertIn(b"Ashely JT Assistant", response.data)
        self.assertIn(b"Ask My Assistant", response.data)
        self.assertIn(b'id="assistant-drawer"', response.data)
        self.assertIn(b"./style.css", response.data)
        self.assertNotIn(b"{{", response.data)

    def test_portfolio_assets_and_resume_are_served(self):
        stylesheet = self.client.get("/style.css")
        portrait = self.client.get("/images/me.jpg")
        resume = self.client.get("/files/Takudzwa-Ashely-John-CV.pdf")

        self.assertEqual(stylesheet.status_code, 200)
        self.assertEqual(portrait.status_code, 200)
        self.assertEqual(resume.status_code, 200)
        self.assertEqual(resume.mimetype, "application/pdf")

    def test_portfolio_phase_two_content_and_accessibility(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        for project in (
            "SmartShelf AI Pricing System",
            "CodeGenius Website",
            "Personal Assistant Bot",
            "Web Portfolio",
        ):
            self.assertIn(project, html)

        self.assertIn('href="./files/Takudzwa-Ashely-John-CV.pdf"', html)
        self.assertIn('label class="sr-only" for="assistant-input"', html)
        self.assertIn('aria-label="Open navigation menu"', html)
        self.assertNotIn('href=""', html)
        self.assertIsNone(re.search(r"\bto\s+to\b", html, re.IGNORECASE))
        self.assertNotIn("perfomance", html.lower())
        self.assertNotIn("UI/UX Designing", html)

    def test_assistant_widget_uses_production_api_and_wake_states(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        script = self.client.get("/main.js").get_data(as_text=True)
        stylesheet = self.client.get("/style.css").get_data(as_text=True)

        self.assertIn("Ashely JT Assistant", html)
        self.assertIn("Starting Ashely JT Assistant...", html)
        self.assertIn("The assistant is waking up. This may take a moment.", html)
        self.assertRegex(
            script,
            r'const ASSISTANT_API_BASE_URL = "https://[^"]+";',
        )
        self.assertIn("`${ASSISTANT_API_BASE_URL}/health`", script)
        self.assertIn("`${ASSISTANT_API_BASE_URL}/chat`", script)
        self.assertIn("ASSISTANT_HEALTH_RETRY_MS", script)
        self.assertIn("while (Date.now() < deadline)", script)
        self.assertIn("ASSISTANT_TYPEWRITER_WORD_DELAY_MS", script)
        self.assertIn("await typeAssistantResponse(typingMessage, answer.response)", script)
        self.assertIn("document.createTreeWalker", script)
        self.assertNotIn("typingMessage.remove()", script)
        self.assertIn('grid-template-areas:', stylesheet)
        self.assertIn('grid-area: suggestions;', stylesheet)
        self.assertIn('.assistant-bubble.is-generating::after', stylesheet)
        self.assertIn(
            "The assistant is taking longer than usual. You can wait a moment or try again.",
            script,
        )

    def test_health_endpoint_and_cors_headers(self):
        response = self.client.get("/health", headers={"Origin": "https://takudzwa-john.tech"})
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload, {"status": "ok"})
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])

    def test_chat_preflight_allows_cross_origin_requests(self):
        response = self.client.options(
            "/chat",
            headers={
                "Origin": "https://takudzwa-john.tech",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.headers["Access-Control-Allow-Headers"], "Content-Type")

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

    def test_problem_solving_question_returns_behavioral_story(self):
        response = self.post_chat("How did you solve a difficult problem?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "behavioral")
        self.assertIn("legacy workflow", payload["response"])
        self.assertNotIn("based in Harare", payload["response"])

    def test_contact_response_includes_phone_numbers(self):
        response = self.post_chat("How can I contact you?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("0786530315", payload["response"])
        self.assertIn("0712723622", payload["response"])

    def test_empty_message_is_rejected(self):
        response = self.post_chat("")
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("Please enter a message", payload["response"])


if __name__ == "__main__":
    unittest.main()
