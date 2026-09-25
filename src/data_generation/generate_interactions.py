"""Generate synthetic user-restaurant interactions.

How this works
--------------
Users and restaurants are loaded from CSV. We do NOT add new columns to
users.csv.

For each user, the script first builds *hidden* cuisine preferences in
memory only. These are 1-3 favourite cuisines, sampled so that different
users like different things. They are used to score restaurants, then
discarded. They never appear in interactions.csv or users.csv.

A restaurant is more likely to be chosen when:
- its cuisine is one of the user's hidden favourites
- its price is close to the user's preferred_price_range
- it is in the same city (Klang Valley cities get a small nearby bonus)
- it has a higher rating and more reviews

Most pairs start as a view. Better-matching restaurants are more likely
to continue down the funnel: click -> like/save -> visit -> rating.
Events for the same pair are ordered in time.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)

MIN_RESTAURANTS_PER_USER = 8
MAX_RESTAURANTS_PER_USER = 16

PRICE_LEVEL = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

# Nearby cities that people in the Klang Valley might still visit.
KLANG_VALLEY = {"Kuala Lumpur", "Petaling Jaya", "Shah Alam"}

START_TIME = datetime(2025, 10, 1)
END_TIME = datetime(2026, 9, 20)


def project_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")
    return data_dir


def make_hidden_preferences(cuisines):
    """Pick 1-3 favourite cuisines for one user. Kept in memory only."""
    n_favourites = random.randint(1, 3)
    return random.sample(cuisines, n_favourites)


def restaurant_score(user, restaurant, favourite_cuisines):
    """Higher score = more likely this user notices this restaurant."""
    score = 0.4

    if restaurant["cuisine"] in favourite_cuisines:
        score += 5.0

    price_gap = abs(
        PRICE_LEVEL[restaurant["price_range"]]
        - PRICE_LEVEL[user["preferred_price_range"]]
    )
    score += max(0.0, 2.0 - price_gap)

    if restaurant["city"] == user["city"]:
        score += 3.0
    elif user["city"] in KLANG_VALLEY and restaurant["city"] in KLANG_VALLEY:
        score += 0.8

    score += (restaurant["rating"] - 3.0) * 0.9
    score += min(restaurant["review_count"], 600) / 500.0

    return max(score, 0.05)


def pick_weighted_restaurants(restaurants, scores, n_picks):
    """Choose restaurants without replacement, using the scores as weights."""
    pool = list(range(len(restaurants)))
    weights = list(scores)
    chosen = []

    n_picks = min(n_picks, len(pool))
    for _ in range(n_picks):
        idx = random.choices(pool, weights=weights, k=1)[0]
        chosen.append(restaurants[idx])
        position = pool.index(idx)
        pool.pop(position)
        weights.pop(position)

    return chosen


def random_timestamp():
    seconds_range = int((END_TIME - START_TIME).total_seconds())
    return START_TIME + timedelta(seconds=random.randint(0, seconds_range))


def events_for_match(score):
    """Better matches are more likely to move past a simple view."""
    events = ["view"]

    p_click = min(0.90, 0.18 + score / 12.0)
    if random.random() > p_click:
        return events
    events.append("click")

    p_like = min(0.55, 0.08 + score / 18.0)
    if random.random() < p_like:
        events.append("like")

    p_save = min(0.40, 0.05 + score / 22.0)
    if random.random() < p_save:
        events.append("save")

    p_visit = min(0.45, 0.04 + score / 20.0)
    if random.random() > p_visit:
        return events
    events.append("visit")

    p_rating = min(0.70, 0.20 + score / 16.0)
    if random.random() < p_rating:
        events.append("rating")

    return events


def generate_interactions(users_df, restaurants_df):
    restaurants = restaurants_df.to_dict("records")
    cuisines = sorted(restaurants_df["cuisine"].unique())

    rows = []
    interaction_number = 1

    for user in users_df.to_dict("records"):
        favourites = make_hidden_preferences(cuisines)
        scores = [
            restaurant_score(user, restaurant, favourites)
            for restaurant in restaurants
        ]

        n_restaurants = random.randint(
            MIN_RESTAURANTS_PER_USER, MAX_RESTAURANTS_PER_USER
        )
        chosen = pick_weighted_restaurants(restaurants, scores, n_restaurants)

        for restaurant in chosen:
            match_score = restaurant_score(user, restaurant, favourites)
            event_types = events_for_match(match_score)

            event_time = random_timestamp()
            for event_type in event_types:
                rows.append(
                    {
                        "interaction_id": f"I{interaction_number:05d}",
                        "user_id": user["user_id"],
                        "restaurant_id": restaurant["restaurant_id"],
                        "event_type": event_type,
                        "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                interaction_number += 1
                # Later funnel events happen a little after the previous one.
                event_time = event_time + timedelta(minutes=random.randint(2, 180))

    return pd.DataFrame(rows)


def main():
    data_dir = project_paths()
    os.makedirs(data_dir, exist_ok=True)

    users_df = pd.read_csv(os.path.join(data_dir, "users.csv"))
    restaurants_df = pd.read_csv(os.path.join(data_dir, "restaurants.csv"))

    df = generate_interactions(users_df, restaurants_df)

    output_path = os.path.join(data_dir, "interactions.csv")
    df.to_csv(output_path, index=False)

    print(df.head().to_string(index=False))
    print(f"\nDataset shape: {df.shape}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
