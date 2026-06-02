# Smart Movie Retention System 

An end-to-end, AI-powered movie recommendation engine designed to reduce customer churn through highly personalized content delivery. Built with **LightGBM** and **FastAPI**, this system combines collaborative filtering with content-based features to predict user preferences and serve dynamic recommendations via a sleek web interface.

## The Business Problem
Streaming platforms face high **Customer Churn** rates due to the "choice paralysis" phenomenon — users find it difficult to discover relevant content among thousands of available movies. 

Furthermore, the existing email marketing process is highly inefficient: campaigns are created manually, contain the same generic recommendations for everyone (e.g., "Top 10 New Releases of the Week"), and consequently suffer from low Open Rates and Click-Through Rates (CTR). As a result, the company bleeds money on constantly acquiring new customers instead of effectively retaining existing ones.

## The AI Solution
This project solves the retention problem by replacing generic manual curation with a **Machine Learning pipeline**. By analyzing historical user interactions and movie metadata (genres, release years), the LightGBM model predicts the exact probability of a user enjoying a specific movie. This allows the business to automate personalized marketing and transform the user dashboard into a highly engaging, tailored experience.

## Tech Stack
* **Machine Learning:** Python, Pandas, Scikit-learn, LightGBM
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Frontend:** HTML, CSS, JavaScript (Vanilla), Promise-based async rendering
* **External APIs:** OMDb API (for real-time poster fetching)

## Key Features
* **Hybrid Recommendation Engine:** Handles complex categorical data and missing values to prevent popularity bias, trained with smart negative sampling.
* **Blazing-Fast REST API:** FastAPI backend capable of serving AI predictions in milliseconds.
* **Interactive UI:** Clean, responsive frontend with parallel image loading (`Promise.all()`) to eliminate waterfall rendering delays.
* **Transparency Mode:** A "Show AI Scores" toggle that reveals the model's exact match probability percentages for each user.

## Repository Structure
* `data/preprocessed/` - Contains the cleaned datasets and feature matrices (ready for direct inference).
* `models/` - Contains the pre-trained LightGBM model (`lightgbm_hybrid_final.txt`).
* `src/backend.py` - The FastAPI application serving the recommendation logic.
* `frontend/index.html` - The web application interface.
* `notebooks/` - Jupyter notebooks containing the full EDA, data preprocessing, and model training pipelines.

> **Note:** To ensure the mock database works perfectly out of the box, the preprocessed sample data and the trained model are included in this repository. You do not need to run the data preprocessing notebooks to start the web application.

## How to Run the Application Locally

### 1. Clone the repository
```bash
git clone <your-github-repo-url>
cd <your-repo-folder>
```

### 2. Set up the Environment
Ensure you have Python installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Add your OMDb API Key
To display movie posters, you need a free API key from [OMDb API](http://www.omdbapi.com/).

1. Open `frontend/index.html`.
2. Locate the API key variable (around line 74): `const OMDB_API_KEY = 'YOUR_KEY_HERE';`
3. Replace the placeholder with your actual API key.

### 4. Start the Backend Server
Run the following command from the root directory of the project:

```bash
uvicorn src.backend:app --reload
```
### 5. Open the Frontend
Using VS Code, open the index.html and press F5 or use the "Live Server" extension.

## Application Overview 

https://github.com/user-attachments/assets/c5e94b7a-ffa6-4249-8ccf-810bd53f5630
