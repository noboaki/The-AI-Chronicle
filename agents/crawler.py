import os
import requests
import psycopg2

DB_URL = os.getenv("DATABASE_URL", "postgresql://chronicle:password@localhost:5432/chronicle_db")

def get_or_create_source(conn, name, type_val, url_pattern):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM sources WHERE name = %s", (name,))
        res = cur.fetchone()
        if res:
            return res[0]
        
        cur.execute(
            "INSERT INTO sources (name, type, url_pattern) VALUES (%s, %s, %s) RETURNING id",
            (name, type_val, url_pattern)
        )
        conn.commit()
        return cur.fetchone()[0]

def scrape_hackernews(conn, source_id, limit=10):
    print("Scraping Hacker News...")
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        story_ids = requests.get(top_stories_url).json()[:limit]
    except Exception as e:
        print("Error fetching HN:", e)
        return

    with conn.cursor() as cur:
        for sid in story_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
            if not story or "title" not in story:
                continue

            cur.execute("SELECT id FROM raw_posts WHERE source_id = %s AND external_id = %s", (source_id, str(story["id"])))
            if cur.fetchone():
                continue

            titletxt = story.get("title", "")
            content = story.get("text", "") # Comments/Text
            url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
            score = story.get("score", 0)

            cur.execute("""
                INSERT INTO raw_posts (source_id, external_id, title, content, url, score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (source_id, str(story["id"]), titletxt, content, url, score))
        conn.commit()
    print("HN Scrape complete.")

def scrape_reddit(conn, source_id, subreddit="LocalLLaMA", limit=10):
    print(f"Scraping r/{subreddit}...")
    headers = {"User-Agent": "AIChronicleBot/1.0"}
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    try:
        res = requests.get(url, headers=headers).json()
    except Exception as e:
        print("Error fetching Reddit:", e)
        return
    
    if "data" not in res:
        print("Failed or Rate Limited by Reddit:", res)
        return

    with conn.cursor() as cur:
        for child in res["data"].get("children", []):
            post = child["data"]
            pid = post["id"]
            
            cur.execute("SELECT id FROM raw_posts WHERE source_id = %s AND external_id = %s", (source_id, pid))
            if cur.fetchone():
                continue
                
            titletxt = post.get("title", "")
            content = post.get("selftext", "")
            p_url = "https://reddit.com" + post.get("permalink", "")
            score = post.get("score", 0)

            cur.execute("""
                INSERT INTO raw_posts (source_id, external_id, title, content, url, score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (source_id, pid, titletxt, content, p_url, score))
        conn.commit()
    print("Reddit Scrape complete.")

if __name__ == "__main__":
    try:
        conn = psycopg2.connect(DB_URL)
        print("Connected to Database")
        
        hn_id = get_or_create_source(conn, "Hacker News", "hackernews", "https://news.ycombinator.com/item?id=")
        reddit_id = get_or_create_source(conn, "r/LocalLLaMA", "reddit", "https://reddit.com")
        
        scrape_hackernews(conn, hn_id, limit=20)
        scrape_reddit(conn, reddit_id, limit=20)
        
        conn.close()
    except psycopg2.Error as e:
        print("DB Error:", e)
