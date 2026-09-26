"""Filter restaurants using structured user preferences."""

import os

import pandas as pd


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


def filter_restaurants(restaurants, preferences):
    filtered = restaurants.copy()

    cuisine = preferences.get("cuisine")
    city = preferences.get("city")
    price_range = preferences.get("price_range")
    minimum_rating = preferences.get("minimum_rating")

    if cuisine:
        filtered = filtered[
            filtered["cuisine"].str.contains(
                cuisine,
                case=False,
                na=False,
            )
        ]

    if city:
        filtered = filtered[
            filtered["city"].str.contains(
                city,
                case=False,
                na=False,
            )
        ]

    if price_range:
        filtered = filtered[
            filtered["price_range"] == price_range
        ]

    if minimum_rating is not None:
        filtered = filtered[
            filtered["rating"] >= minimum_rating
        ]

    return filtered.reset_index(drop=True)


def main():
    restaurants = load_restaurants()

    preferences = {
        "cuisine": "Japanese",
        "city": "Kuala Lumpur",
        "price_range": "$",
        "minimum_rating": None,
    }

    results = filter_restaurants(
        restaurants,
        preferences,
    )

    columns = [
        "restaurant_id",
        "name",
        "cuisine",
        "price_range",
        "rating",
        "city",
    ]

    print(results[columns].to_string(index=False))


if __name__ == "__main__":
    main()