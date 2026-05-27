import json
import random
import os
import spacy

class AdvancedPersonalAssistant:
    def __init__(self):
        # path to data.json (assuming it's in the root folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_file = os.path.join(base_dir, "data.json")
        
        self.load_data(data_file)
        self.nlp = self.load_nlp_model()
        self.context = {'last_intent': None}
        self.setup_knowledge_base()

    def load_data(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print("✅ Data loaded successfully")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.data = {}

    def load_nlp_model(self):
        try:
            print("⏳ Loading NLP model...")
            # Tries to load the medium model (vectors)
            return spacy.load("en_core_web_md")
        except:
            print("⚠️  'en_core_web_md' not found. using 'sm' (keyword fallback).")
            try:
                return spacy.load("en_core_web_sm")
            except:
                return None

    def setup_knowledge_base(self):
        # Define keywords for intents
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'skills': ['skills', 'technologies', 'stack', 'programming', 'languages'],
            'experience': ['experience', 'work', 'job', 'internship', 'career', 'ok zimbabwe'],
            'education': ['education', 'degree', 'university', 'college', 'school', 'msu'],
            'projects': ['projects', 'portfolio', 'apps', 'github', 'website'],
            'contact': ['contact', 'email', 'linkedin', 'reach', 'phone'],
            'behavioral': ['challenge', 'mistake', 'leadership', 'teamwork', 'conflict', 'proud'],
            'technical': ['architecture', 'coding style', 'deep dive', 'specifics']
        }
        
        # Pre-compute vectors if model exists and has vectors loaded
        self.intent_vectors = {}
        # FIX: Check length of vectors vocab instead of attribute
        if self.nlp and len(self.nlp.vocab.vectors) > 0:
            for intent, keywords in self.intents.items():
                self.intent_vectors[intent] = self.nlp(" ".join(keywords))

    def get_intent(self, user_input):
        if not self.nlp: return 'fallback'
        
        doc = self.nlp(user_input.lower())
        
        # 1. Check for specific tech keywords (Override)
        text = user_input.lower()
        if any(t in text for t in ['python', 'django', 'flutter', 'react']):
            return 'technical'

        # 2. Vector Similarity
        best_intent = None
        highest_score = 0.0
        
        # FIX: Check if vectors are available before computing similarity
        if len(self.nlp.vocab.vectors) > 0:
            for intent, vector in self.intent_vectors.items():
                score = doc.similarity(vector)
                if score > highest_score:
                    highest_score = score
                    best_intent = intent
            
            if highest_score > 0.55:
                return best_intent

        # 3. Keyword Fallback
        for intent, keywords in self.intents.items():
            if any(k in text for k in keywords):
                return intent
                
        return None

    def get_response(self, user_input):
        intent = self.get_intent(user_input)
        
        # Context handling (Follow-ups)
        if not intent and self.context['last_intent']:
            if any(w in user_input.lower() for w in ['more', 'tell me', 'detail']):
                intent = self.context['last_intent']

        if intent:
            self.context['last_intent'] = intent
            
            if intent == 'greeting':
                return f"Hello! I am {self.data['personal_info']['name']}'s AI Assistant. Ask me about my Internship, Python Skills, or Projects."
            
            if intent == 'skills':
                langs = ", ".join(self.data['skills']['programming_languages'])
                frames = ", ".join(self.data['skills']['frameworks'])
                return f"I am proficient in **{langs}**. My framework focus includes **{frames}**."
                
            if intent == 'experience':
                role = self.data['experience'][0]
                return f"I am currently an **{role['role']}** at **{role['company']}**. {role['description']}"
                
            if intent == 'projects':
                proj = self.data['projects'][0]
                return f"I developed **{proj['name']}**, which is a {proj['description']} Built with {', '.join(proj['technologies'])}."
                
            if intent == 'education':
                edu = self.data['education'][0]
                return f"I am studying for a **{edu['degree']}** at **{edu['institution']}**, expected to graduate in {edu['year']}."
                
            if intent == 'contact':
                return f"You can email me at **{self.data['personal_info']['email']}**."
                
            if intent == 'behavioral':
                # Find matching story or random one
                for story in self.data['behavioral_responses']:
                    if any(tag in user_input.lower() for tag in story['tags']):
                        return f"**Situation:** {story['response']}"
                return f"**Example:** {self.data['behavioral_responses'][0]['response']}"

            if intent == 'technical':
                # Check for specific tech explanation
                for tech, deep_dive in self.data['technical_deep_dives'].items():
                    if tech in user_input.lower():
                        return f"**{tech.title()} Experience:** {deep_dive}"
                return "I can discuss my technical depth in Python, Django, or Flutter. Which one interests you?"

        return "I'm not sure I understand. Try asking about my **Skills**, **Projects**, or **Education**."