"""Content-based restaurant recommendations using TF-IDF."""

import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Stronger interactions indicate stronger user preference.
INTERACTION_WEIGHTS = {
    "view": 1,
    "click": 2,
    "like": 3,
    "save": 4,
    "visit": 5,
    "rating": 5,
}


def project_paths():
    """Find the project's data folder."""

    # This file is in src/recommendation/
    # so we go up two folders to reach the project root.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(
        os.path.join(script_dir, "..", "..")
    )

    return os.path.join(project_root, "data")


def prepare():
    """Load data and create TF-IDF and similarity matrix."""

    data_dir = project_paths()

    # Load restaurant data
    restaurants = pd.read_csv(
        os.path.join(data_dir, "restaurants.csv")
    )

    # Load user interaction data
    interactions = pd.read_csv(
        os.path.join(data_dir, "interactions.csv")
    )

    # Combine restaurant information into one text field.
    # TF-IDF will use this text to understand restaurant similarity.
    restaurants["content_text"] = (
        restaurants["cuisine"].fillna("")
        + " "
        + restaurants["categories"].fillna("")
        + " "
        + restaurants["description"].fillna("")
    )

    # Convert restaurant text into TF-IDF vectors.
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        restaurants["content_text"]
    )

    # Calculate similarity between every pair of restaurants.
    similarity_matrix = cosine_similarity(
        tfidf_matrix
    )

    # Map restaurant ID to its row number in the similarity matrix.
    id_to_index = {
        restaurant_id: i
        for i, restaurant_id in enumerate(
            restaurants["restaurant_id"]
        )
    }

    return (
        restaurants,
        interactions,
        similarity_matrix,
        id_to_index,
    )


def get_similar_restaurants(restaurant_id, top_k=10):
    """Find restaurants similar to a given restaurant."""

    (
        restaurants,
        _,
        similarity_matrix,
        id_to_index,
    ) = prepare()

    # Check whether the restaurant exists.
    if restaurant_id not in id_to_index:
        raise ValueError(
            f"Unknown restaurant_id: {restaurant_id}"
        )

    # Find the restaurant's row in the similarity matrix.
    index = id_to_index[restaurant_id]

    # Get similarity scores between this restaurant
    # and every other restaurant.
    scores = similarity_matrix[index]

    # Copy restaurant information.
    similar = restaurants.copy()

    # Add similarity scores.
    similar["similarity"] = scores

    # Remove the restaurant itself.
    similar = similar[
        similar["restaurant_id"] != restaurant_id
    ]

    # Highest similarity first.
    similar = similar.sort_values(
        "similarity",
        ascending=False,
    )

    return similar.head(top_k).reset_index(drop=True)


def recommend_for_user(user_id, top_k=10):
    """Recommend restaurants based on the user's interaction history."""

    (
        restaurants,
        interactions,
        similarity_matrix,
        id_to_index,
    ) = prepare()

    # Get all interactions for this user.
    user_interactions = interactions[
        interactions["user_id"] == user_id
    ].copy()

    if len(user_interactions) == 0:
        raise ValueError(
            f"No interactions found for user_id: {user_id}"
        )

    # Convert interaction types into preference weights.
    user_interactions["weight"] = (
        user_interactions["event_type"]
        .map(INTERACTION_WEIGHTS)
        .fillna(1)
    )

    # Get the restaurants this user has interacted with.
    seen_ids = user_interactions["restaurant_id"].unique()

    # Keep only restaurants that exist in our restaurant catalog.
    valid_seen_ids = [
        rid for rid in seen_ids
        if rid in id_to_index
    ]

    if len(valid_seen_ids) == 0:
        raise ValueError(
            f"No matching restaurants found for user_id: {user_id}"
        )

    # Convert restaurant IDs into row positions.
    seen_indexes = [
        id_to_index[rid]
        for rid in valid_seen_ids
    ]

    # Calculate total interaction weight for each restaurant.
    weights = []

    for restaurant_id in valid_seen_ids:

        restaurant_weight = user_interactions.loc[
            user_interactions["restaurant_id"] == restaurant_id,
            "weight",
        ].sum()

        weights.append(restaurant_weight)

    # Convert weights into a NumPy column vector.
    weights = np.array(weights).reshape(-1, 1)

    # Get similarity scores for the user's restaurants.
    user_similarity = similarity_matrix[seen_indexes]

    # Apply each restaurant's interaction weight.
    weighted_similarity = user_similarity * weights

    # Add the weighted scores together.
    combined_scores = weighted_similarity.sum(axis=0)

    # Create recommendation table.
    ranked = restaurants.copy()

    ranked["similarity"] = combined_scores

    # Don't recommend restaurants the user has already interacted with.
    ranked = ranked[
        ~ranked["restaurant_id"].isin(seen_ids)
    ]

    # Highest recommendation score first.
    ranked = ranked.sort_values(
        "similarity",
        ascending=False,
    )

    return ranked.head(top_k).reset_index(drop=True)


def main():

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "rating",
        "similarity",
    ]

    # ---------------------------------------------------------
    # Test 1: Similar restaurants
    # ---------------------------------------------------------

    print("Restaurants similar to R001:")

    print(
        get_similar_restaurants(
            "R001",
            top_k=10,
        )[columns].to_string(index=False)
    )

    # ---------------------------------------------------------
    # Test 2: Personalized recommendations
    # ---------------------------------------------------------

    print("\nRecommendations for user U001:")

    print(
        recommend_for_user(
            "U001",
            top_k=10,
        )[columns].to_string(index=False)
    )


if __name__ == "__main__":
    main()