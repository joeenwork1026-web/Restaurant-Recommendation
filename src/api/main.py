"""FastAPI backend for the restaurant recommendation system."""

from fastapi import FastAPI
from pydantic import BaseModel

from src.AI.ai_recommender import recommend_from_text
from src.AI.explainer import explain_recommendation


app = FastAPI(
    title="Restaurant Recommendation API",
    description="AI-powered restaurant recommendation system",
    version="1.0.0",
)


class RecommendationRequest(BaseModel):
    user_request: str
    top_k: int = 5


@app.get("/")
def root():
    return {
        "message": "Restaurant Recommendation API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/recommend")
def recommend(request: RecommendationRequest):

    preferences, recommendations = recommend_from_text(
        user_request=request.user_request,
        top_k=request.top_k,
    )

    recommendation_list = []

    for _, restaurant in recommendations.iterrows():

        explanation = explain_recommendation(
            user_request=request.user_request,
            restaurant=restaurant,
        )

        recommendation_list.append(
            {
                "restaurant_id": restaurant["restaurant_id"],
                "name": restaurant["name"],
                "cuisine": restaurant["cuisine"],
                "price_range": restaurant["price_range"],
                "rating": restaurant["rating"],
                "review_count": int(
                    restaurant["review_count"]
                ),
                "city": restaurant["city"],
                "content_score": float(
                    restaurant["content_score"]
                ),
                "popularity_score": float(
                    restaurant["popularity_score"]
                ),
                "query_score": float(
                    restaurant["query_score"]
                ),
                "explanation": explanation,
            }
        )

    return {
        "user_request": request.user_request,
        "preferences": preferences,
        "recommendations": recommendation_list,
    }