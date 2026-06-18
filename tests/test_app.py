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
        resume = self.client.get("/files/Takudzwa%20John%20CV.pdf")
        robots = self.client.get("/robots.txt")
        sitemap = self.client.get("/sitemap.xml")
        favicon = self.client.get("/favicon.svg")

        self.assertEqual(stylesheet.status_code, 200)
        self.assertEqual(portrait.status_code, 200)
        self.assertEqual(resume.status_code, 200)
        self.assertEqual(robots.status_code, 200)
        self.assertEqual(sitemap.status_code, 200)
        self.assertEqual(favicon.status_code, 200)
        self.assertEqual(favicon.mimetype, "image/svg+xml")
        self.assertEqual(resume.mimetype, "application/pdf")

    def test_portfolio_phase_two_content_and_accessibility(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)
        stylesheet = self.client.get("/style.css").get_data(as_text=True)

        for project in (
            "SmartShelf AI",
            "AI Personal Assistant Chatbot",
            "ICT Asset Management System",
            "Portfolio Website",
            "Creatificant",
            "CodeGenius Engineers Website",
        ):
            self.assertIn(project, html)

        self.assertIn('id="experience"', html)
        self.assertIn('id="certifications"', html)
        self.assertIn("OK Zimbabwe Limited", html)
        self.assertIn("Midlands State University", html)
        self.assertIn("Student on Employment Programme, IT Department", html)
        self.assertIn('class="experience-list"', html)
        self.assertIn("August 2023 - June 2024", html)
        self.assertIn("August 2025 - June 2026", html)
        self.assertIn("Summarize MSU IT experience", html)
        self.assertIn("Show technical support experience", html)
        self.assertIn("Show networking experience", html)
        self.assertIn("project-based collaboration rather than formal employment", html)
        self.assertIn("Computer Systems Engineering Graduate", html)
        self.assertIn("takudzwajohn3275@gmail.com", html)
        self.assertIn("+263 786 530 315", html)
        self.assertIn("+263 712 723 622", html)
        self.assertEqual(html.count("Problem solved"), 6)
        self.assertEqual(html.count("Key features"), 6)
        self.assertIn("Full-stack &amp; IoT Developer", html)
        self.assertIn("Designer &amp; Front-end Developer", html)
        self.assertIn("Live Demo", html)
        self.assertIn("GitHub", html)
        self.assertIn("Case Study", html)
        self.assertIn("https://github.com/AshelyJT/Personal--Assistant-Bot", html)
        self.assertIn("https://creatificant.netlify.app/", html)
        self.assertIn("https://codegenius-engineers.netlify.app/", html)
        self.assertIn("<title>Takudzwa Ashely John | Graduate Computer Systems Engineer</title>", html)
        self.assertIn('property="og:title"', html)
        self.assertIn('property="og:description"', html)
        self.assertIn('name="keywords"', html)
        self.assertIn('type="application/ld+json"', html)
        self.assertIn('class="hero-contact"', html)
        self.assertIn('src="./main.js" defer', html)
        self.assertIn('rel="icon" type="image/svg+xml" href="./favicon.svg"', html)
        self.assertNotIn("fonts.cdnfonts.com", html)
        self.assertIn('href="./files/Takudzwa%20John%20CV.pdf"', html)
        self.assertIn('label class="sr-only" for="assistant-input"', html)
        self.assertIn('aria-label="Open navigation menu"', html)
        self.assertIn('class="mobile-assistant-icon"', html)
        self.assertIn("Explore my skills and projects", html)
        self.assertIn(".mobile-assistant-copy", stylesheet)
        self.assertIn(".mobile-assistant-arrow", stylesheet)
        self.assertIn(".experience-list::before", stylesheet)
        self.assertIn("@keyframes experienceBeacon", stylesheet)
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
        self.assertIn('id="assistant-greeting" hidden', html)
        self.assertIn('class="assistant-close"', html)
        self.assertIn("Starting Ashely JT Assistant...", html)
        self.assertIn("The first connection can take up to a minute while the service starts.", html)
        self.assertIn('class="assistant-wake-steps"', html)
        self.assertIn('<div class="assistant-loader" aria-hidden="true">', html)
        self.assertIn("@keyframes assistantLoaderProgress", stylesheet)
        self.assertNotIn("@keyframes assistantLoaderSpin", stylesheet)
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
        self.assertIn("isAssistantNearBottom()", script)
        self.assertIn('block.hidden = true', script)
        self.assertIn('block.hidden = false', script)
        self.assertNotIn("selected_projects[:2]", open("backend/nlp_bot.py", encoding="utf-8").read())
        self.assertNotIn("typingMessage.remove()", script)
        self.assertIn("const isReady = await ensureAssistantReady()", script)
        self.assertIn("await sendAssistantMessage()", script)
        self.assertIn("target.querySelector(\".section-heading\")", script)
        self.assertIn("- headerHeight", script)
        self.assertIn('grid-template-areas:', stylesheet)
        self.assertIn('grid-area: suggestions;', stylesheet)
        self.assertIn('.assistant-bubble.is-generating::after', stylesheet)
        self.assertIn("startAssistantWakeProgress()", script)
        self.assertIn("showAssistantGreeting()", script)
        self.assertNotIn("ASSISTANT_WAKE_MESSAGES", script)
        self.assertIn('class="assistant-response-divider"', script)
        self.assertIn('class="assistant-project-heading"', script)
        self.assertIn(".assistant-close span::before", stylesheet)
        self.assertIn(".assistant-close span::after", stylesheet)

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
        response = self.post_chat("Tell me about SmartShelf AI")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("SmartShelf AI", payload["response"])
        self.assertIn("Machine Learning", payload["response"])
        self.assertNotIn("Stack:", payload["response"])
        self.assertNotIn("Role:", payload["response"])

    def test_general_project_question_returns_all_projects(self):
        response = self.post_chat("Show me your projects")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("Here are all 6 projects", payload["response"])
        self.assertIn("**1. SmartShelf AI**", payload["response"])
        self.assertIn("**6. CodeGenius Engineers Website**", payload["response"])
        for project in (
            "SmartShelf AI",
            "AI Personal Assistant Chatbot",
            "ICT Asset Management System",
            "Portfolio Website",
            "Creatificant",
            "CodeGenius Engineers Website",
        ):
            self.assertIn(project, payload["response"])

    def test_chatbot_question_returns_project_details(self):
        response = self.post_chat("Tell me about the AI Personal Assistant Chatbot")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("AI Personal Assistant Chatbot", payload["response"])
        self.assertIn("web interface", payload["response"])

    def test_asset_management_question_returns_internship_project(self):
        response = self.post_chat("Tell me about the ICT Asset Management System")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("ICT Asset Management System", payload["response"])
        self.assertIn("tracking ict assets", payload["response"].lower())

    def test_creatificant_question_returns_project_details(self):
        response = self.post_chat("Tell me about Creatificant")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("Creatificant", payload["response"])
        self.assertIn("creative design", payload["response"].lower())
        self.assertIn("https://creatificant.netlify.app/", payload["response"])

    def test_codegenius_project_question_returns_project_details(self):
        response = self.post_chat("Tell me about the CodeGenius Engineers Website")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("CodeGenius Engineers Website", payload["response"])
        self.assertIn("project contributor", payload["response"].lower())
        self.assertIn("https://codegenius-engineers.netlify.app/", payload["response"])

    def test_codegenius_affiliation_is_not_presented_as_employment(self):
        response = self.post_chat("Are you part of CodeGenius Engineers Group?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "about")
        self.assertIn("project-based collaboration", payload["response"].lower())
        self.assertIn("not formal employment", payload["response"])
        self.assertIn("available for full-time graduate opportunities", payload["response"].lower())
        self.assertIn("Translate business and project requirements", payload["response"])
        self.assertIn("HTML, CSS, JavaScript", payload["response"])
        self.assertIn("https://codegenius-engineers.netlify.app/", payload["response"])

    def test_codegenius_contribution_question_uses_collaboration_knowledge(self):
        response = self.post_chat("What did you do with CodeGenius?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "about")
        self.assertIn("Software Developer and Project Contributor", payload["response"])
        self.assertIn("technical planning", payload["response"])

    def test_general_codegenius_question_returns_website_project(self):
        response = self.post_chat("What is CodeGenius?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "projects")
        self.assertIn("CodeGenius Engineers Website", payload["response"])
        self.assertIn("Responsive Design", payload["response"])

    def test_internship_response_mentions_asset_management_work(self):
        response = self.post_chat("Tell me about your internship experience")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "experience")
        self.assertIn("OK Zimbabwe Limited", payload["response"])
        self.assertIn("network support", payload["response"])
        self.assertIn("cybersecurity awareness", payload["response"])

    def test_msu_student_on_employment_experience(self):
        response = self.post_chat("What experience does Takudzwa have at Midlands State University?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "experience")
        self.assertIn("Student on Employment Programme", payload["response"])
        self.assertIn("Midlands State University", payload["response"])
        self.assertIn("university staff and students", payload["response"])

    def test_student_on_employment_programme_question(self):
        response = self.post_chat("What is the Student on Employment Programme?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "experience")
        self.assertIn("while studying", payload["response"])
        self.assertIn("professional IT support duties", payload["response"])

    def test_technical_support_hardware_and_networking_questions(self):
        questions = [
            "What technical support experience does Takudzwa have?",
            "Does Takudzwa have hardware troubleshooting experience?",
            "Does Takudzwa have networking support experience?",
        ]

        for question in questions:
            response = self.post_chat(question)
            payload = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(payload["intent"], "experience")
            self.assertIn("Midlands State University", payload["response"])
            self.assertIn("technical support", payload["response"].lower())
            self.assertIn("Networking Department", payload["response"])

    def test_skills_response_is_conversational(self):
        response = self.post_chat("What are your technical skills?")
        payload = response.get_json()

        self.assertIn("Programming", payload["response"])
        self.assertIn("Cybersecurity", payload["response"])
        self.assertIn("Oracle Cloud", payload["response"])

    def test_certifications_are_grouped_by_focus(self):
        response = self.post_chat("what certifications do you have")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "certifications")
        self.assertIn("AI & Data", payload["response"])
        self.assertIn("Software Development", payload["response"])
        self.assertIn("Cloud, Infrastructure & DevOps", payload["response"])

    def test_career_availability_response(self):
        response = self.post_chat("Are you available for graduate trainee roles?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "opportunities")
        self.assertIn("Graduate Trainee", payload["response"])
        self.assertIn("ICT Support", payload["response"])

    def test_problem_solving_question_returns_behavioral_story(self):
        response = self.post_chat("How did you solve a difficult problem?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "behavioral")
        self.assertIn("ICT asset tracking", payload["response"])
        self.assertNotIn("based in Harare", payload["response"])

    def test_contact_response_includes_phone_numbers(self):
        response = self.post_chat("How can I contact you?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("takudzwajohn3275@gmail.com", payload["response"])
        self.assertIn("+263 786 530 315", payload["response"])
        self.assertIn("+263 712 723 622", payload["response"])

    def test_education_response_identifies_graduate_status(self):
        response = self.post_chat("What is your education?")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["intent"], "education")
        self.assertIn("graduate of", payload["response"])
        self.assertIn("completed in 2026", payload["response"])

    def test_empty_message_is_rejected(self):
        response = self.post_chat("")
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("Please enter a message", payload["response"])


if __name__ == "__main__":
    unittest.main()
