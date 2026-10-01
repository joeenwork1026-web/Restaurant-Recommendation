"""Complete AI-powered restaurant recommendation pipeline."""

from src.AI.qwen import extract_preferences
from src.AI.restaurant_filter import (
    load_restaurants,
    filter_restaurants,
)
from src.recommendation.query_ranker import rank_candidates


def recommend_from_text(
    user_request,
    top_k=10,
):
    # 1. Let Qwen understand the user's request
    preferences = extract_preferences(
        user_request
    )

    # 2. Load restaurants
    restaurants = load_restaurants()

    # 3. Try exact matching first
    filtered_restaurants = filter_restaurants(
        restaurants,
        preferences,
    )

    match_type = "exact"

    # 4. If no exact match,
    #    relax the price restriction
    if filtered_restaurants.empty:
        fallback_preferences = preferences.copy()
        fallback_preferences["price_range"] = None

        filtered_restaurants = filter_restaurants(
            restaurants,
            fallback_preferences,
        )

        match_type = "relaxed_price"

    # 5. If still no results,
    #    relax both price and city
    if filtered_restaurants.empty:
        fallback_preferences = preferences.copy()
        fallback_preferences["price_range"] = None
        fallback_preferences["city"] = None

        filtered_restaurants = filter_restaurants(
            restaurants,
            fallback_preferences,
        )

        match_type = "similar"

    # 6. Nothing found even after fallback
    if filtered_restaurants.empty:
        return (
            preferences,
            filtered_restaurants,
            "none",
        )

    # 7. Rank the candidates
    candidate_restaurant_ids = (
        filtered_restaurants[
            "restaurant_id"
        ].tolist()
    )

    ranked_restaurants = rank_candidates(
        restaurants=restaurants,
        candidate_restaurant_ids=(
            candidate_restaurant_ids
        ),
        user_request=user_request,
    )

    return (
        preferences,
        ranked_restaurants.head(top_k),
        match_type,
    )