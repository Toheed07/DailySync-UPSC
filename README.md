# Building an AI-Powered UPSC Learning Engine with FastAPI and Google Cloud

## Introduction | Overview

UPSC aspirants face the challenge of processing vast amounts of daily current affairs from multiple sources. Manually extracting relevant information, creating study materials, and generating practice questions is time-consuming and often inconsistent. This problem becomes more complex when you need to:

- Scrape content from multiple news sources daily
- Filter and prioritize content based on UPSC relevance
- Generate structured study materials (recall cards, mindmaps, practice questions)
- Store and retrieve content efficiently for later review

**Target Audience**: This blog is for developers with intermediate Python knowledge, basic understanding of REST APIs, and familiarity with cloud services. You should be comfortable with:
- Python 3.13+
- FastAPI framework basics
- Working with APIs and databases
- Docker containerization

**What You'll Accomplish**: By the end of this blog, you'll have built a complete AI-powered content generation system that:
- Automatically scrapes current affairs from multiple sources
- Uses Google Gemini AI to extract relevant sections and generate study materials
- Stores structured content in Google Cloud Firestore
- Provides a RESTful API for content retrieval
- Runs as a containerized microservice with background processing

## URLs

### Frontend
- **Live Application**: [https://dailysync-upsc.netlify.app/](https://dailysync-upsc.netlify.app/)

### Backend API
- **API Documentation**: [https://dailysync-upsc-416562352574.europe-west1.run.app/docs](https://dailysync-upsc-416562352574.europe-west1.run.app/docs)
- **API Base URL**: `https://dailysync-upsc-416562352574.europe-west1.run.app`


## Design

### Architecture Overview

The system follows a layered microservice architecture with clear separation of concerns:

```
Client → API Layer → Service Layer → Processing Layer → Data Layer
```

**Why This Design?**

1. **Layered Architecture**: Separates API endpoints, business logic, AI processing, and data storage. This makes the system maintainable, testable, and scalable.

2. **Background Processing**: Content generation is resource-intensive (AI calls, web scraping). Running it as background tasks prevents API timeouts and improves user experience.

3. **Retry Mechanism**: AI API calls and web scraping can fail due to network issues. A retry mechanism (3 attempts with 5-second delays) ensures reliability.

4. **Section Tracking**: All generated content (cards, mindmaps, PYQs) is linked to source sections via `section_index` and `section_title`. This maintains relationships and enables better content organization.

5. **Cloud-Native Storage**: Using Firestore provides:
   - Automatic scaling
   - Real-time synchronization capabilities
   - No server management
   - Built-in security

### Key Design Decisions

**FastAPI Framework**: Chosen for its async capabilities, automatic API documentation, and modern Python features. Perfect for handling concurrent requests.

**Google Gemini AI**: Selected for its cost-effectiveness, quality outputs, and ease of integration. The `gemini-2.0-flash-lite` model balances speed and quality.

**Firestore**: NoSQL database ideal for document-based content storage. Each date becomes a document, making queries simple and efficient.

**Docker Containerization**: Ensures consistent deployment across environments and simplifies cloud deployment.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              API LAYER (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ GET /content │  │ GET /dates   │  │ POST /generate│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              SERVICE LAYER                                   │
│  ┌────────────────────┐      ┌────────────────────┐         │
│  │ Content Service    │      │ Database Service   │         │
│  │ (Orchestration)    │─────▶│ (CRUD Operations)  │         │
│  │ Retry: 3x, 5s delay│      └────────────────────┘         │
│  └────────────────────┘                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│         PROCESSING LAYER                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Scraper  │→ │ Section  │→ │  Cards   │  │ Mindmap  │    │
│  │          │  │ Extractor│  │ Generator│  │ Generator│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                    │                         │
│                              ┌──────────┐                   │
│                              │ PYQ Gen   │                   │
│                              └──────────┘                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐                  ┌───────▼────────┐
│ Google Gemini  │                  │ Google Firestore│
│      AI        │                  │    Database     │
└────────────────┘                  └─────────────────┘
```

## Prerequisites

Before you begin, ensure you have the following installed and configured:

### Software Requirements

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Git** - [Install Git](https://git-scm.com/downloads)
- **Code Editor** - VS Code, PyCharm, or your preferred IDE

### Cloud Services & APIs

- **Google Cloud Account** - [Sign up for Google Cloud](https://cloud.google.com/)
- **Google Cloud Project** with Firestore enabled
- **Google Gemini API Key** - [Get API Key](https://makersuite.google.com/app/apikey)
- **Firestore Service Account JSON** - Download from Google Cloud Console

### Python Packages

The project uses these key libraries:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-cloud-firestore` - Firestore client
- `google-genai` - Gemini AI client
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests

### Assumed Knowledge

- Basic Python programming (functions, classes, error handling)
- Understanding of REST APIs (GET, POST requests)
- Familiarity with JSON data structures
- Basic command-line usage
- Understanding of environment variables

## Step-by-step Instructions

### Step 1: Project Setup

Create a new directory and set up the project structure:

```bash
mkdir daily-sync-upsc
cd daily-sync-upsc
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Create the following directory structure:

```
daily-sync-upsc/
├── api/
│   └── content.py
├── agents/
│   ├── analyse.py
│   ├── cards.py
│   ├── mindmap.py
│   └── pyq.py
├── config/
│   ├── ai.py
│   └── db.py
├── services/
│   ├── content.py
│   └── db_service.py
├── scrap/
│   └── scrap.py
├── prompts/
│   └── prompt.py
├── utils/
│   └── utils.py
├── data/
├── main.py
├── requirements.txt
├── Dockerfile
└── .env
```

### Step 2: Install Dependencies

Create `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
google-cloud-firestore==2.13.1
google-genai
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PROJECT_ID=your_gcp_project_id
PORT=8000
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

**Security Note**: Never commit `.env` files to version control. Add `.env` to your `.gitignore`.

### Step 4: Set Up Configuration Files

**config/ai.py** - Gemini AI Client:

```python
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
```

**config/db.py** - Firestore Client:

```python
from google.cloud import firestore
from dotenv import load_dotenv
import os

load_dotenv()

project_id = os.getenv("PROJECT_ID")
db = firestore.Client(project=project_id)
```

### Step 5: Implement the Scraper Module

**scrap/scrap.py** - Web scraping functionality:

```python
import requests
from bs4 import BeautifulSoup
import os

def get_project_root():
    """Get the project root directory."""
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))
    return project_root

def get_data_dir():
    """Get the absolute path to the data directory."""
    project_root = get_project_root()
    data_dir = os.path.join(project_root, "data")
    return data_dir

website_urls = {
    "drishti": "https://www.drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/",
    "indianexpress": "https://indianexpress.com/about/current-affairs/",
}

def scrape_article(url: str, output_file: str):
    """Scrape article content from a URL."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Extract title, content, etc. (simplified for brevity)
    # ... (full implementation in actual code)
    
    # Save to file
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    output_file_path = os.path.join(data_dir, output_file)
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_file_path

def scrape_all_articles(date: str):
    """Scrape articles from all sources for a given date."""
    articles = []
    for website, url in website_urls.items():
        output_file = scrape_article(
            url=url + date, 
            output_file=f"{date}_{website}.txt"
        )
        if output_file and os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            articles.append(content)
    
    return "\n".join(articles)
```

**Key Points**:
- Uses absolute paths for file operations (works in Docker)
- Handles errors gracefully
- Saves raw content to `/data` directory

### Step 6: Create AI Agents

**agents/analyse.py** - Section extraction:

```python
from config.ai import client
from google.genai import types
from prompts.prompt import default_prompt
from utils.utils import extract_json_block
import json

def extract_sections(article_text: str):
    """Extract UPSC-relevant sections from article."""
    prompt = f"""
    Analyze the following current affairs article and extract ONLY 
    the sections that are IMPORTANT for UPSC preparation.
    
    INPUT ARTICLE:
    {article_text}
    
    OUTPUT FORMAT (JSON ARRAY):
    [
      {{
        "title": "Section Title",
        "content": ["Point 1", "Point 2", ...],
        "importance": "absolutely_important"
      }}
    ]
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=default_prompt["analyse"]
        ),
        contents=prompt,
    )
    
    raw_text = response.text or ""
    json_payload = extract_json_block(raw_text)
    return json.loads(json_payload)
```

**agents/cards.py**, **agents/mindmap.py**, **agents/pyq.py** follow similar patterns, each calling Gemini AI with specific prompts.

### Step 7: Implement Service Layer

**services/content.py** - Content generation orchestration:

```python
import time
from scrap.scrap import scrape_all_articles
from agents.analyse import extract_sections
from agents.cards import create_cards
from agents.mindmap import create_mindmap
from agents.pyq import create_pyq
from services.db_service import save_daily_content

MAX_RETRIES = 3
RETRY_DELAY = 5

def generate_and_save_content(date: str):
    """Generate and save all content for a date."""
    for attempt in range(MAX_RETRIES):
        try:
            # Step 1: Scrape articles
            article = scrape_all_articles(date=date)
            
            # Step 2: Extract sections
            sections = extract_sections(article_text=article)
            
            if not sections:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
            
            # Step 3: Generate content for each section
            all_cards = []
            all_mindmaps = []
            all_pyqs = {"prelims": [], "mains": []}
            
            for section_index, section in enumerate(sections):
                section_content = section.get("content", [])
                section_text = "\n".join(section_content) if isinstance(section_content, list) else str(section_content)
                section_title = section.get("title", f"Section {section_index + 1}")
                
                # Generate cards with section tracking
                section_cards = create_cards(content=section_text)
                if isinstance(section_cards, list):
                    for card in section_cards:
                        if isinstance(card, dict):
                            card["section_index"] = section_index
                            card["section_title"] = section_title
                    all_cards.extend(section_cards)
                
                # Generate mindmap with section tracking
                mindmap = create_mindmap(content=section_text)
                if isinstance(mindmap, dict):
                    mindmap["section_index"] = section_index
                    mindmap["section_title"] = section_title
                all_mindmaps.append(mindmap)
                
                # Generate PYQ with section tracking
                pyq = create_pyq(content=section_text)
                if isinstance(pyq, dict):
                    # Add section tracking to prelims and mains
                    # ... (implementation details)
            
            # Step 4: Save to database
            success = save_daily_content(
                date=date,
                sections=sections,
                cards=all_cards,
                mindmap={"mindmaps": all_mindmaps},
                pyq=all_pyqs
            )
            
            if success:
                return {
                    "message": "Content generated and saved successfully",
                    "date": date,
                    "sections_count": len(sections),
                    "cards_count": len(all_cards),
                    # ... more stats
                }
            
        except Exception as e:
            print(f"Error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
    
    return None
```

**Key Features**:
- Retry mechanism for reliability
- Section tracking for all generated content
- Error handling and logging

### Step 8: Create API Endpoints

**api/content.py** - REST API:

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.db_service import get_daily_content, get_all_dates
from services.content import generate_and_save_content

router = APIRouter()

@router.get("/content/{date}")
async def get_content_by_date(date: str):
    """Fetch content for a specific date."""
    content = get_daily_content(date)
    if content is None:
        raise HTTPException(status_code=404, detail=f"No content found for date: {date}")
    return content

@router.get("/dates")
async def get_available_dates():
    """Get all available dates."""
    dates = get_all_dates()
    return {"dates": dates}

@router.post("/generate/{date}")
async def generate_and_save_content(date: str, background_tasks: BackgroundTasks):
    """Trigger background content generation."""
    background_tasks.add_task(generate_and_save_content, date=date)
    return {"message": f"Starting generation for date {date}"}
```

**main.py** - FastAPI application:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.content import router as content_router

app = FastAPI(title="DailySync UPSC", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content_router, prefix="/api", tags=["Content"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 9: Dockerize the Application

**Dockerfile**:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t daily-sync-upsc .
docker run -p 8000:8000 --env-file .env daily-sync-upsc
```

### Step 10: Test the API

Start the server:

```bash
uvicorn main:app --reload
```

Test endpoints:

```bash
# Generate content for a date
curl -X POST "http://localhost:8000/api/generate/13-10-2025"

# Get available dates
curl "http://localhost:8000/api/dates"

# Get content for a date
curl "http://localhost:8000/api/content/13-10-2025"
```

## Result / Demo

### Expected Output Structure

When you query `/api/content/13-10-2025`, you'll receive a JSON response like:

```json
{
  "date": "13-10-2025",
  "sections": [
    {
      "title": "India-Nepal Power Trade Agreement",
      "content": ["Point 1", "Point 2", ...],
      "importance": "absolutely_important"
    },
    ...
  ],
  "cards": [
    {
      "title": "India–Nepal Power Trade Agreement",
      "gs": "GS2 (IR), GS3 (Energy)",
      "tags": ["Hydropower", "Bilateral Relations"],
      "summary": "3-4 line summary...",
      "section_index": 0,
      "section_title": "India-Nepal Power Trade Agreement"
    },
    ...
  ],
  "mindmap": {
    "mindmaps": [
      {
        "title": "Main topic",
        "nodes": [...],
        "section_index": 0,
        "section_title": "..."
      },
      ...
    ]
  },
  "pyq": {
    "prelims": [
      {
        "question": "...",
        "options": {...},
        "correct_answer": "a",
        "section_index": 0,
        "section_title": "..."
      },
      ...
    ],
    "mains": [...]
  },
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

### Visualization Best Practices

When presenting results:

1. **Use Clear Labels**: All fields are clearly named and self-documenting
2. **Hierarchical Structure**: Content is organized by date → sections → generated materials
3. **Relationship Tracking**: `section_index` and `section_title` maintain relationships
4. **Consistent Format**: All dates follow DD-MM-YYYY format
5. **Metadata**: Timestamps track creation and updates

### Key Metrics

- **Processing Time**: ~2-5 minutes per date (depending on article length)
- **Content Generated**: 4-8 sections, 10-20 cards, 4-8 mindmaps, 10-30 PYQs per date
- **API Response Time**: <100ms for retrieval, instant for generation trigger

## What's Next?

### Enhancements to Consider

1. **Scheduled Automation**: Use Cloud Scheduler or cron jobs to automatically generate content daily
2. **Caching Layer**: Implement Redis caching for frequently accessed dates
3. **User Authentication**: Add authentication to protect API endpoints
4. **Frontend Integration**: Build a React/Next.js frontend to display content
5. **Analytics Dashboard**: Track content generation metrics and user engagement
6. **Multi-language Support**: Extend to support content in regional languages
7. **Content Recommendations**: Use AI to suggest related topics and dates
8. **Export Functionality**: Add PDF/JSON export for offline study

### Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Firestore Guide](https://cloud.google.com/firestore/docs)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Related Projects

- Build a notification system to alert users of new content
- Create a mobile app using the REST API
- Implement a search functionality across all generated content
- Add collaborative features for study groups

## Call to Action


