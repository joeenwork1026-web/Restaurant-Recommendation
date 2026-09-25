"""Popularity-based restaurant recommendations.

Approach
--------
This recommender does not learn user taste. It only asks: "How many
different people interacted with this restaurant?"

A restaurant that 40 unique users viewed/clicked/liked is treated as more
popular than one that 5 unique users touched, even if those 5 users left
many events. Using unique users avoids counting the same person twice.

Pandas steps
------------
1. read_csv          load restaurants and interactions
2. groupby + nunique count distinct user_id values per restaurant_id
3. merge             attach that count onto the restaurant table
4. fillna            restaurants with no interactions get popularity 0
5. sort_values       highest popularity first; rating breaks ties
6. head              keep only the top K rows
"""

import os

import pandas as pd


def project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")
    return data_dir


def load_popularity_table():
    data_dir = project_paths()
    restaurants = pd.read_csv(os.path.join(data_dir, "restaurants.csv"))
    interactions = pd.read_csv(os.path.join(data_dir, "interactions.csv"))

    # One row per restaurant: how many unique users interacted with it.
    popularity = (
        interactions.groupby("restaurant_id")["user_id"]
        .nunique()
        .reset_index(name="popularity")
    )

    # Keep restaurant details and add the popularity column.
    ranked = restaurants.merge(popularity, on="restaurant_id", how="left")
    ranked["popularity"] = ranked["popularity"].fillna(0).astype(int)

    ranked = ranked.sort_values(
        by=["popularity", "rating"],
        ascending=[False, False],
    )
    return ranked.reset_index(drop=True)


def get_popular_restaurants(top_k=10):
    """Return the top K restaurants by unique-user popularity."""
    ranked = load_popularity_table()
    return ranked.head(top_k)


def main():
    top_10 = get_popular_restaurants(top_k=10)
    columns = ["restaurant_id", "name", "cuisine", "rating", "popularity"]
    print(top_10[columns].to_string(index=False))


if __name__ == "__main__":
    main()
