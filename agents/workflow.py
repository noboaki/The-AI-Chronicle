import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # Load variables from .env file

api_key = os.getenv("GEMINI_API_KEY", "your-api-key")
genai.configure(api_key=api_key)

class TrendAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-flash-latest")

    def detect_trends(self, raw_posts):
        prompt = "Analyze the following community posts and group them into 3 trending topics:\\n"
        for post in raw_posts:
            prompt += f"- {post['title']}: {post['content']}\\n"

        response = self.model.generate_content(prompt)
        return response.text

class JournalistAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-flash-latest")

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
        self.model = genai.GenerativeModel("gemini-flash-latest")
        
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

def save_db(en_article, translated_dict):
    conn = psycopg2.connect(DB_URL)
    
    # Extract title from the first line of markdown
    title = en_article.split("\\n")[0].replace("#", "").strip()
    if not title:
        title = "Trending AI News"

    try:
        with conn.cursor() as cur:
            # Save English article
            cur.execute("""
                INSERT INTO articles (title, content, category, ai_model, status, published_at)
                VALUES (%s, %s, %s, %s, 'published', CURRENT_TIMESTAMP)
                RETURNING id
            """, (title, en_article, "Development", "gemini-flash-latest"))
            
            article_id = cur.fetchone()[0]
            
            # Save translations
            for lang_code, text in translated_dict.items():
                trans_title = text.split("\\n")[0].replace("#", "").strip()
                if not trans_title:
                    trans_title = title
                    
                cur.execute("""
                    INSERT INTO article_translations (article_id, language_code, title, content)
                    VALUES (%s, %s, %s, %s)
                """, (article_id, lang_code, trans_title, text))
                
            conn.commit()
            print(f"\\nArticle '{title}' and translations saved to DB! (ID: {article_id})")
    except psycopg2.Error as e:
        print("Failed to save to DB:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    forums = fetch_raw_posts(limit=15)
    
    if not forums:
        print("No raw posts found in database. Please run crawler.py first.")
        exit()
    
    analyzer = TrendAnalyzer()
    print("Detecting trends...")
    
    journalist = JournalistAgent()
    print("\\nGenerating English Article...")
    time.sleep(12) # Delay to avoid hitting 5 RPM free tier limit
    en_article = journalist.generate_article("AI Community Trends", str(forums))
    print(en_article)
    
    translator = TranslatorAgent()
    languages = [('ko', 'Korean'), ('zh', 'Chinese'), ('es', 'Spanish'), ('ja', 'Japanese')]
    
    print("\\nGenerating Translations...")
    translations = {}
    for code, lang in languages:
        print(f"\\n--- Translating to {lang} ---")
        time.sleep(15) # Stay under 5 RPM limit
        try:
            translated = translator.translate_article(en_article, lang)
            print(translated[:150] + "...") # Print snippet
        except Exception as e:
            print(f"Translation to {lang} failed (Daily quota likely exceeded). Using fallback text.")
            first_line = en_article.split('\\n')[0].replace('#', '').strip()
            translated = f"# {first_line}\\n\\n번역이 지연 중입니다 (API 일일 사용량 초과)."
            
        translations[code] = translated
        
    save_db(en_article, translations)
