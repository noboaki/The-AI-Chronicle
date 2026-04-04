import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # Load variables from .env file

api_key = os.getenv("GEMINI_API_KEY", "your-api-key")
genai.configure(api_key=api_key)

class TrendAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def detect_trends(self, raw_posts):
        prompt = "Analyze the following community posts and group them into 3 trending topics:\\n"
        for post in raw_posts:
            prompt += f"- {post['title']}: {post['content']}\\n"

        response = self.model.generate_content(prompt)
        return response.text

class JournalistAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def generate_article(self, trend_title, community_discussions):
        prompt = f"""
        Act as an objective, professional NYT tech journalist.
        Write an article in ENGLISH covering the trending topic: '{trend_title}'.
        Requirements: Headline, Short Subtitle, 1-paragraph summary, Main body.
        Discussions: {community_discussions}
        """
        response = self.model.generate_content(prompt)
        return response.text

class TranslatorAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
    def translate_article(self, english_article, target_language):
        prompt = f"""
        Translate the following news article into {target_language}.
        Preserve the markdown formatting, the journalistic tone, and structure.
        
        Article:
        {english_article}
        """
        response = self.model.generate_content(prompt)
        return response.text

import psycopg2
import psycopg2.extras

DB_URL = os.getenv("DATABASE_URL", "postgresql://chronicle:password@localhost:5432/chronicle_db")

def fetch_raw_posts(limit=10):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Fetch fresh posts that haven't been processed yet
        cur.execute("SELECT title, content, score, url FROM raw_posts ORDER BY created_at DESC LIMIT %s", (limit,))
        posts = [dict(row) for row in cur.fetchall()]
        conn.close()
        return posts
    except psycopg2.Error as e:
        print("DB Error:", e)
        return []

if __name__ == "__main__":
    forums = fetch_raw_posts(limit=15)
    
    if not forums:
        print("No raw posts found in database. Please run crawler.py first.")
        exit()
    
    analyzer = TrendAnalyzer()
    print("Detecting trends...")
    print(analyzer.detect_trends(forums))
    
    journalist = JournalistAgent()
    print("\\nGenerating English Article...")
    en_article = journalist.generate_article("OpenAI o1-mini release", str(forums))
    print(en_article)
    
    translator = TranslatorAgent()
    languages = ['Korean (ko)', 'Chinese (zh)', 'Spanish (es)', 'Japanese (ja)']
    
    print("\\nGenerating Translations...")
    for lang in languages:
        print(f"\\n--- Translating to {lang} ---")
        translated = translator.translate_article(en_article, lang)
        print(translated[:150] + "...") # Print snippet
