"""Complete AI-powered restaurant recommendation pipeline."""

from src.AI.qwen import extract_preferences
from src.AI.restaurant_filter import (
    load_restaurants,
    filter_restaurants,
)
from src.AI.explainer import explain_recommendation
from src.recommendation.query_ranker import rank_candidates


def recommend_from_text(
    user_request,
    top_k=10,
):
    # 1. Understand the user's request.
    preferences = extract_preferences(
        user_request
    )

    # 2. Load restaurant data.
    restaurants = load_restaurants()

    # 3. Filter restaurants using the
    # structured preferences from Qwen.
    filtered_restaurants = filter_restaurants(
        restaurants,
        preferences,
    )

    if filtered_restaurants.empty:
        return preferences, filtered_restaurants

    # 4. Get candidate restaurant IDs.
    candidate_restaurant_ids = (
        filtered_restaurants[
            "restaurant_id"
        ].tolist()
    )

    # 5. Rank the candidates.
    ranked_restaurants = rank_candidates(
        restaurants=restaurants,
        candidate_restaurant_ids=(
            candidate_restaurant_ids
        ),
        user_request=user_request,
    )

    # 6. Return top recommendations.
    return (
        preferences,
        ranked_restaurants.head(top_k),
    )


def main():
    user_request = (
        "I want a cheap Japanese restaurant "
        "in Kuala Lumpur with good ratings."
    )

    preferences, recommendations = (
        recommend_from_text(
            user_request,
            top_k=5,
        )
    )

    print("=" * 60)
    print("USER REQUEST")
    print("=" * 60)
    print(user_request)

    print("\n" + "=" * 60)
    print("EXTRACTED PREFERENCES")
    print("=" * 60)
    print(preferences)

    if recommendations.empty:
        print("\nNo restaurants matched your preferences.")
        return

    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    for _, restaurant in recommendations.iterrows():

        print(
            f"\n{restaurant['name']} "
            f"({restaurant['restaurant_id']})"
        )

        print(
            f"Cuisine: {restaurant['cuisine']}"
        )

        print(
            f"Price: {restaurant['price_range']}"
        )

        print(
            f"Rating: {restaurant['rating']}"
        )

        print(
            f"Reviews: {restaurant['review_count']}"
        )

        print(
            f"Query score: "
            f"{restaurant['query_score']:.4f}"
        )

        # 7. Ask Qwen to explain the recommendation.
        explanation = explain_recommendation(
            user_request=user_request,
            restaurant=restaurant,
        )

        print(
            f"Why: {explanation}"
        )


if __name__ == "__main__":
    main()