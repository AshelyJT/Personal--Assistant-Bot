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
            "skills": ["skills", "technologies", "stack", "programming", "languages", "tools", "networking", "support"],
            "experience": [
                "experience",
                "work",
                "job",
                "internship",
                "attachment",
                "career",
                "ok zimbabwe",
                "midlands state university",
                "msu",
                "student on employment",
                "it department",
                "technical support",
                "hardware",
                "troubleshooting",
                "networking support",
                "networking",
            ],
            "education": ["education", "degree", "graduate", "graduation", "university", "college", "school", "msu"],
            "projects": ["projects", "portfolio", "apps", "website", "smartshelf", "chatbot", "asset management", "asset tracking", "creatificant", "codegenius"],
            "certifications": ["certification", "certifications", "certificate", "certificates", "credential", "credentials"],
            "opportunities": ["opportunity", "opportunities", "available", "availability", "role", "roles", "hire"],
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

        if "codegenius" in text and any(
            phrase in text
            for phrase in [
                "part of",
                "member",
                "employed",
                "work for",
                "work with",
                "worked with",
                "your role",
                "what did you do",
                "contribute",
                "collaborat",
                "affiliation",
                "relationship",
            ]
        ):
            self.last_confidence = 0.95
            return "about"

        if any(t in text for t in ["python", "django", "java", "c++", "cloud", "cybersecurity", "iot", "mqtt", "esp32"]):
            self.last_confidence = 0.92
            return "technical"

        priority_intents = [
            "achievements",
            "projects",
            "experience",
            "opportunities",
            "education",
            "certifications",
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
                "Summarize MSU IT experience",
                "Show technical support experience",
                "Show networking experience",
            ],
            "projects": [
                "Tell me about SmartShelf AI",
                "Tell me about the AI Personal Assistant Chatbot",
                "Tell me about Creatificant",
            ],
            "certifications": [
                "What cloud skills do you have?",
                "What are your AI and data skills?",
                "What software development skills do you have?",
            ],
            "opportunities": [
                "What are your strongest technical skills?",
                "Tell me about your internship experience",
                "How can I contact you?",
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
            "languages": len(skills.get("Programming", [])),
            "projects": len(self.data.get("projects", [])),
            "experience_items": len(self.data.get("experience", [])),
        }

    def format_skills(self):
        skills = self.get_skills()
        if not skills:
            return "I do not have skill details available yet."

        sections = []
        for category, items in skills.items():
            if items:
                sections.append(f"- **{category}:** {', '.join(items)}")

        return (
            "My technical skills cover software, infrastructure, and intelligent systems:\n\n"
            + "\n".join(sections)
        )

    def format_certifications(self):
        certifications = self.data.get("certifications", {})
        if not certifications:
            return "I do not have certification details available yet."

        groups = [
            f"- **{category}:** {', '.join(items)}"
            for category, items in certifications.items()
            if items
        ]
        return (
            "My certifications and professional learning show continued growth across AI, "
            "data, software development, cloud, DevOps, networking, and database systems:\n\n"
            + "\n".join(groups)
            + "\n\nCertificate files are available on request."
        )

    def format_codegenius_collaboration(self):
        collaborations = self.data.get("collaborations", [])
        collaboration = next(
            (
                item for item in collaborations
                if "codegenius" in item.get("organization", "").lower()
            ),
            {},
        )
        if not collaboration:
            return "I do not have CodeGenius Engineers Group details available yet."

        response = (
            f"I contribute to collaborative software projects with "
            f"**{collaboration.get('organization', 'CodeGenius Engineers Group')}** "
            f"as a **{collaboration.get('role', 'Project Contributor')}**.\n\n"
            f"**Relationship:** {collaboration.get('relationship', 'Project-based collaboration')}.\n\n"
            f"{collaboration.get('description', '')}"
        )

        responsibilities = collaboration.get("responsibilities", [])
        if responsibilities:
            response += "\n\nMy contributions include:\n" + "\n".join(
                f"- {responsibility}" for responsibility in responsibilities
            )

        technologies = collaboration.get("technologies", [])
        if technologies:
            response += f"\n\n**Technologies:** {', '.join(technologies)}."

        link = collaboration.get("link")
        if self.is_public_link(link):
            response += f"\n\nView the website: {link}"

        availability = collaboration.get("availability")
        if availability:
            response += f"\n\n**Availability:** {availability}."

        return response

    def format_projects(self, query=""):
        projects = self.data.get("projects", [])
        if not projects:
            return "I do not have project details available yet."

        filtered_projects = [
            project for project in projects
            if project.get("name", "").lower() in query.lower()
            or any(
                alias.lower() in query.lower()
                for alias in project.get("aliases", [])
            )
            or any(tech.lower() in query.lower() for tech in project.get("technologies", []))
        ]

        if not filtered_projects:
            project_overview = []
            for index, project in enumerate(projects, start=1):
                name = project.get("name", "Project")
                description = project.get("description", "Software project").rstrip(".")
                technologies = ", ".join(project.get("technologies", [])[:5])
                summary = f"**{index}. {name}**\n{description}."
                if technologies:
                    summary += f"\n\nBuilt with **{technologies}**."
                link = project.get("link")
                if link and self.is_public_link(link):
                    summary += f"\n\nView project: {link}"
                project_overview.append(summary)

            return (
                f"Here are all {len(project_overview)} projects in my portfolio:\n\n"
                + "\n\n".join(project_overview)
            )

        project_summaries = []
        for project in filtered_projects:
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

        return "\n\n".join(project_summaries)

    def format_achievements(self):
        achievements = []
        for role in self.data.get("experience", []):
            company = role.get("company", "the organization")
            for achievement in role.get("achievements", []):
                achievements.append(f"- {achievement} ({company})")

        if not achievements:
            return "I do not have achievements listed yet."

        return "A couple of achievements I am especially proud of are:\n\n" + "\n".join(achievements)

    def format_experience(self, query=""):
        roles = self.data.get("experience", [])
        if not roles:
            return "I do not have experience details available yet."

        text = query.lower()
        matching_roles = []
        explicit_msu_query = any(
            term in text
            for term in ["midlands", "msu", "student on employment", "university"]
        )
        explicit_ok_query = any(
            term in text
            for term in ["ok zimbabwe", "internship", "attachment", "industrial"]
        )
        support_query = any(
            term in text
            for term in ["hardware", "networking", "technical support", "troubleshooting"]
        )

        for role in roles:
            searchable = " ".join(
                [
                    role.get("company", ""),
                    role.get("role", ""),
                    role.get("description", ""),
                    " ".join(role.get("achievements", [])),
                ]
            ).lower()

            if explicit_msu_query:
                if any(term in searchable for term in ["midlands", "student on employment"]):
                    matching_roles.append(role)
                    continue

            if explicit_ok_query:
                if "ok zimbabwe" in searchable or "ict intern" in searchable:
                    matching_roles.append(role)
                    continue

            if support_query:
                if any(term in searchable for term in ["hardware", "networking", "technical support", "troubleshooting", "user support"]):
                    matching_roles.append(role)
                    continue

        selected_roles = matching_roles or roles
        summaries = []

        for role in selected_roles:
            summary = (
                f"**{role.get('role', 'ICT Experience')} - {role.get('company', 'Organization')}**\n"
                f"{role.get('duration', 'Listed period')}"
            )
            description = role.get("description", "").strip()
            if description:
                summary += f"\n\n{description}"
            achievements = role.get("achievements", [])
            if achievements:
                summary += "\n\nResponsibilities included:\n" + "\n".join(
                    f"- {achievement}" for achievement in achievements
                )
            summaries.append(summary)

        return "\n\n".join(summaries)

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
            return f"Hello! I am {name}'s AI assistant. Ask me about graduate opportunities, technical skills, certifications, experience, or projects."

        if intent == "about":
            name = personal_info.get("name", "Takudzwa")
            title = personal_info.get("title", "Computer Systems Engineering Graduate")
            location = personal_info.get("location", "Zimbabwe")
            summary = personal_info.get("summary", "")
            if "codegenius" in text:
                return self.format_codegenius_collaboration()
            return f"I'm **{name}**, a {title} based in {location}. {summary}"

        if intent == "skills":
            return self.format_skills()

        if intent == "experience":
            return self.format_experience(user_input)

        if intent == "projects":
            return self.format_projects(user_input)

        if intent == "achievements":
            return self.format_achievements()

        if intent == "certifications":
            return self.format_certifications()

        if intent == "opportunities":
            opportunities = personal_info.get("opportunities", [])
            role_list = ", ".join(opportunities) or "graduate technology roles"
            return (
                "I am currently open to career opportunities in "
                f"**{role_list}**. I am available to discuss roles based in Harare "
                "as well as suitable remote or hybrid opportunities."
            )

        if intent == "education":
            edu = self.get_first_item("education")
            if not edu:
                return "I do not have education details available yet."
            return (
                f"I am a graduate of **{edu.get('institution', 'university')}** with a "
                f"**{edu.get('degree', 'degree')}**, completed in {edu.get('year', '2026')}."
            )

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
            return "I can discuss my technical depth in Python, Django, cloud, cybersecurity, or IoT. Which one interests you?"

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
