# E-Commerce Screenshot Analyzer

A Python application that extracts product information from e-commerce screenshots using OCR and recommends cheaper alternatives. Supports both mobile and desktop screenshots, and allows experimentation with EasyOCR and Donut models.

---

## Features

- Extract text from screenshots (mobile & desktop)
- Detect product name, price, and rating
- Recommend cheaper alternatives using SerpAPI or DuckDuckGo
- FastAPI backend with optional Streamlit frontend

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <repo-folder> 
```
2. Create and activate a virtual environment: 
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
Or a Conda environment 
```bash
conda create --name my_env python=3.10
conda activate my_env
```
3. Install dependencies 
```bash
pip install -r requirements.txt 
```
4. Create ```.env``` file
```bash
SERPAPI_KEY=your_serpapi_key
GEMINI_API_KEY=your_gemini_key
```
5. Run API backend
```bash 
uvicorn src.api.main:app --reload
```
6. Run Streamlit frontend 
```bash
streamlit run src/app_api.py
```
Or without running the API 
```bash
streamlit run src/app.py
```