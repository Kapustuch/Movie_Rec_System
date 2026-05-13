from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import lightgbm as lgb
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Data
production_model = lgb.Booster(model_file='models/lightgbm_hybrid_final.txt')

interactions_df = pd.read_csv('data/preprocessed/ratings_cleaned.csv') 
movies_features = pd.read_pickle('data/preprocessed/movies_features_lgbm.pkl')
movies_df = pd.read_csv('data/preprocessed/movies_cleaned.csv') 

def get_recommendations_hybrid(user_id, model, interactions_df, movies_features_df, top_n=10):
    # 1. Find movies the user has already interacted with
    seen_movies = interactions_df[interactions_df['userId'] == user_id]['movieId'].unique()
    
    # 2. Get a list of all available movies in the catalog
    all_movies = movies_features_df['movieId'].unique()
    
    # 3. Filter out the seen movies to get candidates
    unseen_movies = list(set(all_movies) - set(seen_movies))
    
    # 4. Create a DataFrame for the candidates
    candidates = pd.DataFrame({'movieId': unseen_movies})
    
    # Assign the current user_id to all candidate rows
    candidates['userId'] = user_id
    
    # 5. Merge with movie attributes (year, genres)
    candidates = candidates.merge(movies_features_df, on='movieId', how='left')
    
    # Ensure categorical types are preserved for LightGBM
    candidates['userId'] = candidates['userId'].astype('category')
    
    # 6. Prepare features for prediction
    features_to_predict = [col for col in candidates.columns if col not in ['movieId']]
    X_pred = candidates[features_to_predict]
    
    # 7. Generate probability scores
    candidates['prediction_score'] = model.predict(X_pred)
    
    # 8. Sort movies by score in descending order and select Top-N
    top_recs = candidates.sort_values(by='prediction_score', ascending=False).head(top_n)
    
    # Return the movie IDs and their scores
    return top_recs[['movieId', 'prediction_score']]

# Create API endpoint
@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: int):
    top_recs = get_recommendations_hybrid(
        user_id=user_id, 
        model=production_model, 
        interactions_df=interactions_df,
        movies_features_df=movies_features, 
        top_n=5
    )
    
    final_output = top_recs.merge(movies_df[['movieId', 'title', 'genres', 'imdbId']], on='movieId', how='left')
    
    result = []
    for _, row in final_output.iterrows():
        imdb_id_str = str(int(row['imdbId'])) if pd.notna(row['imdbId']) else "0"
        
        result.append({
            "title": row['title'],
            "genre": row['genres'],
            "imdbId": imdb_id_str
        })
    
    return result