"""Hybrid restaurant recommendation system."""

import os
import pandas as pd

from src.recommendation.content_based import (
    recommend_for_user as content_recommend,
)
from src.recommendation.collaborative import (
    recommend_for_user as collaborative_recommend,
)
from src.recommendation.popularity import (
    get_popular_restaurants,
)

def project_paths():
    """Find the project's data folder."""

    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.abspath(
        os.path.join(script_dir, "..", "..")
    )

    return os.path.join(project_root, "data")

def min_max_normalize(scores):
    """Convert scores to a 0-1 range."""

    if scores.empty:
        return scores

    min_score = scores.min()
    max_score = scores.max()

    # Avoid division by zero if all scores are identical.
    if max_score == min_score:
        return pd.Series(0.0, index=scores.index)

    return (scores - min_score) / (max_score - min_score)

def get_recommendation_scores(user_id, top_k=10):
    """Get recommendation scores from all three models."""

    content_scores = content_recommend(
        user_id,
        top_k=top_k,
    )

    collaborative_scores = collaborative_recommend(
        user_id,
        top_k=top_k,
    )

    popularity_table = get_popular_restaurants(
        top_k=top_k,
    )

    popularity_scores = popularity_table.set_index(
        "restaurant_id"
    )["popularity"]

    return (
        content_scores,
        collaborative_scores,
        popularity_scores,
    )

def combine_score_tables(
    content_scores,
    collaborative_scores,
    popularity_scores,
):
    """Combine scores from the three recommendation models."""

    # Content-based returns a DataFrame.
    # Keep only restaurant ID and similarity score.
    content_scores = content_scores.set_index(
        "restaurant_id"
    )["similarity"]

    scores = pd.concat(
        [
            content_scores.rename("content"),
            collaborative_scores.rename("collaborative"),
            popularity_scores.rename("popularity"),
        ],
        axis=1,
    )

    # If a restaurant was not recommended by a model,
    # give it a score of 0.
    scores = scores.fillna(0)

    return scores

def normalize_score_table(scores):
    """Normalize each recommendation model to a 0-1 range."""

    normalized = scores.copy()

    normalized["content"] = min_max_normalize(
        normalized["content"]
    )

    normalized["collaborative"] = min_max_normalize(
        normalized["collaborative"]
    )

    normalized["popularity"] = min_max_normalize(
        normalized["popularity"]
    )

    return normalized

def calculate_hybrid_score(
    normalized_scores,
    content_weight=0.4,
    collaborative_weight=0.4,
    popularity_weight=0.2,
):
    """Calculate the final weighted hybrid recommendation score."""

    scores = normalized_scores.copy()

    scores["hybrid_score"] = (
        content_weight * scores["content"]
        + collaborative_weight * scores["collaborative"]
        + popularity_weight * scores["popularity"]
    )

    return scores.sort_values(
        "hybrid_score",
        ascending=False,
    )

def recommend_for_user(
    user_id,
    top_k=10,
    content_weight=0.4,
    collaborative_weight=0.4,
    popularity_weight=0.2,
):
    """Generate hybrid restaurant recommendations for a user."""

    # 1. Get scores from all three recommendation models.
    content_scores, collaborative_scores, popularity_scores = (
        get_recommendation_scores(
            user_id,
            top_k=top_k,
        )
    )

    # 2. Combine the three score tables.
    combined_scores = combine_score_tables(
        content_scores,
        collaborative_scores,
        popularity_scores,
    )

    # 3. Normalize all model scores to 0-1.
    normalized_scores = normalize_score_table(
        combined_scores
    )

    # 4. Calculate the final weighted hybrid score.
    hybrid_scores = calculate_hybrid_score(
        normalized_scores,
        content_weight=content_weight,
        collaborative_weight=collaborative_weight,
        popularity_weight=popularity_weight,
    )

    # 5. Keep only the top K recommendations.
    hybrid_scores = hybrid_scores.head(top_k)

    # 6. Add restaurant information.
    recommendations = add_restaurant_details(
        hybrid_scores
    )

    return recommendations

def add_restaurant_details(hybrid_scores):
    """Add restaurant information to the hybrid recommendations."""

    data_dir = project_paths()

    restaurants = pd.read_csv(
        os.path.join(data_dir, "restaurants.csv")
    )

    recommendations = hybrid_scores.reset_index()

    recommendations = recommendations.merge(
        restaurants,
        on="restaurant_id",
        how="left",
    )

    return recommendations