# 🚀 AI Training Data Sourcer Agent

> Find the best training datasets for your ML projects in seconds using AI-powered multi-agent search.

An intelligent agent system that searches across **Kaggle, HuggingFace, GitHub, and ArXiv** to find, analyze, and provide preprocessing code for training datasets.

## ✨ Features

- **Multi-Source Search**: Simultaneously searches 4+ dataset sources
- **Quality Analysis**: Evaluates datasets for size, licensing, documentation, and community feedback
- **Preprocessing Code**: Auto-generates starter code for different ML tasks
- **ReAct Agent Architecture**: Intelligent reasoning and task planning using DeepSeek API
- **Beautiful UI**: Clean, dark-mode frontend built with React
- **Docker Ready**: One-command deployment

## 🎯 What It Does

```
User Input: "Image classification dataset"
         ↓
    Agent Searches:
    ├─ Kaggle for popular datasets
    ├─ HuggingFace for ready-to-use data
    ├─ GitHub for community datasets
    └─ ArXiv for academic benchmarks
         ↓
Returns:
    ├─ Top 5 curated datasets
    ├─ Quality metrics & licensing info
    ├─ Download links
    └─ Python preprocessing code
```

## 🏗️ Architecture

### Backend (FastAPI + LangChain)
- **ReAct Agent Pattern**: Uses Chain-of-Thought reasoning for dataset discovery
- **DeepSeek API Integration**: Native OpenAI-compatible API support
- **6 Specialized Tools**:
  - `search_kaggle_datasets` - Find competition datasets
  - `search_huggingface_datasets` - Discover HF Dataset Hub
  - `search_github_datasets` - Browse GitHub dataset repos
  - `search_arxiv_papers` - Search academic papers
  - `analyze_dataset_quality` - Quality assessment
  - `generate_preprocessing_code` - Auto-generate Python code

### Frontend (React)
- Modern, responsive design
- Real-time search with streaming results
- Quick-start buttons for common tasks
- Mobile-friendly interface

### Tech Stack
```
Backend:        FastAPI, LangChain, DeepSeek API
Frontend:       React, Vite
Database:       None (stateless)
Deployment:     Docker, Docker Compose
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (easiest) OR
- Python 3.11+, Node.js 18+
- DeepSeek API key ([get one free](https://platform.deepseek.com))

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/pranjalisr/ai-data-sourcer.git
cd ai-data-sourcer

# Create .env file
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# Run everything
docker-compose up
```

Then open **http://localhost:3000**

### Option 2: Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Set your API key
export DEEPSEEK_API_KEY="your_key_here"

# Run server
uvicorn main:app --reload
```

Server runs on **http://localhost:8000**

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:3000**

## 📝 Usage Examples

### Example 1: Image Classification
```
Input: "Image classification"
Description: "Building a CNN for medical imaging"
Constraints: "Need high-quality labeled data"

Output:
✓ ImageNet (1.2M images, 1000 classes)
✓ CIFAR-10 (50K images, 10 classes)
✓ Medical Imaging Datasets from ArXiv
+ Preprocessing code for PyTorch
+ License info (all open source)
```

### Example 2: NLP / Sentiment Analysis
```
Input: "Sentiment analysis"
Description: "Twitter/social media sentiment"
Constraints: "Real-time data needed"

Output:
✓ SemEval Twitter Sentiment Dataset
✓ Stanford Movie Reviews
✓ Hugging Face Sentiment Datasets
+ HuggingFace tokenizer code
+ Train/validation split utilities
```

## 🔌 API Endpoints

### POST `/search-datasets`
Main endpoint for dataset search.

**Request:**
```json
{
  "ml_task": "image classification",
  "problem_description": "Medical imaging for X-rays",
  "constraints": "High-quality labeled data"
}
```

**Response:**
```json
{
  "status": "success",
  "task": "image classification",
  "recommendations": "Agent analysis with dataset recommendations...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET `/health`
Health check endpoint.

```bash
curl http://localhost:8000/health
```

### POST `/analyze-dataset/{dataset_name}`
Analyze a specific dataset.

```bash
curl -X POST http://localhost:8000/analyze-dataset/ImageNet
```

### POST `/generate-preprocessing`
Generate preprocessing code.

```bash
curl -X POST "http://localhost:8000/generate-preprocessing?dataset_type=image&ml_task=image_classification"
```

## 🔧 Configuration

### Environment Variables

```env
# Required
DEEPSEEK_API_KEY=sk-xxx...

# Optional
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=3000
LOG_LEVEL=INFO
```

### DeepSeek API Setup

1. Get API key: https://platform.deepseek.com
2. Create `.env` file:
   ```
   DEEPSEEK_API_KEY=your_key_here
   ```
3. The agent uses DeepSeek's OpenAI-compatible API endpoint automatically

## 🎓 How It Works

### Agent Flow (ReAct Pattern)

```
Observation: User asks about "image classification datasets"
             ↓
Thought:     "I need to search multiple sources for image datasets"
             ↓
Action:      [search_kaggle_datasets("image classification")]
             ↓
Observation: "Found CIFAR-10, ImageNet, ..."
             ↓
Thought:     "Good start. Let me also check HuggingFace"
             ↓
Action:      [search_huggingface_datasets("image classification")]
             ↓
... (continues iterating until complete)
             ↓
Final Output: Curated list of 5+ datasets with analysis
```

## 📊 Supported ML Tasks

The agent can help with:
- Image Classification (CIFAR, ImageNet, custom)
- Object Detection (COCO, Pascal VOC)
- NLP (Sentiment, NER, Translation)
- Time Series (Stock data, sensors)
- Tabular Data (Regression, classification)
- Recommender Systems
- Audio & Speech
- Multimodal Tasks

## 🛠️ Development

### Project Structure
```
ai-data-sourcer/
├── backend/
│   ├── main.py              # FastAPI app + ReAct agent
│   ├── requirements.txt
│   └── tools/               # (Can be extracted later)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

### Adding New Dataset Sources

1. Create a new tool in `backend/main.py`:
```python
@tool
def search_your_source(query: str) -> str:
    """Search your custom dataset source."""
    # Implementation here
    return results

tools.append(search_your_source)
```

2. The agent will automatically use it

### Extending the Agent

Modify the `prompt_template` in `backend/main.py` to change agent behavior:
```python
prompt_template = """
You are an AI Training Data Sourcer...
[Customize instructions here]
"""
```

## 🚀 Deployment

### Render.com (Free)
```bash
# Push to GitHub
git push

# Connect repo on Render
# Set environment: DEEPSEEK_API_KEY
# Done! 🎉
```

### Railway.app
```bash
# Add to package.json
{
  "scripts": {
    "start": "uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### AWS / Google Cloud
```bash
# Build image
docker build -t ai-data-sourcer .

# Push to registry
docker tag ai-data-sourcer:latest [YOUR_REGISTRY]/ai-data-sourcer:latest
docker push [YOUR_REGISTRY]/ai-data-sourcer:latest

# Deploy
# (Follow your cloud provider's docs)
```

## 📈 Performance & Limits

- **Search Time**: 5-15 seconds (depending on sources)
- **API Calls**: 5-10 per search
- **Agent Iterations**: Max 10 (configurable)
- **Concurrent Users**: Limited by DeepSeek API rate limits

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] More dataset sources (IEEE DataPort, Zenodo, etc.)
- [ ] Caching for repeated searches
- [ ] User accounts & search history
- [ ] Dataset recommendations based on code
- [ ] Live dataset availability checking
- [ ] Integration with Jupyter notebooks

## 📄 License

MIT License - Free to use and modify

## 🔗 Links

- **DeepSeek API Docs**: https://platform.deepseek.com/api-docs
- **LangChain Docs**: https://python.langchain.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

## 💬 Questions?

Open an issue or reach out:
- Email: pranjalisr25@gmail.com
- LinkedIn: https://linkedin.com/in/pranjalisr
- GitHub: @pranjalisr

---

**Built with ❤️ by [Pranjali SR](https://github.com/pranjalisr)**

*Star ⭐ this repo if it helps you find datasets faster!*
