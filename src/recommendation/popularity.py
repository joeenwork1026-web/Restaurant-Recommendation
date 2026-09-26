"""Popularity-based restaurant recommender."""

import os

import pandas as pd


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


def load_popularity_table(
    interactions=None,
):
    """
    Create a popularity table for restaurants.

    Popularity is measured by the number of
    unique users who interacted with a restaurant.
    """

    data_dir = project_paths()

    # Load restaurant information.
    restaurants = pd.read_csv(
        os.path.join(
            data_dir,
            "restaurants.csv",
        )
    )

    # Load interactions.
    if interactions is None:

        interactions = pd.read_csv(
            os.path.join(
                data_dir,
                "interactions.csv",
            )
        )

    else:
        interactions = interactions.copy()

    # Count unique users for each restaurant.
    popularity = (
        interactions
        .groupby("restaurant_id")["user_id"]
        .nunique()
        .reset_index(
            name="popularity"
        )
    )

    # Add popularity information to the
    # restaurant dataset.
    ranked = restaurants.merge(
        popularity,
        on="restaurant_id",
        how="left",
    )

    # Restaurants with no interactions get
    # a popularity score of 0.
    ranked["popularity"] = (
        ranked["popularity"]
        .fillna(0)
        .astype(int)
    )

    # First sort by popularity.
    #
    # If two restaurants have the same popularity,
    # use rating as the tie-breaker.
    ranked = ranked.sort_values(
        by=[
            "popularity",
            "rating",
        ],
        ascending=[
            False,
            False,
        ],
    )

    return ranked.reset_index(
        drop=True
    )


def get_popular_restaurants(
    top_k=10,
    interactions=None,
):
    """
    Return the most popular restaurants.
    """

    ranked = load_popularity_table(
        interactions=interactions
    )

    return ranked.head(
        top_k
    )


def get_popularity_scores(
    interactions=None,
):
    """
    Return popularity scores indexed by
    restaurant_id.

    This is useful for the hybrid recommender.
    """

    popularity_table = load_popularity_table(
        interactions=interactions
    )

    return (
        popularity_table
        .set_index("restaurant_id")[
            "popularity"
        ]
    )


def main():
    """Run a simple popularity recommendation."""

    top_10 = get_popular_restaurants(
        top_k=10
    )

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "rating",
        "popularity",
    ]

    print(
        top_10[
            columns
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()