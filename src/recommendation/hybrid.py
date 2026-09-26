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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(
        os.path.join(script_dir, "..", "..")
    )
    data_dir = os.path.join(project_root, "data")
    return data_dir


def min_max_normalize(scores):
    if scores.empty:
        return scores

    minimum = scores.min()
    maximum = scores.max()

    if maximum == minimum:
        return pd.Series(0.0, index=scores.index)

    return (scores - minimum) / (maximum - minimum)


def get_recommendation_scores(
    user_id,
    top_k=10,
    interactions=None,
):
    content_scores = content_recommend(
        user_id=user_id,
        top_k=top_k,
        interactions=interactions,
    )

    collaborative_scores = collaborative_recommend(
        user_id=user_id,
        top_k=top_k,
        similar_user_count=10,
        minimum_similarity=0.0,
        interactions=interactions,
    )

    popularity_table = get_popular_restaurants(
        top_k=top_k,
        interactions=interactions,
    )

    popularity_scores = (
        popularity_table
        .set_index("restaurant_id")["popularity"]
    )

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
    content_scores = (
        content_scores
        .set_index("restaurant_id")["similarity"]
    )

    collaborative_scores = (
        collaborative_scores
        .set_index("restaurant_id")["collaborative_score"]
    )

    popularity_scores = popularity_scores

    scores = pd.concat(
        [
            content_scores.rename("content"),
            collaborative_scores.rename("collaborative"),
            popularity_scores.rename("popularity"),
        ],
        axis=1,
    )

    scores = scores.fillna(0)

    return scores


def normalize_score_table(scores):
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


def remove_seen_restaurants(
    recommendations,
    user_id,
    interactions,
):
    seen_restaurants = set(
        interactions.loc[
            interactions["user_id"] == user_id,
            "restaurant_id",
        ]
    )

    recommendations = recommendations[
        ~recommendations.index.isin(seen_restaurants)
    ]

    return recommendations


def add_restaurant_details(hybrid_scores):
    data_dir = project_paths()

    restaurants = pd.read_csv(
        os.path.join(data_dir, "restaurants.csv")
    )

    recommendations = (
        hybrid_scores
        .rename_axis("restaurant_id")
        .reset_index()
    )

    recommendations = recommendations.merge(
        restaurants,
        on="restaurant_id",
        how="left",
    )

    return recommendations


def recommend_for_user(
    user_id,
    top_k=10,
    content_weight=0.4,
    collaborative_weight=0.4,
    popularity_weight=0.2,
    interactions=None,
    candidate_restaurant_ids=None,
):
    if interactions is None:
        data_dir = project_paths()

        interactions = pd.read_csv(
            os.path.join(
                data_dir,
                "interactions.csv",
            )
        )

    else:
        interactions = interactions.copy()

    (
        content_scores,
        collaborative_scores,
        popularity_scores,
    ) = get_recommendation_scores(
        user_id=user_id,
        top_k=top_k,
        interactions=interactions,
    )

    combined_scores = combine_score_tables(
        content_scores,
        collaborative_scores,
        popularity_scores,
    )

    normalized_scores = normalize_score_table(
        combined_scores
    )

    hybrid_scores = calculate_hybrid_score(
        normalized_scores,
        content_weight=content_weight,
        collaborative_weight=collaborative_weight,
        popularity_weight=popularity_weight,
    )

    # If candidate restaurants were provided,
    # only keep those restaurants.
    if candidate_restaurant_ids is not None:
        hybrid_scores = hybrid_scores[
            hybrid_scores.index.isin(
                candidate_restaurant_ids
            )
        ]

    hybrid_scores = remove_seen_restaurants(
        hybrid_scores,
        user_id,
        interactions,
    )

    hybrid_scores = hybrid_scores.head(top_k)

    recommendations = add_restaurant_details(
        hybrid_scores
    )

    return recommendations


def main():
    recommendations = recommend_for_user(
        user_id="U001",
        top_k=10,
        content_weight=0.4,
        collaborative_weight=0.4,
        popularity_weight=0.2,
    )

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "price_range",
        "rating",
        "content",
        "collaborative",
        "popularity",
        "hybrid_score",
    ]

    print(
        recommendations[columns].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()