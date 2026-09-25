"""User-based collaborative filtering for restaurant recommendations."""

import os

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# Interaction strength.
# Stronger actions indicate stronger user preference.
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


def load_data():
    """Load interaction data and create the user-item matrix."""

    data_dir = project_paths()

    interactions = pd.read_csv(
        os.path.join(data_dir, "interactions.csv")
    )

    # Convert event types into numerical preference strengths.
    interactions["weight"] = (
        interactions["event_type"]
        .map(INTERACTION_WEIGHTS)
        .fillna(1)
    )

    # Create the user-item interaction matrix.
    #
    # Rows    = users
    # Columns = restaurants
    # Values  = interaction strength
    user_item_matrix = interactions.pivot_table(
        index="user_id",
        columns="restaurant_id",
        values="weight",
        aggfunc="sum",
        fill_value=0,
    )

    return interactions, user_item_matrix


def get_similar_users(user_id, user_item_matrix, top_k=10):
    """Find users with interaction patterns similar to the given user."""

    if user_id not in user_item_matrix.index:
        raise ValueError(
            f"Unknown user_id: {user_id}"
        )

    # Calculate cosine similarity between every pair of users.
    user_similarity = cosine_similarity(
        user_item_matrix
    )

    # Get the row corresponding to the requested user.
    user_index = user_item_matrix.index.get_loc(
        user_id
    )

    similarities = user_similarity[user_index]

    # Create a table containing users and their similarity scores.
    similar_users = pd.DataFrame(
        {
            "user_id": user_item_matrix.index,
            "similarity": similarities,
        }
    )

    # Remove the user themselves.
    similar_users = similar_users[
        similar_users["user_id"] != user_id
    ]

    # Highest similarity first.
    similar_users = similar_users.sort_values(
        "similarity",
        ascending=False,
    )

    return similar_users.head(top_k).reset_index(drop=True)


def recommend_for_user(user_id, top_k=10, similar_user_count=10):
    """Recommend restaurants using similar users' behavior."""

    interactions, user_item_matrix = load_data()

    # ---------------------------------------------------------
    # 1. Find users who behave similarly to this user.
    # ---------------------------------------------------------

    similar_users = get_similar_users(
        user_id,
        user_item_matrix,
        top_k=similar_user_count,
    )

    # ---------------------------------------------------------
    # 2. Get the restaurant interactions of those users.
    # ---------------------------------------------------------

    top_user_ids = similar_users["user_id"].tolist()

    candidate_scores = user_item_matrix.loc[
        top_user_ids
    ]

    # ---------------------------------------------------------
    # 3. Weight each user's behavior by how similar
    #    they are to the target user.
    # ---------------------------------------------------------

    similarity_weights = (
        similar_users
        .set_index("user_id")["similarity"]
    )

    weighted_scores = candidate_scores.mul(
        similarity_weights,
        axis=0,
    )

    # Add scores from all similar users.
    restaurant_scores = weighted_scores.sum(
        axis=0
    )

    # ---------------------------------------------------------
    # 4. Remove restaurants the target user has
    #    already interacted with.
    # ---------------------------------------------------------

    user_history = user_item_matrix.loc[user_id]

    user_history = user_history[
        user_history > 0
    ]

    restaurant_scores = restaurant_scores.drop(
        user_history.index,
        errors="ignore",
    )

    # ---------------------------------------------------------
    # 5. Sort restaurants by recommendation score.
    # ---------------------------------------------------------

    restaurant_scores = restaurant_scores.sort_values(
        ascending=False,
    )

    # Return the top K recommendations.
    return restaurant_scores.head(top_k)


def main():

    print("Similar users to U001:")
    print()

    _, user_item_matrix = load_data()

    similar_users = get_similar_users(
        "U001",
        user_item_matrix,
        top_k=10,
    )

    print(
        similar_users.to_string(index=False)
    )

    print("\nCollaborative recommendations for U001:")
    print()

    recommendations = recommend_for_user(
        "U001",
        top_k=10,
    )

    print(
        recommendations.to_string()
    )


if __name__ == "__main__":
    main()