import json
import os
import re

import spacy


class AdvancedPersonalAssistant:
    def __init__(self):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(backend_dir, "data.json")

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
            "behavioral": [
                "challenge",
                "difficult",
                "problem",
                "solve",
                "mistake",
                "leadership",
                "teamwork",
                "conflict",
                "proud",
            ],
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
        for project in selected_projects[:2]:
            name = project.get("name", "Project")
            description = project.get("description", "software project").rstrip(".").lower()
            article = "an" if description.startswith(("a", "e", "i", "o", "u")) else "a"
            technologies = ", ".join(project.get("technologies", [])) or "various technologies"
            link = project.get("link")
            role = project.get("role")
            summary = f"**{name}**\n{name} is {article} {description}. "
            if role:
                summary += f"I worked on it as the {role.lower()}, "
            else:
                summary += "I built it "
            summary += f"using **{technologies}**."

            if project.get("impact"):
                impact = project["impact"].rstrip(".")
                if impact.lower().startswith("designed "):
                    summary += f"\n\nThe project was {impact.lower()}."
                else:
                    summary += f"\n\nThe project {impact[0].lower() + impact[1:]}."

            if project.get("features"):
                summary += "\n\nSome of the key parts I worked on were:\n" + "\n".join(
                    f"- {feature}" for feature in project["features"][:3]
                )
            if link and self.is_public_link(link):
                summary += f"\n\nYou can view the project here: {link}"
            project_summaries.append(summary)

        if len(project_summaries) == 1:
            return project_summaries[0]

        return "Here are two projects that show the kind of work I enjoy:\n\n" + "\n\n".join(project_summaries)

    def format_achievements(self):
        achievements = []
        for role in self.data.get("experience", []):
            company = role.get("company", "the organization")
            for achievement in role.get("achievements", []):
                achievements.append(f"- {achievement} ({company})")

        if not achievements:
            return "I do not have achievements listed yet."

        return "A couple of achievements I am especially proud of are:\n\n" + "\n".join(achievements)

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
            return (
                f"I'm **{name}**, a {title} based in {location}. "
                "I enjoy turning practical problems into useful software, especially through "
                "backend development, mobile apps, and intelligent systems."
            )

        if intent == "skills":
            skills = self.get_skills()
            languages = [
                language.title() if language.upper() == "JAVA" else language
                for language in skills.get("programming_languages", [])
                if language.lower() != "python"
            ]
            langs = ", ".join(languages) or "JavaScript and SQL"
            frameworks = ", ".join(skills.get("frameworks", [])) or "Flask, Django, React, and Flutter"
            tools = ", ".join(skills.get("tools", []))
            libraries = ", ".join(skills.get("libraries", []))
            response = (
                f"My strongest language is **Python**, and I also work with {langs}. "
                f"For application development, I use **{frameworks}** depending on whether "
                "the project is web, backend, or mobile."
            )
            if libraries:
                response += f"\n\nI have also used {libraries} for data and machine-learning work."
            if tools:
                response += f" My regular development tools include {tools}."
            return response

        if intent == "experience":
            role = self.get_first_item("experience")
            if not role:
                return "I do not have experience details available yet."
            achievements = role.get("achievements", [])
            description = role.get("description", "").strip()
            if description.lower().startswith("worked "):
                description = f"I {description[0].lower() + description[1:]}"
            response = (
                f"I worked as an **{role.get('role', 'ICT Intern')}** at "
                f"**{role.get('company', 'OK Zimbabwe Limited')}** from "
                f"{role.get('duration', 'the listed period')}. "
                f"During that time, {description}"
            )
            if achievements:
                response += "\n\nTwo highlights from that experience were:\n" + "\n".join(
                    f"- {achievement}" for achievement in achievements
                )
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
            phone_numbers = personal_info.get("phone_numbers", [])
            linkedin = personal_info.get("linkedin")
            github = personal_info.get("github")
            links = [f"You can email me at **{email}**."]
            if phone_numbers:
                links.append(f"You can also call me on **{' or '.join(phone_numbers)}**.")
            if self.is_public_link(linkedin):
                links.append(f"You can also find me on LinkedIn: {linkedin}")
            if self.is_public_link(github):
                links.append(f"My code is available on GitHub: {github}")
            return "\n\n".join(links)

        if intent == "behavioral":
            stories = self.data.get("behavioral_responses", [])
            for story in stories:
                if any(tag in text for tag in story.get("tags", [])):
                    return f"Here is one example: {story.get('response', '')}"
            if stories:
                return f"Here is one example: {stories[0].get('response', '')}"
            return "I do not have behavioral examples available yet."

        if intent == "technical":
            deep_dives = self.data.get("technical_deep_dives", {})
            for tech, deep_dive in deep_dives.items():
                if tech in text:
                    return f"When it comes to **{tech.title()}**, {deep_dive[0].lower() + deep_dive[1:]}"
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
