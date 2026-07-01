# DataFinder - AI Training Data Sourcer Agent

Smart dataset discovery and preprocessing recommendations for ML/AI projects.

DataFinder is a full-stack AI agent that understands your machine learning task and automatically recommends the best datasets from Kaggle, HuggingFace, GitHub, and ArXiv. It intelligently detects your problem domain, identifies the appropriate data type, and generates task-specific preprocessing code templates.

## Features

### Intelligent Domain Detection
Automatically identifies your problem domain:
- **Telecom / Business** — Customer churn, retention, attrition prediction
- **Medical / Healthcare** — Disease diagnosis, clinical outcomes, health monitoring
- **NLP / Text** — Sentiment analysis, fake news detection, document classification
- **Computer Vision** — Image classification, object detection, segmentation
- **Time Series** — Forecasting, anomaly detection, temporal prediction

### Smart Dataset Discovery
Multi-source dataset recommendations:
- **Live API Searches** — Real-time results from HuggingFace and GitHub APIs
- **Curated Fallbacks** — Domain-specific Kaggle dataset recommendations
- **Domain-Aware Ranking** — Results scored based on relevance to your task
- **Academic Papers** — ArXiv research papers matching your problem

### Data Type Detection
Automatically identifies your data needs:
- **Tabular Data** — CSV files, structured records, customer databases
- **Text Data** — Articles, documents, reviews, social media content
- **Image Data** — Photos, medical scans, satellite imagery, visual content
- **Time Series** — Stock prices, sensor readings, temporal sequences

### Task-Specific Code Generation
Production-ready preprocessing templates:
- **Tabular** — Pandas, OneHotEncoder, StandardScaler, RandomForest
- **Text/NLP** — TfidfVectorizer, LogisticRegression, classification metrics
- **Images** — PyTorch, torchvision, CNN architectures
- **Time Series** — Train/test splits with temporal awareness

## Quick Start

### Prerequisites
- Docker & Docker Compose
- DeepSeek API Key (get free key at https://platform.deepseek.com)

### Installation

1. Clone the repository
```bash
git clone https://github.com/pranjalisr/ML-Datasets-finder.git
cd ML-Datasets-finder
```

2. Set up environment
```bash
cp .env.example .env
# Edit .env and add your DeepSeek API key
nano .env
```

3. Run with Docker
```bash
docker-compose up --build
```

### Access the App
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Health Check: http://localhost:8000/health

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18 + Vite |
| Backend | FastAPI 0.104.1 |
| Server | Uvicorn 0.24.0 |
| LLM | DeepSeek API |
| Container | Docker Compose |
| Data Processing | Pandas + NumPy |

### Dependencies (9 packages total)

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
python-dotenv==1.0.0
pandas==2.1.3
numpy==1.26.2
```

No LangChain. No OpenAI SDK. Direct HTTP requests only.

## Project Structure

```
ML-Datasets-finder/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React component
│   │   ├── App.css          # Styling
│   │   └── markdownUtils.js # Markdown parser
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Backend container
├── .env.example            # Environment template
└── README.md              # This file
```

## API Endpoints

### POST /search-datasets

Main endpoint for dataset discovery.

**Request:**
```json
{
  "ml_task": "Binary classification",
  "problem_description": "Predict whether a telecom customer will leave the service based on contract type, monthly charges, tenure, support tickets, and service usage.",
  "constraints": "Tabular CSV dataset, customer-level rows, binary churn label, no image data."
}
```

**Response:**
```json
{
  "status": "success",
  "task": "Customer Churn Prediction",
  "domain": "Telecom / Business",
  "data_type": "tabular",
  "query": "churn customer telecom contract tenure monthly charges service usage",
  "recommendations": "# Dataset Search Results\n\n## Kaggle Datasets:\n1. **Telco Customer Churn**\n..."
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

## How It Works

The application uses a 7-step intelligent pipeline:

1. **Input Processing** — Parse user task, description, and constraints
2. **Domain Detection** — Keyword matching to identify problem domain
3. **Data Type Detection** — Detect whether task needs tabular, text, image, or time series data
4. **Query Building** — Extract key terms and build focused search query
5. **Multi-Source Search** — Search Kaggle, HuggingFace, GitHub, and ArXiv simultaneously
6. **Result Ranking** — Score results based on domain relevance and exact keyword matches
7. **Code Generation** — Generate task-specific preprocessing code templates

### Scoring Algorithm

Each result receives a relevance score:

```
score = 1.0
score += 0.3 * count(boost_keywords)
score *= max(0.1, 1.0 - 0.2 * count(penalty_keywords))

Exact matches: +10 for "churn", +8 for "telecom"
Generic results: -20 for "data-analysis-projects"

Show only results > 0.4
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Custom Domain Keywords

Edit backend/main.py to add domains:

```python
DOMAIN_CONFIGS = {
    "churn": {
        "boost": ["churn", "customer", "attrition", "retention", "telecom"],
        "penalty": ["heart", "disease", "medical", "image"]
    },
    "medical": {
        "boost": ["disease", "diagnosis", "patient", "clinical"],
        "penalty": ["churn", "telecom", "image"]
    }
}
```

## Usage Examples

### Example 1: Customer Churn Prediction

Input:
```
Task: Binary classification
Description: Predict whether a telecom customer will leave
Constraints: Tabular CSV, customer-level rows, churn label
```

Output:
```
Title: Customer Churn Prediction
Domain: Telecom / Business
Data Type: Tabular

Kaggle Datasets:
1. Telco Customer Churn
2. IBM Telco Customer Churn
3. Telecom Customer Churn Dataset

Preprocessing Code:
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

data = pd.read_csv("dataset.csv")
possible_targets = ["Churn", "churn", "Exited", "Attrition"]
target = next((col for col in possible_targets if col in data.columns), data.columns[-1])
```

### Example 2: Fake News Detection

Input:
```
Task: Text classification
Description: Detect fake vs real news articles
Constraints: English news, CSV format, TF-IDF friendly
```

Output:
```
Title: Fake News Detection
Domain: NLP / Text
Data Type: Text

Kaggle Datasets:
1. Fake and Real News Dataset
2. Fake News Detection Dataset
3. LIAR Dataset

Preprocessing Code:
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

data = pd.read_csv("dataset.csv")
possible_text_cols = ["text", "article", "content", "body", "title"]
text_col = next((col for col in possible_text_cols if col in data.columns), data.columns[0])

model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english", max_features=10000)),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(X_train, y_train)
preds = model.predict(X_test)
```

## Performance

| Metric | Value |
|--------|-------|
| Frontend Load Time | ~200ms |
| API Response Time | ~2-3s |
| Container Footprint | ~150MB |
| Concurrent Requests | Unlimited |
| Cold Start | ~3s |

## Troubleshooting

### Docker build fails
```bash
docker system prune -af --volumes
docker-compose up --build
```

### Backend returns 502 error
```bash
docker-compose logs backend
cat .env | grep DEEPSEEK_API_KEY
```

### Frontend not loading
- Check if port 3000 is free: `lsof -i :3000`
- Check browser console for CORS errors
- Verify backend: `curl http://localhost:8000/health`

### Results are generic
- Provide detailed problem description
- Include domain keywords in constraints
- Ensure data type matches your task

## Architecture Decisions

### Why No LangChain?
Version conflicts and dependency bloat. Direct HTTP requests are cleaner, faster, and easier to maintain.

### Why Custom Markdown Parser?
react-markdown creates npm conflicts. Custom parser handles our markdown subset with zero conflicts.

### Why Direct HTTP?
No authentication overhead for public APIs. Smaller package footprint. Direct control over requests. Faster iteration.

### Why DeepSeek API?
Cost-effective, good quality, OpenAI-compatible endpoint, easy to switch providers.

## Future Enhancements

- Multi-language dataset support
- Kaggle API integration
- Pre-trained models discovery
- Dataset quality scoring
- Code execution sandbox
- Search history and favorites
- Export code as .py file
- Web scraping for additional sources

## Contributing

Contributions welcome! Areas for improvement:
- Add more domain configurations
- Improve ArXiv paper ranking
- Better GitHub repository filtering
- PyTorch/TensorFlow preprocessing templates
- Mobile responsiveness
- Dark mode
- Search history

Fork the repo, create a feature branch, commit changes, and open a pull request.

## License

MIT License - use freely in your own work.

## Author

**Pranjali SR** - ML/AI Engineer

- GitHub: [@pranjalisr](https://github.com/pranjalisr)
- Portfolio: [View Projects](https://github.com/pranjalisr?tab=repositories)

---

Built with ❤️ for the ML community

Status: Production Ready | Last Updated: July 2026
