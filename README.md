# Multimodal Product Search Engine

An AI-powered e-commerce search engine that uses **Deep Learning (CLIP & FAISS)** to understand both **images and natural language text** to search for visually and semantically similar products.

![Multimodal Product Search Engine](https://img.shields.io/badge/AI-CLIP%20%2B%20FAISS-10b981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)

---

## 📌 Project Overview

Traditional search engines rely purely on exact keyword matching. If a user has an image of a shoe or wants to search using a combination like *"find shoes like this image but under ₹3000"*, traditional search fails.

This project demonstrates how **Contrastive Language–Image Pre-training (CLIP)** maps both images and text into a shared 512-dimensional vector space. Using **FAISS (Facebook AI Similarity Search)**, the system performs ultra-fast vector similarity search to return the most relevant products instantly.

---

## ✨ Features

- **Text Search**: Search for products using natural language queries (e.g., *"black running shoes"*, *"casual white sneakers"*).
- **Image Search**: Upload any image (JPG, JPEG, PNG) to find visually similar products from the database.
- **Multimodal (Image + Text) Search**: Upload an image **and** type a text constraint at the same time (e.g., Upload a shoe image + Type *"under ₹3000"*).
- **CLIP Vector Embeddings**: Uses OpenAI CLIP (`openai/clip-vit-base-patch32`) to project visual and textual features into normalized embeddings.
- **FAISS Vector Indexing**: Pre-calculates and indexes product embeddings using FAISS `IndexFlatIP` (Cosine Similarity) for sub-millisecond retrieval.
- **Interactive UI**: Sleek, modern dark-themed glassmorphism interface with drag-and-drop file upload, real-time image preview, filtering by category/price/similarity, and detailed product views.

---

## 🏗️ Architecture & Data Flow

```text
               USER
                 │
      ┌──────────┴──────────┐
      │  Image / Text / Both│
      └──────────┬──────────┘
                 │
            FastAPI Server
                 │
             CLIP Model
      (Text & Image Features)
                 │
       Normalized Embedding
                 │
            FAISS Index
      (Inner Product / Cosine)
                 │
        Top Match Products
                 │
         Frontend Web UI
```

---

## 📐 Multimodal Weighted Embedding Combination

When a user provides both an **image** and a **text query**, the engine combines their embeddings using a weighted sum:

$$\text{final\_embedding} = (\text{image\_embedding} \times \text{image\_weight}) + (\text{text\_embedding} \times \text{text\_weight})$$

* Default Weights: `image_weight = 0.6`, `text_weight = 0.4`
* The resulting vector is **L2-normalized** before querying the FAISS vector index.

---

## 📂 Folder Structure

```text
multimodal-product-search/
├── frontend/
│   ├── index.html         # Homepage with AI Search Interface & Categories
│   ├── results.html       # Search Results with Sidebar Filters & Similarity Badges
│   ├── product.html       # Product Details & "Find Similar" Recommendation Engine
│   ├── style.css          # Dark Glassmorphism Design System
│   ├── script.js          # Fetch API logic, Drag & Drop, Renderers
│   └── assets/
│       └── products/      # 30 Sample Product Images across 6 Categories
│
├── backend/
│   ├── main.py            # FastAPI Entrypoint, CORS & Static Mounts
│   ├── models/            # Pydantic Request/Response Data Schemas
│   ├── routes/            # Search & Product API Endpoints
│   ├── services/          # SearchService wrapping AI Engine & Index
│   └── data/
│       └── products.json  # 30 Sample E-commerce Products
│
├── ai_engine/
│   ├── clip_model.py      # HuggingFace CLIP Model & Processor Singleton
│   ├── embedding.py       # Image, Text & Multimodal Embedding Generator
│   ├── vector_search.py   # FAISS Index Builder & Query Executor
│   └── index.py           # Offline Script to Index Products
│
├── requirements.txt       # Python Dependencies
└── README.md              # Documentation
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Install Dependencies
Navigate to the project directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Step 1: Generate Product Embeddings & FAISS Index
Before starting the server, run the offline indexing script to generate product vector embeddings:

```bash
python -m ai_engine.index
```

This generates `ai_engine/product_embeddings.npy` and `ai_engine/products.index`.

### Step 2: Start the FastAPI Backend Server
Launch the FastAPI development server with Uvicorn:

```bash
python backend/main.py
```
*or directly with Uvicorn:*
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be live at `http://127.0.0.1:8000`.

### Step 3: Access the Frontend Web Application
Open your web browser and navigate to:
```text
http://127.0.0.1:8000/static/index.html
```
*(or open `frontend/index.html` directly in your browser).*

---

## 🔌 API Endpoints Documentation

### Health Check
- **`GET /`**
  - **Description**: Verify backend status.
  - **Response**: `{"message": "Multimodal Product Search API is running"}`

### Text Search
- **`POST /search/text`**
  - **Payload**: `{"query": "black running shoes", "top_k": 10}`
  - **Response**: List of top matching products with percentage similarity scores.

### Image Search
- **`POST /search/image`**
  - **Form Data**: `image` (File), `top_k` (Integer, default 10)
  - **Response**: Products ranked by visual feature similarity.

### Multimodal Search
- **`POST /search/multimodal`**
  - **Form Data**: `image` (File, Optional), `query` (String, Optional), `image_weight` (0.6), `text_weight` (0.4)
  - **Response**: Products matching combined visual and text representation.

### Products API
- **`GET /products`**: Returns list of all 30 products in the dataset.
- **`GET /products/{product_id}`**: Returns details of a single product.

---

## 🔮 Future Improvements

1. **Larger Dataset Integration**: Scale dataset to 100,000+ products using HNSW FAISS indices.
2. **Fine-Tuned Fashion CLIP**: Fine-tune CLIP on e-commerce product domain pairs for higher precision.
3. **Personalized Recommender System**: Factor in user click history and price affinity alongside vector similarity.
4. **Multilingual Search**: Extend support for multi-language product search using multilingual CLIP models.
5. **Price & Attribute Hard Filtering**: Perform hybrid vector search with pre-filtering on price range, brand, and size.
