"""Rank restaurants for a natural-language user query."""

import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(
        os.path.join(script_dir, "..", "..")
    )
    return os.path.join(project_root, "data")


def load_restaurants():
    data_dir = project_paths()

    return pd.read_csv(
        os.path.join(data_dir, "restaurants.csv")
    )


def build_restaurant_text(restaurants):
    return (
        restaurants["cuisine"].fillna("")
        + " "
        + restaurants["categories"].fillna("")
        + " "
        + restaurants["description"].fillna("")
    )


def rank_candidates(
    restaurants,
    candidate_restaurant_ids,
    user_request,
    popularity_weight=0.3,
    content_weight=0.7,
):
    candidates = restaurants[
        restaurants["restaurant_id"].isin(
            candidate_restaurant_ids
        )
    ].copy()

    if candidates.empty:
        return candidates

    # Build TF-IDF representation of all restaurants.
    all_text = build_restaurant_text(restaurants)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    restaurant_matrix = vectorizer.fit_transform(
        all_text
    )

    # Convert the user's natural-language request
    # into the same TF-IDF space.
    query_vector = vectorizer.transform(
        [user_request]
    )

    content_scores = cosine_similarity(
        query_vector,
        restaurant_matrix,
    )[0]

    score_table = restaurants[
        ["restaurant_id"]
    ].copy()

    score_table["content_score"] = content_scores

    candidates = candidates.merge(
        score_table,
        on="restaurant_id",
        how="left",
    )

    # Normalize restaurant popularity using review count.
    max_reviews = candidates["review_count"].max()

    if max_reviews == 0:
        candidates["popularity_score"] = 0.0
    else:
        candidates["popularity_score"] = (
            candidates["review_count"]
            / max_reviews
        )

    candidates["query_score"] = (
        content_weight
        * candidates["content_score"]
        + popularity_weight
        * candidates["popularity_score"]
    )

    candidates = candidates.sort_values(
        "query_score",
        ascending=False,
    )

    return candidates.reset_index(drop=True)


def main():
    restaurants = load_restaurants()

    candidate_ids = [
        "R015",
    ]

    user_request = (
        "I want a cheap Japanese restaurant "
        "in Kuala Lumpur with good ratings."
    )

    recommendations = rank_candidates(
        restaurants=restaurants,
        candidate_restaurant_ids=candidate_ids,
        user_request=user_request,
    )

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "price_range",
        "rating",
        "review_count",
        "content_score",
        "popularity_score",
        "query_score",
    ]

    print(
        recommendations[columns].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()