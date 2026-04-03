# 📰 The AI Chronicle

**The AI Chronicle** is a fully autonomous, AI-powered digital newspaper. It continuously monitors developer hubs like Hacker News and Reddit, leverages LLMs to synthesize community consensus, and publishes professional, multi-lingual articles wrapped in a high-end editorial Next.js UI.

---

## ✨ Key Features
- **Autonomous Crawler:** Built-in Python spider that directly fetches real-time `.json` APIs from Hacker News and Reddit, automatically storing historical raw signals.
- **AI Journalist & Translator Pipeline:** Uses Google's **Gemini 1.5 Pro & Flash** models to extract insights from raw discussions, generate journalistic English news, and simultaneously translate it into **Korean, Chinese, Spanish, and Japanese**.
- **High-Performance Backend:** Written in **Go** utilizing `go-chi` and `pgxpool` to rapidly serve news content and interface seamlessly with a PostgreSQL relational database.
- **NYT-Style Next.js Frontend:** A minimalist, aesthetic front-page built on Next.js 14/15 App Router featuring built-in internationalized (`/[lang]`) routes.

## 🏗️ Architecture Stack
- **Frontend**: Next.js (App Router), React, Tailwind CSS, TypeScript
- **Backend API**: Go (Golang), `go-chi`, `pgxpool`
- **AI Agents**: Python, Google Generative AI (`gemini-1.5-pro/flash`), `requests`, `psycopg2`
- **Database**: PostgreSQL (via Docker)
- **Cache**: Redis

---

## 🚀 Getting Started

### Prerequisites
1. **Docker & Docker Compose** (For PostgreSQL & Redis)
2. **Go** (Version 1.20+)
3. **Node.js** (`v20.9.0` or higher required for Next.js 14+)
4. **Python** (Version 3.10+)
5. **Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/)

### 1. Environment Setup
Copy the configuration template and insert your API key:
```bash
cp .env.example .env
```

### 2. Database Initialization
Spin up the database using Docker and apply the schemas:
```bash
# Start Postgres & Redis
docker compose up -d

# Notice: You must run the SQL schema files to initialize your tables.
# Attach to your local postgres and run:
# \i db/migrations/01_init.sql
# \i db/migrations/02_translations.sql 
```

### 3. Run the Go API Backend
```bash
cd backend
go mod tidy
go run cmd/server/main.go
# Server starts on http://localhost:8080
```

### 4. Run the Next.js Frontend
Open a new terminal session.
```bash
cd frontend
npm install
npm run dev
# Frontend starts on http://localhost:3000
```

### 5. Start the AI Data Pipeline
Open a new terminal session. This will collect data from Reddit/Hacker News and generate the Multi-lingual AI articles.
```bash
# Create a virtual environment and install requirements
cd agents
python -m venv venv
source venv/bin/activate  # (On Windows, `venv\Scripts\activate`)
pip install -r requirements.txt

# Step 1: Gather raw internet discussions
python crawler.py

# Step 2: Analyze, write, and translate the news
python workflow.py
```

---

## 🌎 Supported Languages
The frontend allows seamless language switching directly from the top navigation bar. Currently supported URLs:
- `/en` — English (Default)
- `/ko` — Korean (한국어)
- `/zh` — Chinese (中文)
- `/es` — Spanish (Español)
- `/ja` — Japanese (日本語)

## 📜 License
This project is licensed under the MIT License.
