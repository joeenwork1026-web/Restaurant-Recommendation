"""FastAPI backend for the restaurant recommendation system."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.AI.ai_recommender import recommend_from_text
from src.AI.explainer import explain_recommendation
from src.AI.restaurant_filter import load_restaurants
from src.AI.restaurant_images import (
    image_url_for_restaurant,
    image_urls_for_restaurant,
)


app = FastAPI(
    title="Restaurant Recommendation API",
    description="AI-powered restaurant recommendation system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    user_request: str
    top_k: int = 5


def restaurant_to_dict(restaurant, explanation=None):
    item = {
        "restaurant_id": restaurant["restaurant_id"],
        "name": restaurant["name"],
        "cuisine": restaurant["cuisine"],
        "price_range": restaurant["price_range"],
        "rating": float(restaurant["rating"]),
        "review_count": int(restaurant["review_count"]),
        "city": restaurant["city"],
        "image_url": image_url_for_restaurant(restaurant),
        "image_urls": image_urls_for_restaurant(restaurant),
    }
    if explanation is not None:
        item["explanation"] = explanation
    return item


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


@app.get("/cuisines")
def list_cuisines():
    restaurants = load_restaurants()
    counts = (
        restaurants.groupby("cuisine")
        .size()
        .reset_index(name="count")
        .sort_values("cuisine")
    )
    return {
        "cuisines": counts.to_dict(orient="records"),
    }


@app.get("/restaurants")
def list_restaurants_by_cuisine(
    cuisine: str,
    limit: int = 20,
):
    restaurants = load_restaurants()
    filtered = restaurants[
        restaurants["cuisine"].str.lower() == cuisine.strip().lower()
    ].copy()

    if filtered.empty:
        return {
            "cuisine": cuisine,
            "count": 0,
            "restaurants": [],
        }

    filtered = filtered.sort_values(
        by=["rating", "review_count"],
        ascending=[False, False],
    ).head(limit)

    return {
        "cuisine": cuisine,
        "count": len(filtered),
        "restaurants": [
            restaurant_to_dict(row)
            for _, row in filtered.iterrows()
        ],
    }


@app.post("/recommend")
def recommend(request: RecommendationRequest):

    preferences, recommendations, match_type = (
    recommend_from_text(
        user_request=request.user_request,
        top_k=request.top_k,
    )
)

    recommendation_list = []

    for _, restaurant in recommendations.iterrows():

        explanation = explain_recommendation(
            user_request=request.user_request,
            restaurant=restaurant,
        )

        item = restaurant_to_dict(restaurant, explanation=explanation)
        item["content_score"] = float(restaurant["content_score"])
        item["popularity_score"] = float(restaurant["popularity_score"])
        item["query_score"] = float(restaurant["query_score"])
        recommendation_list.append(item)

    return {
    "user_request": request.user_request,
    "preferences": preferences,
    "match_type": match_type,
    "recommendations": recommendation_list,
}