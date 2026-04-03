CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Sources to monitor
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- e.g., 'hackernews', 'reddit', 'github'
    url_pattern TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw community posts pulled by the Collector Agent
CREATE TABLE raw_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id),
    external_id VARCHAR(255),
    title TEXT,
    content TEXT,
    url TEXT,
    score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Identified trends grouped by the Analyzer Agent
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    rank_score FLOAT,
    status VARCHAR(50) DEFAULT 'detected', -- 'detected', 'analyzing', 'article_generated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Join table for trends and posts
CREATE TABLE trend_posts (
    trend_id UUID REFERENCES trends(id),
    post_id UUID REFERENCES raw_posts(id),
    PRIMARY KEY (trend_id, post_id)
);

-- Generated articles by the Journalist Agent
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trend_id UUID REFERENCES trends(id),
    title VARCHAR(255) NOT NULL,
    subtitle TEXT,
    content TEXT, -- Generated Markdown
    summary TEXT,
    category VARCHAR(100),
    ai_model VARCHAR(100),
    confidence_score FLOAT,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'published'
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Init mock source
INSERT INTO sources (name, type, url_pattern) VALUES ('Hacker News', 'hackernews', 'https://news.ycombinator.com/item?id=');
