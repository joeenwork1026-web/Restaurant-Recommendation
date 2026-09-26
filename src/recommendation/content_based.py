"""Content-based restaurant recommendation system."""

import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


INTERACTION_WEIGHTS = {
    "view": 1,
    "click": 2,
    "like": 3,
    "save": 4,
    "visit": 5,
    "rating": 5,
}


def project_paths():
    """Return the path to the project's data directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    project_root = os.path.abspath(
        os.path.join(script_dir, "..", "..")
    )

    return os.path.join(project_root, "data")


def prepare(interactions=None):
    """Load data and create restaurant TF-IDF vectors."""

    data_dir = project_paths()

    restaurants = pd.read_csv(
        os.path.join(
            data_dir,
            "restaurants.csv",
        )
    )

    if interactions is None:
        interactions = pd.read_csv(
            os.path.join(
                data_dir,
                "interactions.csv",
            )
        )
    else:
        interactions = interactions.copy()

    restaurants["content_text"] = (
        restaurants["cuisine"].fillna("")
        + " "
        + restaurants["categories"].fillna("")
        + " "
        + restaurants["description"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        restaurants["content_text"]
    )

    similarity_matrix = cosine_similarity(
        tfidf_matrix
    )

    id_to_index = {
        restaurant_id: index
        for index, restaurant_id
        in enumerate(restaurants["restaurant_id"])
    }

    return (
        restaurants,
        interactions,
        tfidf_matrix,
        similarity_matrix,
        id_to_index,
    )


def get_similar_restaurants(
    restaurant_id,
    top_k=10,
):
    """Find restaurants similar to a restaurant."""

    (
        restaurants,
        _,
        _,
        similarity_matrix,
        id_to_index,
    ) = prepare()

    if restaurant_id not in id_to_index:
        raise ValueError(
            f"Unknown restaurant_id: {restaurant_id}"
        )

    index = id_to_index[restaurant_id]

    scores = similarity_matrix[index]

    similar = restaurants.copy()

    similar["similarity"] = scores

    similar = similar[
        similar["restaurant_id"] != restaurant_id
    ]

    similar = similar.sort_values(
        "similarity",
        ascending=False,
    )

    return similar.head(top_k).reset_index(
        drop=True
    )


def build_user_profile(
    user_id,
    interactions,
    tfidf_matrix,
    id_to_index,
):
    """Build a weighted content profile for a user."""

    user_interactions = interactions[
        interactions["user_id"] == user_id
    ].copy()

    if user_interactions.empty:
        raise ValueError(
            f"No interactions found for user_id: {user_id}"
        )

    user_interactions["weight"] = (
        user_interactions["event_type"]
        .map(INTERACTION_WEIGHTS)
        .fillna(1)
    )

    profile_vectors = []
    profile_weights = []

    for _, interaction in user_interactions.iterrows():

        restaurant_id = interaction[
            "restaurant_id"
        ]

        if restaurant_id not in id_to_index:
            continue

        restaurant_index = id_to_index[
            restaurant_id
        ]

        restaurant_vector = tfidf_matrix[
            restaurant_index
        ]

        profile_vectors.append(
            restaurant_vector.toarray()[0]
        )

        profile_weights.append(
            interaction["weight"]
        )

    if not profile_vectors:
        raise ValueError(
            f"No matching restaurants found "
            f"for user_id: {user_id}"
        )

    profile_vectors = np.array(
        profile_vectors
    )

    profile_weights = np.array(
        profile_weights
    )

    user_profile = np.average(
        profile_vectors,
        axis=0,
        weights=profile_weights,
    )

    return user_profile


def recommend_for_user(
    user_id,
    top_k=10,
    interactions=None,
):
    """
    Recommend restaurants based on the user's
    learned content preferences.
    """

    (
        restaurants,
        interactions,
        tfidf_matrix,
        _,
        id_to_index,
    ) = prepare(interactions)

    # Build the user's preference profile.
    user_profile = build_user_profile(
        user_id,
        interactions,
        tfidf_matrix,
        id_to_index,
    )

    # Compare the user's profile against every
    # restaurant.
    scores = cosine_similarity(
        user_profile.reshape(1, -1),
        tfidf_matrix,
    )[0]

    recommendations = restaurants.copy()

    recommendations["similarity"] = scores

    # Remove restaurants the user has already
    # interacted with.
    seen_restaurants = set(
        interactions.loc[
            interactions["user_id"] == user_id,
            "restaurant_id",
        ]
    )

    recommendations = recommendations[
        ~recommendations["restaurant_id"].isin(
            seen_restaurants
        )
    ]

    recommendations = recommendations.sort_values(
        "similarity",
        ascending=False,
    )

    return recommendations.head(
        top_k
    ).reset_index(drop=True)


def main():
    """Run a simple content-based recommendation example."""

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "rating",
        "similarity",
    ]

    print(
        "Restaurants similar to R001:"
    )

    print(
        get_similar_restaurants(
            "R001",
            top_k=10,
        )[columns].to_string(index=False)
    )

    print(
        "\nRecommendations for user U001:"
    )

    print(
        recommend_for_user(
            "U001",
            top_k=10,
        )[columns].to_string(index=False)
    )


if __name__ == "__main__":
    main()