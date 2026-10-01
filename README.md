<div align="center">

# 🔍 Multimodal Product Search Engine

### AI-Powered Visual & Semantic Product Search

<img src="https://readme-typing-svg.demolab.com/?lines=Search+by+image.+Search+by+text.;Or+both+at+once.&amp;center=true&amp;width=420&amp;height=35&amp;color=10B981&amp;vCenter=true&amp;size=18" />

<img src="https://img.shields.io/badge/AI-CLIP_%2B_FAISS-10b981?style=for-the-badge" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&amp;logo=fastapi&amp;logoColor=white" />
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&amp;logo=pytorch&amp;logoColor=white" />

</div>

<br>

An AI-powered e-commerce search engine using **Deep Learning (CLIP & FAISS)** to understand both images and natural language, returning visually and semantically similar products — including queries like *"find shoes like this image but under ₹3000"* that keyword search can't handle.

CLIP (Contrastive Language–Image Pre-training) maps images and text into a shared 512-dimensional vector space. FAISS then performs ultra-fast vector similarity search to return the most relevant products instantly.

<br>

## ✨ Features

| | Feature | What it does |
|:---:|---|---|
| 💬 | **Text Search** | Natural language queries like *"black running shoes"* |
| 🖼️ | **Image Search** | Upload a JPG/PNG to find visually similar products |
| 🧩 | **Multimodal Search** | Image + text constraint together, e.g. a shoe photo + *"under ₹3000"* |
| 🧠 | **CLIP Embeddings** | `openai/clip-vit-base-patch32` projects visual and text features into normalized vectors |
| ⚡ | **FAISS Indexing** | `IndexFlatIP` (cosine similarity) for sub-millisecond retrieval |
| 🎨 | **Interactive UI** | Dark glassmorphism design, drag-and-drop upload, live preview, filters |

<br>

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

<br>

## 📐 Multimodal Weighted Embedding

When both an image and a text query are given, their embeddings combine as a weighted sum, then get L2-normalized before querying FAISS:

$$\text{final\_embedding} = (\text{image\_embedding} \times \text{image\_weight}) + (\text{text\_embedding} \times \text{text\_weight})$$

Default weights: `image_weight = 0.6`, `text_weight = 0.4`

<br>

## 🔌 API Endpoints

| Method | Endpoint | Description |
|:---:|---|---|
| `GET` | `/` | Health check — confirms the API is running |
| `POST` | `/search/text` | Text query search, returns ranked matches with similarity scores |
| `POST` | `/search/image` | Image upload search, ranked by visual similarity |
| `POST` | `/search/multimodal` | Combined image + text search |
| `GET` | `/products` | Returns all products in the dataset |
| `GET` | `/products/{product_id}` | Returns details for a single product |

<details>
<summary><b>📦 Example payloads</b></summary>
<br>

**Text search**
```json
{ "query": "black running shoes", "top_k": 10 }
```

**Multimodal search** (form data)
```
image: <file>  (optional)
query: "under ₹3000"  (optional)
image_weight: 0.6
text_weight: 0.4
```

</details>

<br>

## 📁 Project Structure

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
│   ├── models/             # Pydantic Request/Response Data Schemas
│   ├── routes/             # Search & Product API Endpoints
│   ├── services/           # SearchService wrapping AI Engine & Index
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

<br>

## 🔮 Future Improvements

| Idea | Goal |
|---|---|
| **Larger Dataset** | Scale to 100,000+ products with HNSW FAISS indices |
| **Fine-Tuned Fashion CLIP** | Higher precision on e-commerce product domain pairs |
| **Personalized Recommender** | Factor in click history and price affinity |
| **Multilingual Search** | Multi-language queries via multilingual CLIP models |
| **Hybrid Filtering** | Vector search pre-filtered by price, brand and size |

<br>

<div align="center">

*Multimodal Product Search: find it, however you describe it.*

</div>
