from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import requests
import logging
import re
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Training Data Sourcer Agent")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# Initialize DeepSeek Client
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

# Domain-specific keyword configurations
DOMAIN_CONFIGS = {
    "churn": {
        "boost": ["churn", "customer", "telecom", "telco", "retention", "attrition", 
                  "subscription", "contract", "tenure", "monthly", "charges", "tabular", "csv"],
        "penalty": ["heart", "disease", "diabetes", "depression", "plant", "image", "cnn", 
                    "xray", "food", "anime", "medical", "radiology"],
        "data_type": "tabular"
    },
    "medical": {
        "boost": ["medical", "chest", "xray", "x-ray", "pneumonia", "radiology", "lung", 
                  "ct", "mri", "scan", "clinical", "diagnosis", "healthcare"],
        "penalty": ["food", "garbage", "anime", "comic", "churn", "recruitment"],
        "data_type": "image"
    },
    "sentiment": {
        "boost": ["sentiment", "text", "nlp", "reviews", "comments", "tweets", "language", "classification"],
        "penalty": ["image", "xray", "medical", "tabular"],
        "data_type": "text"
    },
    "image": {
        "boost": ["image", "classification", "detection", "segmentation", "cnn", "visual", "picture"],
        "penalty": ["text", "tabular", "csv", "sentiment"],
        "data_type": "image"
    },
    "timeseries": {
        "boost": ["time", "series", "temporal", "forecasting", "stock", "price", "trend", "sequential"],
        "penalty": ["image", "sentiment", "tabular"],
        "data_type": "timeseries"
    }
}

# Preprocessing templates by data type
PREPROCESSING_TEMPLATES = {
    "text": '''import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Load data
data = pd.read_csv("dataset.csv")

# Find text and target columns
possible_text_cols = ["text", "article", "content", "body", "title", "description"]
possible_targets = ["label", "target", "class", "fake", "is_fake", "is_real"]

text_col = next((col for col in possible_text_cols if col in data.columns), data.columns[0])
target_col = next((col for col in possible_targets if col in data.columns), data.columns[-1])

X = data[text_col].fillna("")
y = data[target_col]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# NLP pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english", max_features=10000)),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Fit and evaluate
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(classification_report(y_test, preds))
''',

    "tabular": '''import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Load data
data = pd.read_csv("dataset.csv")

# Separate features and target
possible_targets = ["Churn", "churn", "Exited", "Attrition", "target", "label", "Class"]
target = next((col for col in possible_targets if col in data.columns), data.columns[-1])

X = data.drop(columns=[target])
y = data[target]

# Identify column types
categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

# Preprocessing pipeline
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

# Full pipeline with model
pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("classifier", RandomForestClassifier(random_state=42))
])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Fit model
pipeline.fit(X_train, y_train)

print(f"Accuracy: {pipeline.score(X_test, y_test)}")
''',

    "image": '''import pandas as pd
import torch
from PIL import Image
from torchvision import transforms

# Load dataset
data = pd.read_csv("dataset.csv")

# Image preprocessing pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Load images
images = [transform(Image.open(path).convert("RGB")) for path in data["image_path"]]
labels = torch.tensor(data["label"].values)

# Create dataset and dataloader
dataset = torch.utils.data.TensorDataset(torch.stack(images), labels)
loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

print("Image preprocessing completed.")
''',

    "timeseries": '''import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch

# Load time series data
data = pd.read_csv("dataset.csv", parse_dates=["timestamp"])
data = data.sort_values("timestamp")

# Normalize values
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data[["value"]])

# Create sequences
def create_sequences(data, seq_length=30):
    X, y = [], []

    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])

    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data, seq_length=30)

X = torch.FloatTensor(X)
y = torch.FloatTensor(y)

print("Time series preprocessing completed.")
'''
}

def detect_data_type(task: str, description: str, constraints: str) -> str:
    """Detect the data type from task/description/constraints."""
    full_text = f"{task} {description} {constraints}".lower()
    
    # CHECK TEXT
    if any(word in full_text for word in ["text", "nlp", "sentiment", "language", "document", "review", "sentence", "article", "fake", "news", "misinformation"]):
        return "text"
    
    # CHECK TABULAR FIRST - before checking for "image" keyword
    if any(word in full_text for word in ["tabular", "csv", "structured", "table", "rows", "columns", "customer-level", "numeric", "categorical"]):
        return "tabular"
    
    # CHECK FOR NEGATIVE IMAGE SIGNALS - if contains "no image", skip image detection
    has_no_image = any(phrase in full_text for phrase in ["no image", "not image", "non-image", "without image"])
    if not has_no_image and any(word in full_text for word in ["image", "photo", "picture", "vision", "cnn", "object detection", "x-ray", "jpg", "png", "bounding box"]):
        return "image"
    
    
    # CHECK TIME SERIES
    if any(word in full_text for word in ["time series", "temporal", "timeseries", "forecast", "stock", "price", "timestamp"]):
        return "timeseries"
    
    return "tabular"  # Default to tabular



def get_display_title(task: str, use_case: str, constraints: str = "") -> str:
    """Generate a smart display title based on the actual problem."""
    text = f"{task} {use_case} {constraints}".lower()
    
    # Check fake news FIRST before generic text classification
    if ("fake" in text and "news" in text) or ("news" in text and ("fake" in text or "real" in text)):
        return "Fake News Detection"
    elif "churn" in text:
        return "Customer Churn Prediction"
    elif "fraud" in text:
        return "Fraud Detection"
    elif "pneumonia" in text or "x-ray" in text or "xray" in text:
        return "Medical Image Classification"
    elif "resume" in text:
        return "Resume Screening"
    elif "sentiment" in text:
        return "Sentiment Analysis"
    elif "recommendation" in text:
        return "Recommendation System"
    elif "forecast" in text or "prediction" in text and "time" in text:
        return "Time Series Forecasting"
    
    return task

def detect_domain(task: str, description: str = "") -> str:
    """Detect the domain/category."""
    full_text = (task + " " + description).lower()
    
    if "churn" in full_text or "customer" in full_text or "telecom" in full_text:
        return "Telecom / Business"
    elif any(word in full_text for word in ["medical", "disease", "xray", "health", "clinical"]):
        return "Medical / Healthcare"
    elif any(word in full_text for word in ["sentiment", "text", "nlp", "review", "fake", "news", "misinformation"]):
        return "NLP / Text"
    elif any(word in full_text for word in ["image", "vision", "object detection"]):
        return "Computer Vision"
    elif any(word in full_text for word in ["time", "forecast", "timeseries"]):
        return "Time Series"
    return "General"

def infer_actual_task(task: str, description: str) -> str:
    """Infer the actual task from description, not just the ML method."""
    desc_lower = description.lower()
    
    if "churn" in desc_lower:
        return "Customer Churn Prediction"
    elif "sentiment" in desc_lower:
        return "Sentiment Analysis"
    elif "fake" in desc_lower or "news" in desc_lower or "misinformation" in desc_lower:
        return "Fake News Detection"
    elif "classification" in desc_lower and "image" in desc_lower:
        return "Image Classification"
    elif "forecast" in desc_lower:
        return "Time Series Forecasting"
    elif "detection" in desc_lower:
        return "Object Detection"
    return task  # Return original if can't infer

def extract_key_terms(task: str, description: str, constraints: str) -> list:
    """Extract important keywords with domain intelligence."""
    # Domain-specific keywords to prioritize
    churn_keywords = ["churn", "customer", "attrition", "retention", "telecom", "telco", "contract", "tenure", "monthly", "charges", "service", "usage", "subscription"]
    medical_keywords = ["medical", "disease", "patient", "diagnosis", "clinical", "health", "treatment", "condition"]
    image_keywords = ["image", "object", "detection", "segmentation", "visual", "classification"]
    text_keywords = ["text", "sentiment", "review", "document", "language", "nlp"]
    fake_news_keywords = ["fake", "news", "real", "misinformation", "article", "title", "body", "text", "publication", "source", "metadata", "detection"]
    
    full_text = f"{task} {description} {constraints}".lower()
    
    # Check domain and get relevant keywords
    # Check domain and get relevant keywords
    if any(word in full_text for word in ["fake", "news", "misinformation"]):
        priority_keywords = fake_news_keywords
    elif any(word in full_text for word in ["churn", "customer leave"]):
        priority_keywords = churn_keywords
    elif any(word in full_text for word in ["medical", "disease", "diagnosis"]):
        priority_keywords = medical_keywords
    elif any(word in full_text for word in ["image", "object", "detection"]):
        priority_keywords = image_keywords
    elif any(word in full_text for word in ["sentiment", "text", "nlp"]):
        priority_keywords = text_keywords
    else:
        priority_keywords = []
    
    # Get keywords that appear in text
    found_priority = [w for w in priority_keywords if w in full_text]
    
    # Add additional important words from description/constraints
    stopwords = {"a", "the", "is", "for", "with", "and", "or", "to", "in", "on", "your", "the", "data", "dataset", "no", "not"}
    extra_words = [w for w in full_text.split() if len(w) > 3 and w not in stopwords and w.isalpha()]
    extra_words = list(dict.fromkeys(extra_words))[:5]
    
    # Combine: priority keywords first, then extras
    all_keywords = found_priority + extra_words
    return all_keywords[:12]

def build_search_query(task: str, description: str, constraints: str) -> str:
    """Build a smarter search query - don't repeat task, focus on unique keywords."""
    key_terms = extract_key_terms(task, description, constraints)
    
    # Build: just use unique keywords, not task repeated
    if key_terms:
        query = " ".join(key_terms)
    else:
        query = task
    
    return query.strip()

def score_result(title: str, description: str, domain: Optional[str]) -> float:
    """Score a result based on domain-aware keywords with exact match boost."""
    text = f"{title} {description}".lower()
    title_lower = title.lower()
    score = 1.0
    
    if not domain:
        return score
    
    config = DOMAIN_CONFIGS.get(domain)
    if not config:
        return score
    
    # Boost for relevant keywords
    boost_count = sum(1 for keyword in config["boost"] if keyword in text)
    score *= (1.0 + 0.3 * boost_count)
    
    # EXTRA BOOST for exact matches in title
    if "churn" in title_lower:
        score += 10
    if "telecom" in title_lower or "telco" in title_lower:
        score += 8
    if "customer" in title_lower and "churn" in text:
        score += 10
    
    # STRONG PENALTY for non-churn results when searching churn
    if domain == "Telecom / Business" and "churn" not in text:
        score -= 20
    
    # PENALTY for generic results
    if "data-analysis-projects" in title_lower or "data analysis" in title_lower:
        score -= 5
    if "dummy" in title_lower or "test" in title_lower:
        score -= 3
    
    # Penalize for irrelevant keywords
    penalty_count = sum(1 for keyword in config["penalty"] if keyword in text)
    score *= max(0.1, 1.0 - 0.2 * penalty_count)
    
    return max(0.1, score)  # Don't go below 0.1

def search_huggingface_datasets(query: str, domain: Optional[str]) -> str:
    """Search HuggingFace with domain-aware ranking."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        search_terms = " ".join(query.split()[:4])
        url = f"https://huggingface.co/api/datasets?search={search_terms}&sort=likes&direction=-1"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            datasets = response.json()
            
            # Score and filter
            scored = []
            for ds in datasets:
                title = ds.get('id', '')
                desc = ds.get('description', '') or ''
                score = score_result(title, desc, domain)
                if score > 0.4:  # Only keep reasonably relevant results
                    scored.append((score, ds))
            
            if not scored:
                return f"No highly relevant datasets found on HuggingFace for '{query}'."
            
            scored.sort(key=lambda x: x[0], reverse=True)
            top_datasets = [ds for score, ds in scored[:5]]
            
            result = f"HuggingFace Datasets:\n\n"
            for i, dataset in enumerate(top_datasets, 1):
                result += f"{i}. **{dataset.get('id', 'Unknown')}**\n"
                result += f"   Downloads: {dataset.get('downloads', 0)}\n"
                result += f"   Likes: {dataset.get('likes', 0)}\n"
                result += f"   URL: https://huggingface.co/datasets/{dataset.get('id', '')}\n\n"
            return result
        return f"No datasets found on HuggingFace."
    except Exception as e:
        logger.warning(f"HuggingFace search error: {e}")
        return f"Could not fetch HuggingFace datasets."

def search_kaggle_datasets(query: str, domain: str = "") -> str:
    """Search Kaggle datasets with curated fallbacks."""
    
    # Curated dataset recommendations by domain
    curated_datasets = {
        "Telecom / Business": [
            ("Telco Customer Churn", "Contains customer-level telecom data with tenure, contract type, monthly charges, and churn label."),
            ("IBM Telco Customer Churn", "Standard dataset with 7k customers and 20 features for binary churn classification."),
            ("Telecom Customer Churn Dataset", "Useful for customer retention and attrition prediction with service usage patterns."),
        ],
        "NLP / Text": [
            ("Fake and Real News Dataset", "Contains labeled fake and real news articles with title and text fields for binary classification."),
            ("Fake News Detection Dataset", "Useful for binary classification of news articles as fake or real with metadata."),
            ("LIAR Dataset", "Short political statements labeled by truthfulness level, useful for misinformation detection."),
        ],
        "Medical / Healthcare": [
            ("Heart Disease UCI", "Comprehensive medical dataset for cardiovascular disease prediction."),
            ("Breast Cancer Wisconsin", "Clinical features for binary cancer diagnosis classification."),
            ("Diabetic Retinopathy", "Medical imaging dataset for disease detection."),
        ],
    }
    
    # Get curated results for domain
    datasets = curated_datasets.get(domain, [])
    
    if datasets:
        result = f"Kaggle Datasets:\n\n"
        for i, (name, description) in enumerate(datasets, 1):
            result += f"{i}. **{name}**\n   {description}\n\n"
        result += f"Or search on Kaggle: https://kaggle.com/search?q={query.replace(' ', '+')}\n"
        return result
    else:
        return f"Kaggle Datasets:\n\nSearch on Kaggle: https://kaggle.com/search?q={query.replace(' ', '+')}\n"

def search_github_datasets(query: str, domain: Optional[str]) -> str:
    """Search GitHub with domain-aware ranking."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        }
        search_terms = " ".join(query.split()[:3])
        url = f"https://api.github.com/search/repositories?q={search_terms}+topic:dataset&sort=stars&order=desc&per_page=10"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json().get("items", [])
            
            # Score and filter - STRICT filtering for churn
            scored = []
            for repo in repos:
                title = repo['name']
                desc = repo.get('description', '') or ''
                
                title_text = title.lower()
                desc_text = desc.lower()
                full_text = f"{title_text} {desc_text}"

                # Strict filter: only include repos with churn keywords
                full_text = f"{title} {desc}".lower()
                has_churn_keywords = (
                    "churn" in full_text
                    or "telecom" in full_text
                    or "customer attrition" in full_text
                    or "customer retention" in full_text
                )
                
                # Optional: allow strong description match only if title is not generic
                generic_title_words = [
                    "data-analysis-projects",
                    "machine-learning-projects",
                    "data-science-projects",
                    "ml-projects",
                    "kaggle-projects"
                ]
                is_generic_title = any(word in title_text for word in generic_title_words)

                if is_generic_title:
                    continue
                    
                print("GITHUB CHECK:", title, "|", has_churn_keywords)

                if not has_churn_keywords:
                    continue  # Skip repos without churn keywords
                
                score = score_result(title, desc, domain)
                if score > 0.35:
                    scored.append((score, repo))
            
            if not scored:
                return f"No highly relevant GitHub repositories found."
            
            scored.sort(key=lambda x: x[0], reverse=True)
            top_repos = [repo for score, repo in scored[:5]]
            
            result = f"GitHub Repositories:\n\n"
            for i, repo in enumerate(top_repos, 1):
                result += f"{i}. **{repo['name']}** by {repo['owner']['login']}\n"
                result += f"   Stars: {repo['stargazers_count']}\n"
                result += f"   {repo.get('description', 'N/A')[:80]}\n"
                result += f"   URL: {repo['html_url']}\n\n"
            return result
        return f"No GitHub datasets found."
    except Exception as e:
        logger.warning(f"GitHub search error: {e}")
        return f"Could not fetch GitHub datasets."

def search_arxiv_papers(query: str) -> str:
    """Search ArXiv for papers."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        search_terms = " AND ".join(query.split()[:3])
        url = f"http://export.arxiv.org/api/query?search_query=cat:cs.LG+AND+all:{search_terms}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = f"ArXiv Papers:\n\n"
            lines = response.text.split('\n')
            count = 0
            for line in lines:
                if '<title>' in line and count < 5:
                    title = line.replace('<title>', '').replace('</title>', '').strip()
                    if title and title != 'ArXiv API':
                        count += 1
                        result += f"{count}. {title}\n"
            if count > 0:
                result += f"\nMore: https://arxiv.org/search/?query={query.replace(' ', '+')}&searchtype=all\n"
                return result
        return ""
    except Exception as e:
        logger.warning(f"ArXiv search error: {e}")
        return ""

# ==================== Request Models ====================

class DatasetRequest(BaseModel):
    ml_task: str
    problem_description: Optional[str] = None
    constraints: Optional[str] = None

# ==================== Endpoints ====================

@app.get("/")
def read_root():
    return {
        "name": "DataFinder",
        "description": "Smart dataset discovery across 4 sources",
        "version": "2.0.0"
    }

@app.post("/search-datasets")
async def search_datasets(request: DatasetRequest):
    """Search for datasets with smart query building and domain-aware ranking."""
    try:
        # Detect domain and data type
        domain = detect_domain(request.ml_task, request.problem_description or "")
        actual_task = infer_actual_task(request.ml_task, request.problem_description or "")
        data_type = detect_data_type(request.ml_task, request.problem_description or "", request.constraints or "")
        # Get smart display title
        display_title = get_display_title(
            request.ml_task, 
            request.problem_description or "",
            request.constraints or ""
        )

        # Build smart search query
        search_query = build_search_query(
            request.ml_task,
            request.problem_description or "",
            request.constraints or ""
        )
        
        logger.info(f"Domain: {domain}, DataType: {data_type}, Query: {search_query}")
        
        # Get results from all sources
        kaggle_results = search_kaggle_datasets(search_query, domain)
        hf_results = search_huggingface_datasets(search_query, domain)
        github_results = search_github_datasets(search_query, domain)
        arxiv_results = search_arxiv_papers(search_query)
        
        # Get preprocessing template based on data type
        template_key = data_type if data_type in PREPROCESSING_TEMPLATES else "tabular"
        preprocessing_code = PREPROCESSING_TEMPLATES[template_key]
        
        # Adjust display for text data
        if data_type == "text":
            display_data_type = "Text / Tabular"
        else:
            display_data_type = data_type.capitalize()

        # Compile results
        recommendations = f"""
# Dataset Search Results

**Task:** {request.ml_task}
**Data Type Detected:** {data_type.capitalize()}
**Domain:** {domain.capitalize() if domain else 'General'}
**Search Query:** {search_query}
**Display Title:** {display_title}

## Problem Description
{request.problem_description or 'Finding best datasets for this task'}

## Constraints
{request.constraints or 'None specified'}

---

## {kaggle_results.split(chr(10))[0]}
{chr(10).join(kaggle_results.split(chr(10))[1:])}

---

## {hf_results.split(chr(10))[0]}
{chr(10).join(hf_results.split(chr(10))[1:])}

---

## {github_results.split(chr(10))[0]}
{chr(10).join(github_results.split(chr(10))[1:])}

---

## {arxiv_results.split(chr(10))[0] if arxiv_results else ''}
{chr(10).join(arxiv_results.split(chr(10))[1:]) if arxiv_results else ''}

---

## Preprocessing Code ({data_type.capitalize()} Data)

```python
{preprocessing_code}
```

## Quality Checklist
- ✓ Check dataset size is sufficient
- ✓ Verify licensing compatibility
- ✓ Review documentation
- ✓ Check community activity
- ✓ Verify recent maintenance
- ✓ Assess data completeness
"""
        
        return {
            "status": "success",
            "task": display_title,  # Use smart display title
            "domain": domain,
            "data_type": data_type,
            "query": search_query,
            "recommendations": recommendations,
        }
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
