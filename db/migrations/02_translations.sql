-- Enable translations for articles
CREATE TABLE article_translations (
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL, -- e.g., 'ko', 'zh', 'es', 'ja'
    title VARCHAR(255) NOT NULL,
    subtitle TEXT,
    content TEXT,
    summary TEXT,
    PRIMARY KEY (article_id, language_code)
);
