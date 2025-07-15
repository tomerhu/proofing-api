# proofing-api
Proofreading API MVP: automated grammar &amp; spelling correction.

## Project Vision
An MVP API for automated Hebrew text proofreading, offering:
- Spelling correction  
- Grammar suggestions  
- Style consistency  
- A RESTful interface for editor & web-app integration

## Getting Started
1. Install Python 3.10+  
2. Set up a virtualenv: `python -m venv .venv` & `.\.venv\Scripts\Activate.ps1`  
3. `pip install -r requirements.txt`  
4. `docker compose up -d`  
5. `uvicorn app.main:app --reload`  
