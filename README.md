# Brand Buzz: TikTok Comment Analysis & Visualization

A full-stack application that analyzes TikTok comments about CeraVe products, extracts themes and keywords using AI/ML, and visualizes the results in an interactive network graph.

## 🎯 Project Overview

This project demonstrates a complete data science pipeline from raw social media data to interactive visualization:

- **Data Processing**: Scrapes and cleans TikTok comments
- **AI Analysis**: Extracts keywords and themes using LLM (Llama3)
- **Sentiment Analysis**: Classifies comment sentiment using sentence transformers
- **Network Visualization**: Interactive D3.js graph showing keyword relationships

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Data Pipeline**: Comment preprocessing, keyword extraction, sentiment analysis
- **API Server**: FastAPI with PostgreSQL database
- **AI/ML**: Ollama (Llama3), Sentence Transformers
- **Database**: PostgreSQL with SQLAlchemy ORM

### Frontend (Next.js/React)
- **Interactive Graph**: D3.js network visualization
- **Real-time Updates**: Dynamic data fetching from API
- **Modern UI**: Tailwind CSS with responsive design
- **TypeScript**: Full type safety

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL
- Ollama (for LLM inference)

## 📊 Data Pipeline

### 1. Data Ingestion
- Raw TikTok comments from `tiktok_apify_comments.json`
- There is code to scrape from TikTok using apify, but this only ran once to avoid getting charged too many times by Apify
- In theory, to run this on another TikTok url, you would need to run the apify code with that url. 

### 2. Preprocessing (`scraping.py`)
- Filters out mentions, questions, non-English content
- Grammar correction using LLM
- Language detection and translation
- Outputs cleaned comments to `final_comments.csv`

### 3. Analysis (`theme_and_graph.py`)
- **Keyword Extraction**: Uses Llama3 to extract themes from comments
- **Semantic Matching**: Sentence transformers for keyword-comment matching and sentiment classification
- **Graph Generation**: Creates network of keyword relationships

### 4. Visualization
- Interactive D3.js network graph
- Color-coded sentiment (green=positive, yellow=neutral, red=negative)
- Node size based on keyword frequency
- Edge thickness based on co-occurrence strength

## 🔄 Updating the Graph (Local Only)

**Note**: The deployed version uses static data from a Postgres Database. To update the graph with new analysis, you must run the backend locally.

### Manual Pipeline Execution
1. **Run the full pipeline**:
   ```bash
   cd backend
   python theme_and_graph.py
   ```

2. **Or run individual steps**:
   ```bash
   # Preprocess comments
   python scraping.py
   
   # Generate new graph
   python theme_and_graph.py
   
   # Update database
   python -c "from api import load_graph_data_to_db; load_graph_data_to_db()"
   ```

## 📁 Project Structure

```
suade-take-home/
├── backend/
│   ├── api.py                 # FastAPI server
│   ├── theme_and_graph.py     # Main analysis pipeline
│   ├── scraping.py            # Data preprocessing
│   ├── sentiment_analysis.py  # Sentiment analysis
│   ├── prompts/               # LLM prompts
│   ├── requirements.txt       # Python dependencies
│   └── data files/            # JSON/CSV outputs
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx           # Main application
│   │   ├── components/        # React components
│   │   └── hooks/             # Custom hooks
│   ├── package.json           # Node.js dependencies
│   └── public/                # Static assets
└── README.md
```

## 🔧 API Endpoints

- `GET /comments` - Returns processed comments with keywords
- `GET /graph` - Returns theme graph data for visualization

## 🎨 Features

### Interactive Graph
- **Zoom & Pan**: Navigate the network visualization
- **Node Selection**: Click nodes to filter related comments
- **Tooltips**: Hover for detailed keyword information
- **Sentiment Colors**: Visual sentiment indicators

### Comment Analysis
- **Keyword Filtering**: View comments by selected keywords
- **Sentiment Breakdown**: Positive, neutral, negative classifications
- **Real-time Updates**: Dynamic comment loading (future feature)

### Data Management
- **Keyword Regeneration**: AI-powered theme extraction
- **Database Storage**: Persistent graph data
- **Export Capabilities**: JSON/CSV data outputs

## 🛠️ Development

### Adding New Features
1. **Backend**: Add endpoints in `api.py`
2. **Frontend**: Create components in `src/app/components/`
3. **Analysis**: Extend pipeline in `theme_and_graph.py`

### Customizing Analysis
- **Keywords**: Modify prompts in `prompts/keyword_prompt.txt`
- **Sentiment**: Adjust thresholds in `sentiment_analysis.py`
- **Graph**: Tune parameters in `theme_and_graph.py`

## 🚀 Deployment

### Frontend (Vercel)
- Build: `npm run build`
- Deploy static files
- Set `NEXT_PUBLIC_API_BASE` to your backend URL

### Backend (Render)
- Deploy Python app with PostgreSQL
- Set environment variables for database
- Install Ollama dependencies 

---
