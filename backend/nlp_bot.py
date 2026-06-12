import json
import os
import re

import spacy


class AdvancedPersonalAssistant:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file = os.path.join(base_dir, "data.json")

        self.load_data(data_file)
        self.nlp = self.load_nlp_model()
        self.context = {"last_intent": None}
        self.last_confidence = 0.0
        self.setup_knowledge_base()

    def load_data(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print("Data loaded successfully")
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading data: {e}")
            self.data = {}

    def load_nlp_model(self):
        try:
            print("Loading NLP model...")
            return spacy.load("en_core_web_md")
        except OSError:
            print("'en_core_web_md' not found. Using 'en_core_web_sm' with keyword fallback.")
            try:
                return spacy.load("en_core_web_sm")
            except OSError:
                print("'en_core_web_sm' not found. Using keyword-only matching.")
                return None

    def setup_knowledge_base(self):
        self.intents = {
            "greeting": ["hello", "hi", "hey", "greetings"],
            "about": ["about", "yourself", "who are you", "summary", "profile", "intro"],
            "skills": ["skills", "technologies", "stack", "programming", "languages", "tools", "libraries"],
            "experience": ["experience", "work", "job", "internship", "career", "ok zimbabwe"],
            "education": ["education", "degree", "university", "college", "school", "msu"],
            "projects": ["projects", "portfolio", "apps", "github", "website", "codegenius", "vibemarket"],
            "contact": ["contact", "email", "linkedin", "reach", "phone"],
            "achievements": ["achievement", "achievements", "accomplishment", "impact", "built", "automated"],
            "behavioral": ["challenge", "mistake", "leadership", "teamwork", "conflict", "proud"],
            "technical": ["architecture", "coding style", "deep dive", "specifics"],
        }

        self.intent_vectors = {}
        if self.nlp and len(self.nlp.vocab.vectors) > 0:
            for intent, keywords in self.intents.items():
                self.intent_vectors[intent] = self.nlp(" ".join(keywords))

    def get_intent(self, user_input):
        text = user_input.lower()
        tokens = set(re.findall(r"[a-z0-9]+", text))

        if any(t in text for t in ["python", "django", "flutter", "react"]):
            self.last_confidence = 0.92
            return "technical"

        priority_intents = [
            "achievements",
            "projects",
            "experience",
            "education",
            "contact",
            "skills",
            "behavioral",
        ]
        for intent in priority_intents:
            if any(keyword in text for keyword in self.intents[intent]):
                self.last_confidence = 0.9
                return intent

        if tokens.intersection({"hello", "hi", "hey", "greetings"}):
            self.last_confidence = 0.88
            return "greeting"

        if any(keyword in text for keyword in self.intents["about"]):
            self.last_confidence = 0.86
            return "about"

        if self.nlp:
            doc = self.nlp(text)
            best_intent = None
            highest_score = 0.0

            if len(self.nlp.vocab.vectors) > 0:
                for intent, vector in self.intent_vectors.items():
                    score = doc.similarity(vector)
                    if score > highest_score:
                        highest_score = score
                        best_intent = intent

                if highest_score > 0.55:
                    self.last_confidence = round(highest_score, 2)
                    return best_intent

        for intent, keywords in self.intents.items():
            if intent == "greeting" and tokens.intersection({"hello", "hi", "hey", "greetings"}):
                self.last_confidence = 0.78
                return intent
            if intent != "greeting" and any(keyword in text for keyword in keywords):
                self.last_confidence = 0.74
                return intent

        self.last_confidence = 0.0
        return None

    def get_personal_info(self):
        return self.data.get("personal_info", {})

    def get_skills(self):
        return self.data.get("skills", {})

    def get_first_item(self, section):
        items = self.data.get(section, [])
        return items[0] if items else {}

    def is_public_link(self, url):
        if not url:
            return False

        placeholder_parts = ["yourprofile", "yourusername", "yourportfolio", "project1", "project2"]
        return not any(part in url.lower() for part in placeholder_parts)

    def get_public_links(self):
        personal_info = self.get_personal_info()
        links = []

        for label in ["portfolio", "github", "linkedin"]:
            url = personal_info.get(label)
            if self.is_public_link(url):
                links.append({"label": label.title(), "url": url})

        resume_url = personal_info.get("resume")
        if self.is_public_link(resume_url):
            links.append({"label": "Resume", "url": resume_url})

        return links

    def get_suggestions(self, intent):
        suggestions = {
            "about": [
                "What are your strongest technical skills?",
                "Tell me about your internship experience",
                "Show me your projects",
            ],
            "skills": [
                "What did you build with Django?",
                "How have you used Python?",
                "Tell me about your tools and libraries",
            ],
            "experience": [
                "What achievements are you proud of?",
                "How did you solve a difficult problem?",
                "What did you automate?",
            ],
            "projects": [
                "Tell me about Campus VibeMarket",
                "Tell me about CodeGenius Engineers Website",
                "What technologies did you use?",
            ],
            "achievements": [
                "Tell me about your internship experience",
                "How did you solve a difficult problem?",
                "What did you build with Django?",
            ],
            "contact": [
                "Show me your projects",
                "Tell me about yourself",
                "What are your skills?",
            ],
            "fallback": [
                "Tell me about yourself",
                "Show me your projects",
                "How can I contact you?",
            ],
        }

        return suggestions.get(intent, suggestions["fallback"])

    def get_profile_metrics(self):
        skills = self.get_skills()
        return {
            "languages": len(skills.get("programming_languages", [])),
            "projects": len(self.data.get("projects", [])),
            "experience_items": len(self.data.get("experience", [])),
        }

    def format_projects(self, query=""):
        projects = self.data.get("projects", [])
        if not projects:
            return "I do not have project details available yet."

        filtered_projects = [
            project for project in projects
            if project.get("name", "").lower() in query.lower()
            or any(tech.lower() in query.lower() for tech in project.get("technologies", []))
        ]
        selected_projects = filtered_projects or projects

        project_summaries = []
        for project in selected_projects[:3]:
            name = project.get("name", "Project")
            description = project.get("description", "a software project")
            technologies = ", ".join(project.get("technologies", [])) or "various technologies"
            link = project.get("link")
            summary = f"**{name}**\n{description}\nStack: {technologies}."
            if project.get("role"):
                summary += f"\nRole: {project['role']}"
            if project.get("impact"):
                summary += f"\nImpact: {project['impact']}"
            if project.get("challenge"):
                summary += f"\nChallenge: {project['challenge']}"
            if project.get("features"):
                summary += "\nFeatures:\n" + "\n".join(f"- {feature}" for feature in project["features"])
            if link:
                summary += f"\nLink: {link}"
            project_summaries.append(summary)

        return "\n".join(project_summaries)

    def format_achievements(self):
        achievements = []
        for role in self.data.get("experience", []):
            company = role.get("company", "the organization")
            for achievement in role.get("achievements", []):
                achievements.append(f"- {achievement} ({company})")

        if not achievements:
            return "I do not have achievements listed yet."

        return "**Key achievements:**\n" + "\n".join(achievements)

    def get_response(self, user_input):
        if not user_input or not user_input.strip():
            return "Please ask me something about my skills, projects, experience, or education."

        intent = self.get_intent(user_input)
        text = user_input.lower()

        if not intent and self.context["last_intent"]:
            if any(word in text for word in ["more", "tell me", "detail"]):
                intent = self.context["last_intent"]

        if not intent:
            return "I'm not sure I understand. Try asking about my **Skills**, **Projects**, or **Education**."

        self.context["last_intent"] = intent
        personal_info = self.get_personal_info()

        if intent == "greeting":
            name = personal_info.get("name", "Takudzwa")
            return f"Hello! I am {name}'s AI assistant. Ask me about internship experience, Python skills, education, or projects."

        if intent == "about":
            name = personal_info.get("name", "Takudzwa")
            title = personal_info.get("title", "Software Developer")
            location = personal_info.get("location", "Zimbabwe")
            return f"**{name}** is a {title} based in {location}, with interests in backend development, NLP, mobile apps, and practical software systems."

        if intent == "skills":
            skills = self.get_skills()
            langs = ", ".join(skills.get("programming_languages", [])) or "Python and JavaScript"
            frameworks = ", ".join(skills.get("frameworks", [])) or "Flask, Django, React, and Flutter"
            tools = ", ".join(skills.get("tools", []))
            libraries = ", ".join(skills.get("libraries", []))
            response = f"**Technical skills**\nLanguages: {langs}\nFrameworks: {frameworks}"
            if libraries:
                response += f"\nLibraries: {libraries}"
            if tools:
                response += f"\nTools: {tools}"
            return response

        if intent == "experience":
            role = self.get_first_item("experience")
            if not role:
                return "I do not have experience details available yet."
            achievements = role.get("achievements", [])
            response = f"**{role.get('role', 'ICT Intern')}** at **{role.get('company', 'OK Zimbabwe Limited')}**\nDuration: {role.get('duration', 'Not specified')}\n{role.get('description', '')}"
            if achievements:
                response += "\nHighlights:\n" + "\n".join(f"- {achievement}" for achievement in achievements)
            return response

        if intent == "projects":
            return self.format_projects(user_input)

        if intent == "achievements":
            return self.format_achievements()

        if intent == "education":
            edu = self.get_first_item("education")
            if not edu:
                return "I do not have education details available yet."
            return f"I am studying for a **{edu.get('degree', 'degree')}** at **{edu.get('institution', 'university')}**, expected to graduate in {edu.get('year', 'the near future')}."

        if intent == "contact":
            email = personal_info.get("email", "No email listed")
            linkedin = personal_info.get("linkedin")
            github = personal_info.get("github")
            links = [f"You can email me at **{email}**."]
            if linkedin:
                links.append(f"LinkedIn: {linkedin}")
            if github:
                links.append(f"GitHub: {github}")
            return "\n".join(links)

        if intent == "behavioral":
            stories = self.data.get("behavioral_responses", [])
            for story in stories:
                if any(tag in text for tag in story.get("tags", [])):
                    return f"**Situation:** {story.get('response', '')}"
            if stories:
                return f"**Example:** {stories[0].get('response', '')}"
            return "I do not have behavioral examples available yet."

        if intent == "technical":
            deep_dives = self.data.get("technical_deep_dives", {})
            for tech, deep_dive in deep_dives.items():
                if tech in text:
                    return f"**{tech.title()} Experience:** {deep_dive}"
            return "I can discuss my technical depth in Python, Django, React, or Flutter. Which one interests you?"

        return "I'm not sure I understand. Try asking about my **Skills**, **Projects**, or **Education**."

    def get_answer(self, user_input):
        response = self.get_response(user_input)
        intent = self.context.get("last_intent") or "fallback"

        if response.startswith("I'm not sure") or response.startswith("Please ask"):
            intent = "fallback"

        return {
            "response": response,
            "intent": intent,
            "confidence": self.last_confidence,
            "suggestions": self.get_suggestions(intent),
            "links": self.get_public_links() if intent in {"about", "contact", "projects"} else [],
        }
