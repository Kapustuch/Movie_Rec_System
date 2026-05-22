from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import lightgbm as lgb
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# MOCK DATABASE
MOCK_USER_DB = {
    "yuriikapusta@gmail.com": {"password": "12345", "userId": 97735},
    "daniiltaran@gmail.com": {"password": "12345", "userId": 103943},
    "oscar@gmail.com": {"password": "12345", "userId": 49018},
    "james@gmail.com": {"password": "12345", "userId": 27531},
    "harry@gmail.com": {"password": "12345", "userId": 43143},
    "oliver@gmail.com": {"password": "12345", "userId": 138289},
    "jack@gmail.com": {"password": "12345", "userId": 138166},
    "john@gmail.com": {"password": "12345", "userId": 138164},
    "george@gmail.com": {"password": "12345", "userId": 89575}
}

# Define the request body model for login credentials
class LoginRequest(BaseModel):
    email: str
    password: str

# DATA & MODEL LOADING
production_model = lgb.Booster(model_file='models/lightgbm_hybrid_final.txt')

interactions_df = pd.read_csv('data/preprocessed/ratings_cleaned.csv') 
movies_features = pd.read_pickle('data/preprocessed/movies_features_lgbm.pkl')
movies_df = pd.read_csv('data/preprocessed/movies_cleaned.csv') 

# RECOMMENDATION LOGIC 
def get_recommendations_hybrid(user_id, model, interactions_df, movies_features_df, top_n=10):
    # Find movies the user has already interacted with
    seen_movies = interactions_df[interactions_df['userId'] == user_id]['movieId'].unique()
    all_movies = movies_features_df['movieId'].unique()
    
    # Filter out seen movies to get valid candidates
    unseen_movies = list(set(all_movies) - set(seen_movies))
    
    candidates = pd.DataFrame({'movieId': unseen_movies})
    candidates['userId'] = user_id
    
    # Merge with movie attributes (genres, year, etc.)
    candidates = candidates.merge(movies_features_df, on='movieId', how='left')
    
    # Ensure categorical types are preserved for LightGBM
    candidates['userId'] = candidates['userId'].astype('category')
    
    # Prepare features for prediction (exclude target IDs)
    features_to_predict = [col for col in candidates.columns if col not in ['movieId']]
    X_pred = candidates[features_to_predict]
    
    # Generate probability scores
    candidates['prediction_score'] = model.predict(X_pred)
    
    # Sort movies by score in descending order and select Top-N
    top_recs = candidates.sort_values(by='prediction_score', ascending=False).head(top_n)
    return top_recs[['movieId', 'prediction_score']]

# API ENDPOINTS

@app.post("/login")
async def login(credentials: LoginRequest):
    user_data = MOCK_USER_DB.get(credentials.email)
    
    # Validate credentials
    if user_data and user_data["password"] == credentials.password:
        return {"success": True, "userId": user_data["userId"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: int):
    top_recs = get_recommendations_hybrid(
        user_id=user_id, 
        model=production_model, 
        interactions_df=interactions_df,
        movies_features_df=movies_features, 
        top_n=5 # Limit to Top-5 for UI rendering
    )
    
    # Join with the golden source metadata to get actual titles and genres
    final_output = top_recs.merge(movies_df[['movieId', 'title', 'genres', 'imdbId']], on='movieId', how='left')
    
    result = []
    for _, row in final_output.iterrows():
        # Safely handle potential missing IMDb IDs
        imdb_id_str = str(int(row['imdbId'])) if pd.notna(row['imdbId']) else "0"
        
        result.append({
            "title": row['title'],
            "genre": row['genres'],
            "imdbId": imdb_id_str,
            "score": float(row['prediction_score']) # <--- Add this line!
        })
    
    return result