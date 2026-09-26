"""User-based collaborative filtering recommender."""

import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# Stronger user actions receive larger weights.
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

    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.abspath(
        os.path.join(
            script_dir,
            "..",
            "..",
        )
    )

    data_dir = os.path.join(
        project_root,
        "data",
    )

    return data_dir


def load_data(interactions=None):
    """
    Load interaction data and create a user-item matrix.

    Rows    = users
    Columns = restaurants
    Values  = weighted interaction strength
    """

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

    # Convert event types into numerical weights.
    interactions["weight"] = (
        interactions["event_type"]
        .map(INTERACTION_WEIGHTS)
        .fillna(1)
    )

    # Create the user-item interaction matrix.
    user_item_matrix = interactions.pivot_table(
        index="user_id",
        columns="restaurant_id",
        values="weight",
        aggfunc="sum",
        fill_value=0,
    )

    return (
        interactions,
        user_item_matrix,
    )


def calculate_user_similarity(
    user_item_matrix,
):
    """
    Calculate cosine similarity between users.

    Each row represents one user's restaurant
    interaction profile.
    """

    similarity_matrix = cosine_similarity(
        user_item_matrix
    )

    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=user_item_matrix.index,
        columns=user_item_matrix.index,
    )

    return similarity_df


def get_similar_users(
    user_id,
    similarity_df,
    similar_user_count=10,
    minimum_similarity=0.0,
):
    """
    Find users most similar to the target user.
    """

    if user_id not in similarity_df.index:
        raise ValueError(
            f"User {user_id} was not found."
        )

    similar_users = (
        similarity_df[user_id]
        .drop(user_id)
        .sort_values(
            ascending=False
        )
    )

    # Remove users whose similarity is too low.
    similar_users = similar_users[
        similar_users >= minimum_similarity
    ]

    # Keep only the strongest similar users.
    similar_users = similar_users.head(
        similar_user_count
    )

    return similar_users


def recommend_for_user(
    user_id,
    top_k=10,
    similar_user_count=10,
    minimum_similarity=0.0,
    interactions=None,
):
    """
    Generate recommendations using user-based
    collaborative filtering.

    Recommendation score:

        similarity × interaction strength

    across similar users.
    """

    (
        interactions,
        user_item_matrix,
    ) = load_data(interactions)

    if user_id not in user_item_matrix.index:
        raise ValueError(
            f"User {user_id} was not found "
            f"in the interaction data."
        )

    # Calculate similarity between all users.
    similarity_df = calculate_user_similarity(
        user_item_matrix
    )

    # Find users with similar restaurant preferences.
    similar_users = get_similar_users(
        user_id=user_id,
        similarity_df=similarity_df,
        similar_user_count=similar_user_count,
        minimum_similarity=minimum_similarity,
    )

    # Store recommendation scores here.
    candidate_scores = {}

    # Look at the restaurants interacted with
    # by each similar user.
    for (
        similar_user,
        similarity_score,
    ) in similar_users.items():

        user_restaurants = user_item_matrix.loc[
            similar_user
        ]

        for (
            restaurant_id,
            interaction_weight,
        ) in user_restaurants.items():

            # Ignore restaurants that the user
            # never interacted with.
            if interaction_weight <= 0:
                continue

            # Similarity determines how much
            # this user's preference matters.
            score = (
                similarity_score
                * interaction_weight
            )

            candidate_scores[
                restaurant_id
            ] = (
                candidate_scores.get(
                    restaurant_id,
                    0.0,
                )
                + score
            )

    # Restaurants already seen by the target user
    # should not be recommended again.
    seen_restaurants = set(
        interactions.loc[
            interactions["user_id"] == user_id,
            "restaurant_id",
        ]
    )

    candidate_scores = {
        restaurant_id: score
        for (
            restaurant_id,
            score,
        ) in candidate_scores.items()
        if restaurant_id not in seen_restaurants
    }

    # Convert recommendation scores into a DataFrame.
    recommendations = pd.DataFrame(
        list(
            candidate_scores.items()
        ),
        columns=[
            "restaurant_id",
            "collaborative_score",
        ],
    )

    # Sort highest score first.
    recommendations = recommendations.sort_values(
        "collaborative_score",
        ascending=False,
    )

    # Add restaurant information.
    data_dir = project_paths()

    restaurants = pd.read_csv(
        os.path.join(
            data_dir,
            "restaurants.csv",
        )
    )

    recommendations = recommendations.merge(
        restaurants,
        on="restaurant_id",
        how="left",
    )

    return recommendations.head(
        top_k
    ).reset_index(drop=True)


def main():
    """Run a simple collaborative filtering example."""

    recommendations = recommend_for_user(
        user_id="U001",
        top_k=10,
        similar_user_count=10,
        minimum_similarity=0.0,
    )

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "price_range",
        "rating",
        "collaborative_score",
    ]

    print(
        recommendations[
            columns
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()